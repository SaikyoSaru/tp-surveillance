import time
import numpy as np
from motion_detection.single_motion_detection import singleMotionDetector
from flask import Response, render_template, Flask, redirect, url_for, request, flash
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app.models import User
from app.forms import LoginForm, RegistrationForm
from app import db


from imutils.video import VideoStream
import threading
import argparse
import imutils
import cv2
import time
import datetime 
import redis

from app import app
# outputFrame = None
# lock = threading.Lock()


# vs = VideoStream().start()
# time.sleep(2.0)
# cache = redis.Redis(host='redis', port=6379)



@app.route('/', methods=['Get', 'POST'])
@app.route('/index', methods=['Get', 'POST'])
@login_required
def index():
    if 'logon' in request.form:
        return redirect(url_for('logged_on'))
    return render_template('index.html', title='Home Page')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratz, you are now in the trashpandas squad!, Enjoy your free secure Video suerveillance solutions!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Become one of us!', form=form)
            
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid fusername or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('homepage')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)
        
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)

@app.route('/cameras')
@login_required
def logged_on():
    return render_template('cameras.html')



def detect_motion(frameCount):
    global vs, outputFrame, lock
    md = singleMotionDetector(accumweight=0.1)
    total = 0
    while True:
        frame = vs.read()
        frame = imutils.resize(frame, width=400)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (7, 7), 0)
        
        timestamp = datetime.datetime.now()
        cv2.putText(frame, timestamp.strftime(
			"%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10),
			cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)       
        
        if total > frameCount:
            motion = md.detect(gray)
            if motion:
                (tresh, (minX, minY, maxX, maxY)) = motion
                cv2.rectangle(frame, (minX, minY), (maxX, maxY),
                              (0, 0, 255), 2)
        md.update(gray)
        total+=1
        with lock:
            outputFrame = frame.copy()
            
def generate():
    	# grab global references to the output frame and lock variables
	global outputFrame, lock
	# loop over frames from the output stream
	while True:
		# wait until the lock is acquired
		with lock:
			# check if the output frame is available, otherwise skip
			# the iteration of the loop
			if outputFrame is None:
				continue
			# encode the frame in JPEG format
			(flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
			# ensure the frame was successfully encoded
			if not flag:
				continue
		# yield the output frame in the byte format
		yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
			bytearray(encodedImage) + b'\r\n')
  

@app.route("/video_feed")
def video_feed():
	# return the response generated along with the specific media
	# type (mime type)
	return Response(generate(),
		mimetype = "multipart/x-mixed-replace; boundary=frame")