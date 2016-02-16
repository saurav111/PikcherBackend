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
    company_name = Column(String(64), unique=True)
    user_id_insta= Column(String(64), unique=True)
    first_login = Column(Integer)
    email = Column(String(120),unique=True)

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
    user_link = Column(String(1000), default= 'None')
    created_time = Column(String(64))
    media_id = Column(String(120), unique=True)

#class Tagged_images(db):
#    __tablename__='tagged_images'
#    un_id = Column(Integer, primary_key=True)
#    img_url = Column(String(120), unique=True)
#    img_tag = Column(String(120), unique=True)
#    user_link = Column(String(1000), default= 'None')
#    created_time = Column(String(64))
#    user_id = Column(Integer, ForeignKey('users.un_id'))
#     status = Column(Integer, default=0)


engine = create_engine('sqlite:///app.db')

db.metadata.create_all(engine)