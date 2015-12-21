import os
import time
from instagram.client import InstagramAPI
from flask import Flask, request, render_template, session, redirect, abort, flash, jsonify
from flask_s3 import FlaskS3
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker


app = Flask(__name__)   # create our flask app
app.config.from_object('config')
db = SQLAlchemy(app)

import models

#/////////////////////////////////////////////////s3 details
app.config['FLASKS3_BUCKET_NAME'] = 'mybucketname'
s3 = FlaskS3(app)

app.secret_key = '327e5fca521b4e91818db7e39ec998d3'

#/////////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////////

# configure Instagram API
instaConfig = {
'client_id': '0bfa1f7417f54c79b433437420b338b1',
'client_secret': '28598bc44a444079b95fbe558f5f4527',
'redirect_uri': 'http://localhost:5000/instagram_callback'
}
api = InstagramAPI(**instaConfig)

@app.route('/')
def user_photos():

	# if instagram info is in session variables, then display user photos
	if 'instagram_access_token' in session and 'instagram_user' in session:
		userAPI = InstagramAPI(access_token=session['instagram_access_token'])
		recent_media, next = userAPI.user_recent_media(user_id=session['instagram_user'].get('id'),count=25)
		usernm= recent_media[0].user.username
		pre_user = models.User.query.filter_by(user_name=usernm).first()
		if pre_user is None:
			return redirect('/register')
		else:
			rurl='/'+usernm+'_'+str(pre_user.un_id)
#			for m in recent_media:
#				loc =models.Images(img_url=m.images['low_resolution'].url, user_id=pre_user.un_id)
#				db.session.add(loc)
#				db.session.commit()
			return redirect(rurl)
	else:
		return redirect('/connect')

### All the Users
@app.route('/arun542_1', methods=['GET', 'POST'])
def page_visit():
		userAPI = InstagramAPI(access_token=session['instagram_access_token'])
		recent_media = models.Images.query.filter_by(user_id=1).all()
		templateData = {
		'media' : recent_media
		}
		if request.method == 'POST':
			for rm in recent_media:
				strr="url"+str(rm.un_id)
				new_url= request.form[strr]
				if new_url is not None:
					rm.user_link= new_url
					print rm.user_link
					print rm.img_url
			db.session.commit()
		return render_template('arun542.html', **templateData)

# Redirect users to Instagram for login
@app.route('/connect')
def main():

	try:
		url = api.get_authorize_url(scope=["likes","comments"])
		return '<a href="%s">Connect with Instagram</a>' % url
	except Exception as e:
		print(e)
# Instagram will redirect users back to this route after successfully logging in
@app.route('/instagram_callback')
def instagram_callback():

	code = request.args.get('code')

	if code:

		access_token, user = api.exchange_code_for_access_token(code)
		if not access_token:
			return 'Could not get access token'

			app.logger.debug('got an access token')
			app.logger.debug(access_token)

		# Sessions are used to keep this data 
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