##current value= 15300
import os
import time
from instagram.client import InstagramAPI
from flask import Flask, request, render_template, session, redirect, abort, flash, jsonify, g
from flask_s3 import FlaskS3
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.login import login_user, logout_user, current_user, login_required
from sqlalchemy.orm import sessionmaker
from sqlalchemy import update, engine
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from models import db, User, Images

app = Flask(__name__)   # create our flask app
app.config.from_object('config')
#///////////////////////////////////////////////////////////

engine = create_engine('sqlite:///app.db')
db.metadata.bind =engine

DBsession =sessionmaker(bind=engine)
sessionn= DBsession()

#/////////////////////////////////////////////////s3 details
app.config['FLASKS3_BUCKET_NAME'] = 'mybucketname'
s3 = FlaskS3(app)

app.secret_key = '327e5fca521b4e91818db7e39ec998d3'

#/////////////////////////////////////////////////////////////////////////

lm = LoginManager()
lm.init_app(app)
lm.login_view = '/connect'

#////////////////////////////////////////////////////////////////////////

# configure Instagram API
instaConfig = {
'client_id': '0bfa1f7417f54c79b433437420b338b1',
'client_secret': '28598bc44a444079b95fbe558f5f4527',
'redirect_uri': 'http://localhost:5000/instagram_callback'
}
api = InstagramAPI(**instaConfig)

@lm.user_loader
def load_user(id):
    return sessionn.query(User).get(int(id))

@app.before_request
def before_request():
    g.user = current_user

@app.route('/logout')
def logout():
    logout_user()
    g.user=None
    session.clear()
    return redirect('/connect')

@app.route('/')
def user_photos():
#		print session
	# if instagram info is in session variables, then display user photos
		if 'instagram_access_token' in session and 'instagram_user' in session:
			userAPI = InstagramAPI(access_token=session['instagram_access_token'])
			recent_media, next = userAPI.user_recent_media(user_id=session['instagram_user'].get('id'),count=2)
			usernm= recent_media[0].user.username
			pre_user = sessionn.query(User).filter_by(user_name=usernm).first()
			login_user(pre_user)
			g.user=pre_user
			if pre_user is None:
				return redirect('/register')
			else:
				if pre_user.first_login == 0:
					r_media, next = userAPI.user_recent_media(user_id=session['instagram_user'].get('id'),count=100)
					for m in r_media:
						loc = Images(img_url=m.images['low_resolution'].url, user_id=pre_user.un_id)
						sessionn.add(loc)
					sessionn.commit()
				rurl='/'+usernm+'/'+str(pre_user.un_id)
				return redirect(rurl)
		else:
			return redirect('/connect')

### All the Users
@app.route('/<usernm>/<userid>', methods=['GET', 'POST'])
@login_required
def page_visit(usernm, userid):

		post_user=g.user
#		post_user = sessionn.query(User).filter_by(user_name=usernm).first()
		r_media = sessionn.query(Images).filter_by(user_id=userid).all()
		if post_user.first_login ==0:
			post_user.first_login = 1

		templateData = {
		'media' : r_media
		}
		if request.method == 'POST':
			f = request.form
			for key in f.keys():
			    for value in f.getlist(key):
			    	if value is not None:
						new_url=value
						tab=key
			for rm in r_media:
				strr="url"+str(rm.un_id)
				if strr==""+tab:
					print value
					print tab
					rm.user_link= value			    		
		sessionn.commit()
#		html_add=usernm+'.html'
		return render_template("link_adder.html", post_user=post_user, **templateData)


# Redirect users to Instagram for login
@app.route('/connect')
def main():
	g.link=0
	if g.user is not None and g.user.is_authenticated:
		rurl='/'+g.user.user_name+'/'+str(g.user.un_id)
		print "adfhbsjdfbhsjdfhsjdfhjsd"
		return redirect(rurl)
	else:
		try:
			url = api.get_authorize_url(scope=["likes","comments"])
			return '<a href="%s">Connect with Instagram</a>' % url
		except Exception as e:
			print(e)
# Instagram will redirect users back to this route after successfully logging in
@app.route('/instagram_callback')
def instagram_callback():

	code = request.args.get('code')
	print "asdsadasdasdas"
	if code:

		access_token, user = api.exchange_code_for_access_token(code)
		if not access_token:
			return 'Could not get access token'

			app.logger.debug('got an access token')
			app.logger.debug(access_token)

		# Sessions are used to keep this data 
		if 'fetch_likes' in session:
			session['instagram_access_token_likes'] = access_token
			session['instagram_user_likes'] = user
			urll="/"+session['seller_name']
			return redirect(urll)
		else:
			session['instagram_access_token'] = access_token
			session['instagram_user'] = user

			return redirect('/') # redirect back to main page
		
	else:
		return "Sorry no code provided"



		@app.errorhandler(404)
		def page_not_found(error):
			return render_template('404.html'), 404

#Registering the client
@app.route('/register')
def get_registered():
	return render_template('register.html')

#////////////////////////////////////////////for buyers

@app.route('/connect_for_likes/<usernm>')
def set_and_redirect(usernm):
	re_url = api.get_authorize_url(scope=["public_content"])
	session['fetch_likes'] = 1
	session['seller_name'] = usernm
	return redirect(re_url)

@app.route('/<usernm>', methods=['GET', 'POST'])
def display_user(usernm):
	show_user = sessionn.query(User).filter_by(user_name=usernm).first()
#	print show_user.user_name
	show_media = sessionn.query(Images).filter_by(user_id=show_user.un_id).all()
	liked_media=[]
	my_likes=0
	if request.method == 'POST':
		f=request.form
		print f['bttn']
		if f['bttn']=='Featured':
			my_likes=0
		else:
			my_likes=1
	print my_likes

	if my_likes==1:
		if 'instagram_access_token_likes' in session and 'instagram_user_likes' in session:
#			print session['instagram_access_token_likes']
			userAPI = InstagramAPI(access_token=session['instagram_access_token_likes'])
#			print userAPI
			liked_media, next = userAPI.user_liked_media()
			print liked_media[0].likes[0]
	show_liked=[]
	for obj in show_media:
		print obj.img_url
	for img1 in liked_media:
		for obj in show_media:
#			print obj.img_url
			if img1.likes[0] == obj.img_url:
				show_liked.append(obj)

	return render_template("buy_product.html",usernm=usernm, my_likes=my_likes, show_user=show_user, liked_media=show_liked, show_media=show_media)



# This is a jinja custom filter
@app.template_filter('strftime')
def _jinja2_filter_datetime(date, fmt=None):
    pyDate = time.strptime(date,'%a %b %d %H:%M:%S +0000 %Y') # convert instagram date string into python date/time
    return time.strftime('%Y-%m-%d %h:%M:%S', pyDate) # return the formatted date.
    
# --------- Server On ----------
# start the webserver
if __name__ == "__main__":
	app.debug = True
	
	port = int(os.environ.get('PORT', 5000)) # locally PORT 5000, Heroku will assign its own port
	app.run(host='0.0.0.0', port=port)