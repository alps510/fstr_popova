from fastapi import FastAPI
from crud import add_user, get_items, get_item, get_item_out, put_item, post_item, row_to_str, get_user
from models import SessionLocal, get_db
from models import database

from schemas import Response, Users, Pereval_out_list, Pereval_out, Pereval_out_update
from fastapi.responses import JSONResponse
from typing import List
from fastapi import Depends
from asyncpg.exceptions import UniqueViolationError



app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.post('/', response_model=Response)
async def submit_data(input_json, db: SessionLocal = Depends(get_db)):
    try:
        row_to_str(input_json)
        try:
            pereval_id = await post_item(input_json, db)
            return {"status": 200, "message": "Success!", "pereval_id": pereval_id}
        except UniqueViolationError:
            return {"status": 500, "message": "Server error"}
    except ValueError:
        return {"status": 400, "message": "Invalid data!"}


@app.post('/users/')
async def create_user(user: Users, db: SessionLocal = Depends(get_db)):
    return await add_user(user, db)


@app.get('/users/{user_id}')
async def read_user(user_id: int, db: SessionLocal = Depends(get_db)):
    return await get_user(user_id, db)


@app.get('/{user_id}', response_model=List[Pereval_out_list])
async def read_data(user_id: int, db: SessionLocal = Depends(get_db)):
    return await get_items(user_id, db)


@app.get('/items/{item_id}', response_model=Pereval_out, responses={404: {"model": Response}})
async def read_item(item_id: int, db: SessionLocal = Depends(get_db)):
    try:
        item = await get_item(item_id, db)
    except IndexError:
        return JSONResponse(status_code=404, content={"message": "Item not found"})
    else:
        return await get_item_out(item_id, db)


@app.patch("/{item_id}", response_model=Response)
async def update_item(item_id: int, item: Pereval_out_update, db: SessionLocal = Depends(get_db)):
    try:
        db_item = await get_item(item_id, db)
    except IndexError:
        return {'status': 404, 'message': 'Item not found'}
    else:
        if db_item.status != 'new':
            return {'status': 409, 'message': 'Forbidden. Item already accepted'}
        else:
            await put_item(item_id, item, db)
            return {"status": 200, "message": "Item succesfully updated"}