import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

db = declarative_base()

class User(db):
    __tablename__ = 'users'
    un_id = Column(Integer, primary_key=True)
    access_token = Column(String(120), unique=True)
    user_name = Column(String(64), unique=True)
#   timestamp = Column(DateTime)
    first_login = Column(Integer)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.un_id)  # python 2
        except NameError:
            return str(self.un_id)  # python 3

class Images(db):
    __tablename__='all_images'
    un_id = Column(Integer, primary_key=True)
    img_url = Column(String(120), unique=True)
    user_id = Column(Integer, ForeignKey('users.un_id'))
    user_link = Column(String(120), default= 'None')

engine = create_engine('sqlite:///app.db')

db.metadata.create_all(engine)