from typing import List
import databases
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi import FastAPI
from pydantic import BaseModel


DATABASE_URL = "postgresql+psycopg2://postgres:666666@192.168.56.101:5432/pereval"
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

#class PostIn(BaseModel):
#    title: str
#   text: str
#  is_published: bool


#class Post(BaseModel):
#    id: int
#    title: str
#    text: str
#    is_published: bool

app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
