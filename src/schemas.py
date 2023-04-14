from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class Users(BaseModel):
    email: str
    phone: str
    fam: str
    name: str
    otc: Optional[str]


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


class Pereval_out_update(BaseModel):
    beautyTitle: Optional[str]
    title: Optional[str]
    other_titles: Optional[str]
    connect: Optional[str]
    date: Optional[datetime]
    images: Optional[List[Images]]
    latitude: Optional[float]
    longitude: Optional[float]
    height: Optional[int]
    level_winter: Optional[str]
    level_spring: Optional[str]
    level_summer: Optional[str]
    level_autumn: Optional[str]


class Pereval_out_list(Pereval_out_update):
    beautyTitle: str
    title: str
    other_titles: str
    connect: Optional[str]
    date: datetime
    images: Optional[List[Images]]
    latitude: float
    longitude: float
    height: int
    level_winter: str
    level_spring: str
    level_summer: str
    level_autumn: str
    status: str


class Pereval_out(Pereval_out_list):
    email: str


class Response(BaseModel):
   status: Optional[int]
   message: str
   pereval_id: Optional[int] = None
