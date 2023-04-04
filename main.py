from fastapi.responses import JSONResponse
from typing import List
import databases
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi import FastAPI, Depends
from asyncpg.exceptions import UniqueViolationError
import os
from dotenv import load_dotenv

from models import coords, pereval_added, users, images, pereval_images, metadata
from schemas import Response, Pereval_added, Users, Pereval_out_list, Pereval_out, Pereval_out_update

load_dotenv()


FSTR_DB_HOST = os.getenv('FSTR_DB_HOST')
FSTR_DB_PORT = os.getenv('FSTR_DB_PORT')
FSTR_DB_LOGIN = os.getenv('FSTR_DB_LOGIN')
FSTR_DB_PASS = os.getenv('FSTR_DB_PASS')


DATABASE_URL = 'postgresql+psycopg2://' + FSTR_DB_LOGIN + ':' + FSTR_DB_PASS + '@' + FSTR_DB_HOST + ':' + FSTR_DB_PORT + '/pereval'
database = databases.Database(DATABASE_URL)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

metadata.create_all(engine)


app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.post('/', response_model=Response)
async def submitData(input_json):
    try:
        input_str = Pereval_added.parse_raw(input_json)
        db = SessionLocal()

        try:
            query_coords = coords.insert().values(
                latitude=input_str.coords.latitude,
                longitude=input_str.coords.longitude,
                height=input_str.coords.height)

            last_id_coords = await database.execute(query_coords)

            query_pereval = pereval_added.insert().values(
                date=input_str.add_time,
                beautyTitle=input_str.beauty_title,
                title=input_str.title,
                other_titles=input_str.other_titles,
                connect=input_str.connect,
                user_id=db.query(users).filter(users.c.email == input_str.user.email).scalar(),
                coords_id=last_id_coords,
                level_winter=input_str.level.winter,
                level_spring=input_str.level.spring,
                level_summer=input_str.level.summer,
                level_autumn=input_str.level.autumn,
                status='new')
            last_id = await database.execute(query_pereval)

            if input_str.images:
                for img in input_str:
                    query_images = images.insert().values(
                        data=img.data,
                        title=img.title)

                    last_id_img = await database.execute(query_images)
                    query_pereval_img = pereval_images.insert().values(
                        pereval_added_id=last_id,
                        image_id=last_id_img)
                    last_id_pereval_img = await database.execute(query_pereval_img)

            return {"status": 200, "message": "Success!", "pereval_id": last_id}
        except UniqueViolationError:
            return {"status": 500, "message": "Server error"}
    except ValueError:
        return {"status": 400, "message": "Invalid data!"}


@app.post('/users/')
async def create_user(user: Users):
    query = users.insert().values(
        email=user.email,
        phone=user.phone,
        surname=user.fam,
        name=user.name,
        patronimic=user.otc)

    last_id = await database.execute(query)
    return {'id': last_id}


@app.get('/', response_model=List[Pereval_out_list])
async def read_data(user_id: int, db: SessionLocal = Depends(get_db)):

    data = db.query(pereval_added, coords)\
        .filter(pereval_added.c.coords_id==coords.c.id)\
        .filter(pereval_added.c.user_id==user_id)
    data = data.outerjoin(pereval_images, pereval_images.c.pereval_added_id==pereval_added.c.id)
    data = data.outerjoin(images, images.c.id==pereval_images.c.image_id)

    return data.all()


@app.get('/{item_id}', response_model=Pereval_out, responses={404: {"model": Response}})
async def read_item(item_id: int, db: SessionLocal = Depends(get_db)):
    try:
        data = db.query(pereval_added).filter(pereval_added.c.id==item_id)[0]
    except IndexError:
        return JSONResponse(status_code=404, content={"message": "Item not found"})
    else:
        if data.status != 'accepted':
            return JSONResponse(status_code=404, content={"message": "Item is not checked"})
        else:
            data = db.query(pereval_added, coords, users)\
                .filter(pereval_added.c.id==item_id)\
                .filter(pereval_added.c.coords_id==coords.c.id)\
                .filter(pereval_added.c.user_id==users.c.id)\
                .filter(pereval_added.c.status=='accepted')
            data = data.outerjoin(pereval_images, pereval_images.c.pereval_added_id == pereval_added.c.id)
            data = data.outerjoin(images, images.c.id == pereval_images.c.image_id)

            return data.first()


@app.patch("/{item_id}", response_model=Response)
def update_item(item_id: int, item: Pereval_out_update, db: SessionLocal = Depends(get_db)):
    try:
        db_item = db.query(pereval_added).filter(pereval_added.c.id==item_id)[0]
    except IndexError:
        return {'status': 404, 'message': 'Item not found'}
    else:
        if db_item.status != 'new':
            return {'status': 409, 'message': 'Forbidden. Item already accepted'}
        else:
            item_data = item.dict(exclude_unset=True)

            set_coords = ['latitude', 'longitude', 'height']
            coords_data = {}
            images_data = {}
            for key in set_coords:
                if key in item_data:
                    coords_data[key] = item_data.pop(key)

            if 'images' in item_data:
                images_data['images'] = item_data.pop('images')
            if item_data:
                db.query(pereval_added).filter(pereval_added.c.id == item_id).update(item_data)
            if coords_data:
                db.query(coords).filter(coords.c.id == db_item.coords_id).update(coords_data)
            db.commit()
            data = db.query(pereval_added).filter(pereval_added.c.id == item_id)[0]
            return {"status": 200, "message": "Item succesfully updated"}