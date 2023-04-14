from models import users, database, pereval_added, coords, pereval_images, images, SessionLocal
from schemas import Users, Pereval_out_update, Pereval_added


async def add_user(user: Users, db: SessionLocal):
    query = users.insert().values(
        email=user.email,
        phone=user.phone,
        surname=user.fam,
        name=user.name,
        patronimic=user.otc)
    last_id = await database.execute(query)
    return last_id


async def get_user(user_id: int, db: SessionLocal):
    data = db.query(users).filter(users.c.id == user_id)
    return data[0]


async def get_items(user_id: int, db: SessionLocal):
    data = db.query(pereval_added, coords)\
        .filter(pereval_added.c.coords_id==coords.c.id)\
        .filter(pereval_added.c.user_id==user_id)
    data = data.outerjoin(pereval_images, pereval_images.c.pereval_added_id==pereval_added.c.id)
    data = data.outerjoin(images, images.c.id==pereval_images.c.image_id)
    return data.all()


async def get_item(item_id: int, db: SessionLocal):
    data = db.query(pereval_added).filter(pereval_added.c.id == item_id)
    return data[0]


async def get_item_out(item_id: int, db: SessionLocal):
    data = db.query(pereval_added, coords, users)\
        .filter(pereval_added.c.id==item_id)\
        .filter(pereval_added.c.coords_id==coords.c.id)\
        .filter(pereval_added.c.user_id==users.c.id)
    data = data.outerjoin(pereval_images, pereval_images.c.pereval_added_id == pereval_added.c.id)
    data = data.outerjoin(images, images.c.id == pereval_images.c.image_id)
    return data[0]


async def put_item(item_id: int, item: Pereval_out_update, db: SessionLocal):
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
        db_pereval = await get_item(item_id, db)
        db.query(coords).filter(coords.c.id == db_pereval.coords_id).update(coords_data)
    db.commit()
    data = db.query(pereval_added).filter(pereval_added.c.id == item_id)[0]
    return data


def row_to_str(input_json):
    return Pereval_added.parse_raw(input_json)


async def post_item(input_json, db: SessionLocal):
    input_str = row_to_str(input_json)
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
    return last_id
