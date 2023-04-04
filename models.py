import sqlalchemy

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