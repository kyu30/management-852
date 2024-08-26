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

load_dotenv()
logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
whitelist = 'whitelist.csv'
overview = 'overview.csv'
'''df = pd.read_csv(whitelist, index_col = 'UID')    
df2 = pd.read_csv(overview)'''

class User(UserMixin, db.Model):
    id =  db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Whitelist(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    uid = db.Column(db.String(50), unique = True, nullable = False)
    name = db.Column(db.String(100))
    access = db.Column(db.String(20))
    host = db.Column(db.String(50))
    last_used = db.Column(db.DateTime, default = dt.now)

class History(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    uid = db.Column(db.String(50), nullable = False)
    name = db.Column(db.String(100))
    access = db.Column(db.String(20))
    host = db.Column(db.String(50))
    last_used = db.Column(db.DateTime, default = dt.now)
    door = db.Column(db.String(50))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/', methods=['GET', 'POST'])
def home():
    login_form = LoginForm()
    register_form = RegisterForm()

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

    if register_form.submit.data and register_form.validate_on_submit():
        user = User.query.filter_by(username = register_form.username.data).first()
        if user:
            flash('Username already exists', 'error')
        else:
            hashed_password = generate_password_hash(register_form.password.data)
            new_user = User(username=register_form.username.data, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('home'))

    return render_template('home.html', login_form=login_form, register_form=register_form)

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
            'last_used': entry.last_used.strftime('%Y-%m-%d %H:%M:%S')

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

@app.route('/add_entry', methods = ["POST"])
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

    '''try:
        data = request.json
        logging.debug(f"Received data for add_entry: {data}")
        if not data:
            logging.debug(f"Received data for add_entry: {data}")
        uid = data.get("uid", '').strip().upper()
        name = data.get("name", '').strip()
        access = data.get("permissions", '').strip()
        host = data.get("host", 'host').strip()
        time = dt.now()
        if not uid or not name or not access or not time or not host:
                logging.error(f"Invalid data received: {data}")
                return jsonify({'status': 'error', 'message': 'Invalid data received'}), 400
        else:
            df.loc[uid] = [access, name, host, time]
            print(df)
            df.to_csv(whitelist)
            logging.debug(f"Added entry: {uid}, {name}, {access},{host},{time}")
            return jsonify({'status': 'success'})
    except Exception as e:
        logging.error(f"Error adding entry: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500'''
    

@app.route('/delete_entry', methods=['POST'])
def delete_entry():
    data = request.json
    userid = data.get('uid', '').strip().upper()
    entry = Whitelist.query.filter_by(uid=userid).first()
    if entry:
        db.session.delete(entry)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Entry Deleted'})
    else:
        return jsonify({'status': 'error', 'message': 'Entry not found'})

    '''if uid in df.index:
        df.drop(uid, inplace = True)
        df.to_csv(whitelist)
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error'}), 400'''


@app.route('/access_check', methods=['GET'])
def access_check():
    rfid = request.args.get('rfid').upper()
    door = request.args.get('scanner_id')
    entry = Whitelist.query.filter_by(uid = rfid).first()
    
    print(f"RFID received: {rfid}, door: {door}")
    if entry:
        in_df = True
        #user_info = df.loc[rfid]
        #last_used = pd.to_datetime(df.loc[rfid, 'LastUsed'])
        #permission = df.loc[rfid, 'Permission']

        if (dt.now() - entry.last_used).days > 30 and entry.permission != 'Owner':
            time = False
        else:
            '''df.loc[rfid, 'LastUsed'] = dt.now()
            df.to_csv(whitelist)  # Save the updated last used time'''
            print(f"User Info: {entry.name}\nCard recognized, access granted")
            time = True
            entry2 = History(
                uid = entry.uid,
                name = entry.name,
                access = entry.access,
                host = entry.host,
                last_used = dt.now(),
                door = door
            )
            entry.last_used = dt.now()
            '''df2.loc[len(df2.index)] = [rfid,df.loc[rfid, 'User'], df.loc[rfid, 'Permission'], door, df.loc[rfid, 'Host'], dt.now()]
            df2.to_csv('overview.csv')'''
            db.session.add(entry2)
            db.session.commit()
    else:
        in_df = False
        print("Card not recognized")

    if in_df and time:
        print("Access Granted")
        response = "granted"
    else:
        print("Access Denied")
        response = "denied"
    
    return response

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    with app.app_context():
        db.create_all()
    app.run(host='192.168.0.110', port=5000) #use wifi ip for local testing
    #app.run(host="0.0.0.0", port=port)