from app import db

class User(db.Model):
	__tablename__ = 'users'
	un_id = db.Column(db.Integer, primary_key=True)
	access_token = db.Column(db.String(120), unique=True)
	user_name = db.Column(db.String(64), unique=True)
	timestamp = db.Column(db.DateTime)
	first_login = db.Column(db.Integer, default= 0)

class Images(db.Model):
	un_id = db.Column(db.Integer, primary_key=True)
	img_url = db.Column(db.String(120), unique=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.un_id'))
	user_link = db.Column(db.String(120), default= 'None', unique=True)
