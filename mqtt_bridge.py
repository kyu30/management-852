import paho.mqtt.client as mqtt
import requests
from datetime import datetime
import sqlite3

HEROKU_ENDPOINT = "https://management-852-40069d69dc54.herokuapp.com/scan"
BROKER_IP = "192.168.0.101"
TOPIC_PREFIX = "rfid/"

def setup_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(whitelist);")
    columns = cursor.fetchall()
    print("Whitelist table columns:", columns)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS whitelist (
            id INTEGER PRIMARY KEY,
            uid TEXT,
            name TEXT,
            access TEXT,
            host TEXT,
            last_used DATETIME DEFAULT CURRENT_TIMESTAMP,
            door TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uid TEXT,
            name TEXT,
            access TEXT,
            host TEXT,
            last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            door TEXT
        )
    """)
    conn.commit()
    conn.close()

def log_uid(uid, door):
    global client
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT name, access, host FROM whitelist WHERE uid = ?", (uid,))
    user = cursor.fetchone()

    if user:
        name, access, host = user
    else:
        name, access, host = "Unknown", "None", "Unknown"

    cursor.execute("""
        INSERT INTO history (uid, name, access, host, door)
        VALUES (?, ?, ?, ?, ?)
    """, (uid, name, access, host, door))
    conn.commit()
    conn.close()

    print(f"Logged UID: {uid} - {name} ({access}) via {door}")

    # Determine access response
    response_msg = "ACCESS GRANTED" if access in ("Owner", "Guest") else "ACCESS DENIED"
    client.publish(f"{TOPIC_PREFIX}{door}/response", response_msg)

    # Sync to Heroku
    try:
        r = requests.post(HEROKU_ENDPOINT, json={
            "uid": uid,
            "name": name,
            "access": access,
            "host": host,
            "timestamp": datetime.now().isoformat(),
            "door": door
        })
        print("Synced to Heroku:", r.status_code, r.text)
    except Exception as e:
        print("Heroku sync failed:", e)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
        client.subscribe(f"{TOPIC_PREFIX}#")  # Subscribe to all rfid/<door>
    else:
        print("Failed to connect. RC =", rc)

def on_message(client, userdata, msg):
    uid = msg.payload.decode().strip()
    topic_parts = msg.topic.split('/')
    door_name = topic_parts[1] if len(topic_parts) > 1 else "Unknown"

    log_uid(uid, door_name)
    print(f"UID received from {door_name}: {uid}")

if __name__ == "__main__":
    setup_db()
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
