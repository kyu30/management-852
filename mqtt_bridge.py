import paho.mqtt.client as mqtt
import requests
from flask import Flask
from datetime import datetime
import sqlite3
import os
from datetime import datetime as dt
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL").replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
HEROKU_ENDPOINT = "https://management-852-40069d69dc54.herokuapp.com/scan"
BROKER_IP = "192.168.0.106"
TOPIC_PREFIX = "rfid/"

class User(db.Model): #manager login database
    __tablename__ = 'user'
    id =  db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(512), unique=True, nullable=False)
    password = db.Column(db.String(512), nullable=False)

class Whitelist(db.Model): #whitelist database (stores name, card id, access level, host, last use)
    __tablename__ = 'whitelist'
    id = db.Column(db.Integer, primary_key = True)
    uid = db.Column(db.String(50), unique = True, nullable = False)
    name = db.Column(db.String(100))
    access = db.Column(db.String(20))
    host = db.Column(db.String(50))
    last_used = db.Column(db.DateTime, default = dt.now)
    image = db.Column(db.String(100))

class History(db.Model): #access history database (whitelist info + when it was used, which door was used)
    __tablename__ = 'history'
    id = db.Column(db.Integer, primary_key = True)
    uid = db.Column(db.String(50), nullable = False)
    name = db.Column(db.String(100))
    access = db.Column(db.String(20))
    host = db.Column(db.String(50))
    last_used = db.Column(db.DateTime, default = dt.now)
    door = db.Column(db.String(50))

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker." if rc == 0 else f"MQTT connection failed: {rc}")

    client.subscribe("access/scan")
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
        client.subscribe(f"{TOPIC_PREFIX}#")  # Subscribe to all rfid/<door>
    else:
        print("Failed to connect. RC =", rc)


def on_message(client, userdata, msg):
    try:
        uid = msg.payload.decode().strip()
        udoor = uid.split('-')[0]
        id = uid.split('-')[1].strip()
        print(f"Received UID: {id} at door {udoor} at time: {datetime.now()}")

        with app.app_context():
            entry = Whitelist.query.filter_by(uid=id).first()
            if entry.access == 'OWNER' or entry.access == 'STAFF' or udoor == 'Guest':
                client.publish(f"rfid/{udoor}/result", "granted" if entry else "denied")
            #access = "granted" if entry else "denied"
                name = entry.name if entry else "Unknown"
                print(name)
                log = History(
                    uid=id,
                    name=name,
                    access=entry.access,
                    door = udoor,
                    host=entry.host,
                    last_used=datetime.now(),
                )
                db.session.add(log)
                db.session.commit()

                print(f"Access granted for {name} (UID: {uid})")
            else:
                print(f"Access denied at door {udoor} for {name} (UID: {id})")
    except Exception as e:
        print(f"Error handling message: {e}")

if __name__ == "__main__":
    global client
    client = mqtt.Client(protocol=mqtt.MQTTv311)
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(BROKER_IP, 1883, 60)
        print("Starting MQTT loop...")
        client.loop_forever()
    except Exception as e:
        print("Error connecting to MQTT broker:", e)
