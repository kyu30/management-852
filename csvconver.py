import sqlite3
import csv

conn = sqlite3.connect('instance/users.db')
cursor = conn.cursor()

cursor.execute("SELECT * FROM user")  # or whatever your table is called
rows = cursor.fetchall()

with open('users.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([desc[0] for desc in cursor.description])  # write headers
    writer.writerows(rows)

conn.close()
