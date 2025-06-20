from flask import Flask, request, jsonify, render_template, url_for, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, RegisterForm
from dotenv import load_dotenv
from datetime import datetime as dt
from datetime import time, date, timedelta
import pandas as pd
import secrets
import logging
import os
import sqlite3
import serial 


load_dotenv()
logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

whitelist = 'whitelist.csv'
overview = 'overview.csv'
'''df = pd.read_csv(whitelist, index_col = 'UID')    
df2 = pd.read_csv(overview)'''


class User(UserMixin, db.Model): #manager login database
    __tablename__ = 'user'
    id =  db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Whitelist(db.Model): #whitelist database (stores name, card id, access level, host, last use)
    id = db.Column(db.Integer, primary_key = True)
    uid = db.Column(db.String(50), unique = True, nullable = False)
    name = db.Column(db.String(100))
    access = db.Column(db.String(20))
    host = db.Column(db.String(50))
    last_used = db.Column(db.DateTime, default = dt.now)
    image = db.Column(db.String(100))

class History(db.Model): #access history database (whitelist info + when it was used, which door was used)
    id = db.Column(db.Integer, primary_key = True)
    uid = db.Column(db.String(50), nullable = False)
    name = db.Column(db.String(100))
    access = db.Column(db.String(20))
    host = db.Column(db.String(50))
    last_used = db.Column(db.DateTime, default = dt.now)
    door = db.Column(db.String(50))

with app.app_context():
    db.create_all

@login_manager.user_loader #login to user dashboard
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/', methods=['GET', 'POST']) #login form
def home():
    login_form = LoginForm()

    if login_form.submit.data and login_form.validate_on_submit():
        user = User.query.filter_by(username=login_form.username.data).first()
        if user and check_password_hash(user.password, login_form.password.data):
            login_user(user, remember=login_form.remember.data)
            user.last_login = dt.now()
            db.session.commit()
            session['username'] = user.username
            session['last_login'] = user.last_login
            return redirect(url_for('dashboard'))
        flash('Invalid username or password')


    return render_template('home.html', login_form=login_form)

# This section just loads the pages 
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('overview.html', name=current_user.username)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/overview')
@login_required
def overview():
    return render_template("overview.html")

@app.route('/manager')
@login_required
def manager():
    return render_template("manager.html")

@app.route('/rooms')
@login_required
def rooms():
    return render_template("rooms.html")

@app.route('/users')
@login_required
def users():
    return render_template("users.html")

#This section just loads the tables
@app.route('/get_whitelist', methods = ['GET']) 
def get_whitelist():
    whitelist = Whitelist.query.all()
    data = []
    for entry in whitelist:
        data.append({
            'uid': entry.uid,
            'name': entry.name,
            'access': entry.access,
            'host': entry.host,
            'last_used': entry.last_used.strftime('%Y-%m-%d %H:%M:%S'),
            'image': entry.image

        })
    return jsonify(data)
    

@app.route('/get_overview', methods = ['GET'])
def get_overview():
    history = History.query.all()
    data = []
    for entry in history:
        data.append({
            'uid': entry.uid,
            'name': entry.name,
            'access': entry.access,
            'host': entry.host,
            'last_used': entry.last_used.strftime('%Y-%m-%d %H:%M:%S'),
            'door': entry.door

        })
    return jsonify(data)

@app.route('/add_entry', methods = ["POST"]) #Lets a host add a user into the table
def add_entry():
    data = request.json
    new = Whitelist(
        uid = data['uid'].strip().upper(),
        name = data['name'].strip().upper(),
        access=data['permissions'].strip().upper(),
        host = data['host'].strip(),
        last_used = dt.now()
    )
    db.session.add(new)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Entry added'})

@app.route('/delete_entry', methods=['POST']) #Lets a host delete a user
def delete_entry():
    data = request.get_json()
    userid = data.get('uid').strip().upper()
    entry = Whitelist.query.filter_by(uid=userid).first()
    if entry:
        db.session.delete(entry)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Entry Deleted'})
    else:
        return jsonify({'status': 'error', 'message': 'Entry not found'})


@app.route('/access_check', methods=['GET'])  #RFID checking logic, NEED TO ADD DOOR PERMISSION LOGIc
def access_check():
    rfid = request.args.get('rfid').upper() #pulls RFID info
    door = request.args.get('scanner_id') #identifies which door is being used
    entry = Whitelist.query.filter_by(uid=rfid).first()
    if entry:
        if (dt.now() - entry.last_used).days <= 30 or entry.access == "Owner":
            return jsonify({"status": "Access Granted"})
        else:
            return jsonify({"status": "Access Denied"})
    else:
        return jsonify({"status": "Card not recognized"})

@app.route("/scan", methods = ["POST"])
def scan():
    data = request.get_json()
    print("UID Received", data)
    return "Received", 200

@app.route('/image_render')
def get_images():
    conn = sqlite3.connect('whitelist.db')
    cursor = conn.cursor()
    cursor.execute("SELECT image_path FROM image")
    rows = cursor.fetchall()
    conn.close()
    image_paths = [row[0] for row in rows]
    return jsonify(image_paths)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    with app.app_context():
        db.create_all()
    #app.run(host='192.168.0.104', port=5000) #use wifi ip for local testing
    app.run(host="0.0.0.0", port=port)