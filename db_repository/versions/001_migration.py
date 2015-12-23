from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
users = Table('users', pre_meta,
    Column('un_id', INTEGER, primary_key=True, nullable=False),
    Column('access_token', VARCHAR(length=120)),
    Column('user_name', VARCHAR(length=64)),
    Column('timestamp', DATETIME),
    Column('count', INTEGER),
)

users = Table('users', post_meta,
    Column('un_id', Integer, primary_key=True, nullable=False),
    Column('access_token', String(length=120)),
    Column('user_name', String(length=64)),
    Column('timestamp', DateTime),
    Column('first_login', Integer, default=ColumnDefault(0)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['users'].columns['count'].drop()
    post_meta.tables['users'].columns['first_login'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['users'].columns['count'].create()
    post_meta.tables['users'].columns['first_login'].drop()
