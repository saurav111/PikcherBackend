import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.sqlalchemy import BaseQuery
from sqlalchemy.orm import sessionmaker
from sqlalchemy import update, engine
from models import db, User, Images
import datetime
import models

db = declarative_base()

engine = create_engine('sqlite:///app.db')

db.metadata.create_all(engine)

DBsession =sessionmaker(bind=engine)
sessionn= DBsession()

user_name=input('Enter instagram user_name: ')

user_by_by=sessionn.query(User).filter_by(user_name=user_name).first()

user_id = user_by_by.un_id

all_user_images= sessionn.query(Images).filter_by(user_id=user_id).all()

for a in all_user_images:
	sessionn.delete(a)

sessionn.delete(user_by_by)

sessionn.commit()