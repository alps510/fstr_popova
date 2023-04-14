# fstr_popova
This FastAPI is intended to serve a mobile application for tourists.
Users replenish the base of mountain passes during their trip.

The following features are available:
- Send the data of a new object
- Edit the data that was not verified by moderator
- Get all information about the passes sent before
- Get data of the object by id
- Add a new user

![Image alt](https://github.com/alps510/fstr_popova/raw/refactor/fstr_img.jpg)

Repository contains code for asynchronous api using
the Fast Api framework ,Uvicorn server and Postgres Database
## Preconditions:
Python 3
## Clone the project
git clone https://github.com/alps510/fstr_popova.git
## API documentation (provided by Swagger UI)
http://127.0.0.1:8000/docs
## Run server
uvicorn app.main:app --reload
## Run test
pytest app/test.py
## Requirements
anyio             3.6.2

asyncpg           0.27.0

certifi           2022.12.7

click             8.1.3

colorama          0.4.6

databases         0.7.0

dnspython         2.3.0

email-validator   1.3.1

fastapi           0.95.0

greenlet          2.0.2

h11               0.14.0

httpcore          0.16.3

httptools         0.5.0

httpx             0.23.3

ujson             5.7.0

uvicorn           0.21.1

watchfiles        0.18.1

websockets        10.4

