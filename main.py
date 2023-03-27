from datetime import datetime
from typing import Optional, List
import databases
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi import FastAPI
from pydantic import BaseModel
from asyncpg.exceptions import UniqueViolationError
import os
from dotenv import load_dotenv

load_dotenv()


FSTR_DB_HOST = os.getenv('FSTR_DB_HOST')
FSTR_DB_PORT = os.getenv('FSTR_DB_PORT')
FSTR_DB_LOGIN = os.getenv('FSTR_DB_LOGIN')
FSTR_DB_PASS = os.getenv('FSTR_DB_PASS')


DATABASE_URL = 'postgresql+psycopg2://' + FSTR_DB_LOGIN + ':' + FSTR_DB_PASS + '@' + FSTR_DB_HOST + ':' + FSTR_DB_PORT + '/pereval'
database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()


coords = sqlalchemy.Table(
    'coords',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.INTEGER, primary_key=True),
    sqlalchemy.Column('latitude', sqlalchemy.Float, nullable=False),
    sqlalchemy.Column('longitude', sqlalchemy.Float, nullable=False),
    sqlalchemy.Column('height', sqlalchemy.Integer, nullable=False),
)

images = sqlalchemy.Table(
    'images',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('title', sqlalchemy.String(20), nullable=False),
    sqlalchemy.Column('image', sqlalchemy.LargeBinary, nullable=False),
)

users = sqlalchemy.Table(
    'users',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('email', sqlalchemy.String(20), nullable=False, unique=True),
    sqlalchemy.Column('phone', sqlalchemy.String(20), unique=True),
    sqlalchemy.Column('surname', sqlalchemy.String(20), nullable=False),
    sqlalchemy.Column('name', sqlalchemy.String(20), nullable=False),
    sqlalchemy.Column('patronimic', sqlalchemy.String(20)),
)

pereval_added = sqlalchemy.Table(
    'pereval_added',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('date', sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column('beautyTitle', sqlalchemy.String(20)),
    sqlalchemy.Column('title', sqlalchemy.String(20), nullable=False),
    sqlalchemy.Column('other_titles', sqlalchemy.String(20)),
    sqlalchemy.Column('connect', sqlalchemy.String(20)),
    sqlalchemy.Column('user_id', sqlalchemy.ForeignKey('users.id'), nullable=False),
    sqlalchemy.Column('coords_id', sqlalchemy.ForeignKey('coords.id'), nullable=False),
    sqlalchemy.Column('level_winter', sqlalchemy.String(2)),
    sqlalchemy.Column('level_spring', sqlalchemy.String(2)),
    sqlalchemy.Column('level_summer', sqlalchemy.String(2)),
    sqlalchemy.Column('level_autumn', sqlalchemy.String(2)),
    sqlalchemy.Column('status', sqlalchemy.String(10), nullable=False),
                      )

pereval_images = sqlalchemy.Table(
    'pereval_images',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('pereval_added_id', sqlalchemy.ForeignKey('pereval_added.id'), nullable=False),
    sqlalchemy.Column('image_id', sqlalchemy.ForeignKey('images.id'), nullable=False),
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

metadata.create_all(engine)


class Users(BaseModel):
    email: str
    fam: str
    name: str
    otc: Optional[str]
    phone: str


class Coords(BaseModel):
    latitude: float
    longitude: float
    height: int


class Levels(BaseModel):
    winter: Optional[str]
    summer: Optional[str]
    autumn: Optional[str]
    spring: Optional[str]


class Images(BaseModel):
    data: Optional[bytes] = None
    title: Optional[str] = None


class Pereval_added(BaseModel):
    beauty_title: str
    title: str
    other_titles: str
    connect: Optional[str]
    add_time: datetime
    user: Users
    coords: Coords
    level: Levels
    images: Optional[List[Images]]


class Response(BaseModel):
   status: int
   message: str
   pereval_id: Optional[int] = None

app = FastAPI()


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



