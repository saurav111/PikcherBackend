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

user_nam=input('Enter instagram user_name: ')

company_nam=input('Enter company name: ')

email_id=input('Enter social media manager email address: ')

new_user=User(user_name=user_nam, company_name=company_nam, first_login=0, email=email_id)

sessionn.add(new_user)

sessionn.commit()
