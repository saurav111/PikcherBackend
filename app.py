##current value= 17100
import os
import time
# from instagram import
from instagram import subscriptions
from instagram.client import InstagramAPI
from flask import Flask, request, render_template, session, redirect, abort, flash, jsonify, g
from flask_s3 import FlaskS3
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.sqlalchemy import BaseQuery
from flask.ext.login import LoginManager
from flask.ext.login import login_user, logout_user, current_user, login_required
from sqlalchemy.orm import sessionmaker
from sqlalchemy import update, engine
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from models import db, User, Images
import datetime
import models
#from apschedular.schedular import Schedular

POSTS_PER_PAGE = 5
POSTS_PER_PAGE_SMM = 5

app = Flask(__name__)   # create our flask app
app.config.from_object('config')

#cron= Schedular(daemon=True)
#cron.start()
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
#api.create_subscription(object='user', aspect='media', callback_url='https://gzrkbyhejx.localtunnel.me/hooking_instagram/')

CLIENT_SECRET = '28598bc44a444079b95fbe558f5f4527'

def process_user_update(update):
#    print 'Received a push:'
    user_id_subs=update['object_id']
    user_subs=sessionn.query(User).filter_by(user_id_insta=user_id_subs).first()
    if user_subs is not None and user_subs.first_login ==1:
        print update
        loc = Images(user_id=user_subs.un_id, media_id=update['data']['media_id'])
        sessionn.add(loc)
        sessionn.commit()

#@cron.interval_schedule(minutes=5)
reactor = subscriptions.SubscriptionsReactor()
reactor.register_callback(subscriptions.SubscriptionType.USER, process_user_update)

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

def paginate(sa_query, page, per_page=2, error_out=True):
    sa_query.__class__ = BaseQuery
    # We can now use BaseQuery methods like .paginate on our SA query
    return sa_query.paginate(page, per_page, error_out)

def photo_id_from_url(url):
    split_by_slash = url.split("/")
    return split_by_slash[-1]


# For companies/////////////////////////////////////////////////////////
# For checking registeration and first time data pull


@app.route('/')
def user_photos():
    if 'instagram_access_token' in session and 'instagram_user' in session:
        userAPI = InstagramAPI(access_token=session['instagram_access_token'])
        recent_media, next = userAPI.user_recent_media(user_id=session['instagram_user'].get('id'),count=1)
        usernm= recent_media[0].user.username
        pre_user = sessionn.query(User).filter_by(user_name=usernm).first()
        pre_user.user_id_insta= recent_media[0].user.id
        sessionn.commit()
        if pre_user is None:
            return redirect('/register')
        else:
            login_user(pre_user)
            g.user=pre_user
            rurl='/'+usernm+'/'+str(pre_user.un_id)
            return redirect(rurl)
    else:
        return redirect('/connect')

### All the companies displaying the content
@app.route('/<usernm>/<userid>', methods=['GET', 'POST'])
@app.route('/<usernm>/<userid>/smm/<int:page>', methods=['GET', 'POST'])
@login_required
def page_visit(usernm, userid,page=1):
    if usernm == g.user.user_name and str(userid) == str(g.user.un_id):
        post_user=g.user
        tab=""
        if request.method == 'POST':
            f = request.form
            for key in f.keys():
                for value in f.getlist(key):
                    if value is not None:
                        new_url=value
                        tab=key


        if post_user.first_login ==0 and tab=="first_import":
            userAPI = InstagramAPI(access_token=session['instagram_access_token'])        
            r_media, next = userAPI.user_recent_media(user_id=session['instagram_user'].get('id'),count=2)  
            if len(r_media)>0:
                for m in r_media:
                    loc = Images(img_url=m.images['low_resolution'].url, user_id=post_user.un_id, created_time=m.created_time, media_id=m.id)
                    sessionn.add(loc)
                    
            while next:
                r_media, next = userAPI.user_recent_media(with_next_url=next,count=2)   
                for m in r_media:
                    loc = Images(img_url=m.images['low_resolution'].url, user_id=post_user.un_id, created_time=m.created_time)
                    sessionn.add(loc)
            post_user.first_login = 1
            sessionn.commit()

        r_media = sessionn.query(Images).filter_by(user_id=userid).all()

        # Update url for images added by subscriptions
        if len(r_media)>0:
            for ind_r_media in r_media:
                if ind_r_media.img_url == None:
                    userAPI = InstagramAPI(access_token=session['instagram_access_token'])
                    media = userAPI.media(ind_r_media.media_id)
                    ind_r_media.img_url = media.images['low_resolution'].url
                    ind_r_media.created_time=media.created_time

        # Update urls
        if len(r_media)>0:
            for rm in r_media:
                strr="url"+str(rm.un_id)
                if strr==""+tab:
                    rm.user_link = value 
                                           
            for rmm in r_media:
                strrr="delete"+str(rmm.un_id)
                if strrr==""+tab:
                    sessionn.delete(rmm)


        print session['instagram_access_token']
        sessionn.commit()

        # r_media = sessionn.query(Images).filter_by(user_id=userid).all()
        media_pagination = sessionn.query(Images).filter_by(user_id=userid).order_by(Images.created_time.desc())
        media_pagination = paginate(media_pagination, page,POSTS_PER_PAGE_SMM,False)

        return render_template("link_adder.html", post_user=post_user, media = media_pagination,user_id=userid,user_name=usernm)
    else:
        return render_template("invalid_login.html")

#Registering the company*
@app.route('/register')
def get_registered():
    return render_template('register.html')

# end companies/////////////////////////////////////////////

# Redirect users to Instagram for login//////////////////////////////
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

@app.route('/hooking_instagram/',methods=['GET', 'POST'])
def hook_instagram():
    if request.method == 'POST':
        # POST event is used to for the events notifications
        print "Aa gaye subscriptions!"
        x_hub_signature = request.headers.get('X-Hub-Signature')
        raw_response = request.data
        try:
            reactor.process(CLIENT_SECRET, raw_response, x_hub_signature)
        except subscriptions.SubscriptionVerifyError:
            print 'Signature mismatch'
        return 'done'
    else:
        print "Challenge tha:"
        hub_challenge =  request.args.get('hub.challenge')
        print hub_challenge
        return '{}'.format(hub_challenge)

@app.errorhandler(404)
def page_not_found(error):
    return redirect('/')

#////////////////////////////////////////////for buyers

@app.route('/connect_for_likes/<usernm>')
def set_and_redirect(usernm):
    re_url = api.get_authorize_url(scope=["public_content"])
    session['fetch_likes'] = 1
    session['seller_name'] = usernm
    return redirect(re_url)

# show_media waala procedure will remain the same
# add mediaID attribute to Images waala model and use it to get the correct show_media

@app.route('/<usernm>', methods=['GET', 'POST'])
@app.route('/<usernm>/index/<int:page>', methods=['GET', 'POST'])
def display_user(usernm,page=1):
    show_user = sessionn.query(User).filter_by(user_name=usernm).first()
    if show_user and show_user.first_login==1:
        # show_media = models.Images.query.filter_by(user_id=show_user.un_id).paginate(1,3,False).items
        show_media_pagination = sessionn.query(Images).filter_by(user_id=show_user.un_id).order_by(Images.created_time.desc())
        show_media = sessionn.query(Images).filter_by(user_id=show_user.un_id).all()
        paginated_show_media = paginate(show_media_pagination, page,POSTS_PER_PAGE,False)
        liked_media=[]
        my_likes=0

        # print session['instagram_access_token_likes']
        if request.method == 'POST':
            f=request.form
            if f['bttn']=='Featured':
                my_likes=0
            else:
                my_likes=1

        if my_likes==1:
            if 'instagram_access_token_likes' in session and 'instagram_user_likes' in session:

                userAPI = InstagramAPI(access_token=session['instagram_access_token_likes'])
                liked_media, next = userAPI.user_liked_media()

        show_liked=[]
        # if img1 in liked_media:
        if len(liked_media)>0 and len(show_media)>0:
            for img1 in liked_media:
                for obj in show_media:
                    # print "Liked images ke URL"
                    # print photo_id_from_url(img1.likes[0]) #img1.likes[0]
                    # print "show_media ke URL"
                    # print photo_id_from_url(obj.img_url) #obj.img_url
                    liked_photo = photo_id_from_url(img1.likes[0])
                    all_photo = photo_id_from_url(obj.img_url)
                    if liked_photo == all_photo:
                        show_liked.append(obj)
        return render_template("buy_product.html",usernm=usernm, my_likes=my_likes, show_user=show_user, liked_media=show_liked, show_media=paginated_show_media)
    else:
        return "Not registered Company"

#/////////////////////////////////////endd buyers

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