#Importing libraries used in the code
import serial
import csv
import pandas as pd
from datetime import datetime as dt
from datetime import time, date, timedelta
import paho.mqtt.client as mqtt

MQTT_SERVER = "localhost"
MQTT_TOPIC_SUB = "test/topic"
MQTT_TOPIC_PUB = "test/response"

data1 = {
    "UID": ["84 B8 C8 72"],
    "User": ["Keith"],
    "Permission": ["Owner"],
    "Door": ["Office"],
    "Time": [dt.now()]
}
#Sets up example csv containing information from one card
data2 = {
    "UID": ["84 B8 C8 72"],
    "Permission": ['Owner'],
    "User": ["Keith"],
    "LastUsed": [dt.now()-timedelta(days=20)] #Used this to test LastUsed range for card
}

def on_connect(client, userdata, flags, rc):
    print(f"connected with result code {rc}")
    client.subscribe(MQTT_TOPIC_SUB)
def on_message(client, userdata, msg):
    print(f"Message received: {msg.payload.decode()}")
    rfid_data = msg.payload.decode()
    print(f"UID: {rfid_data}")
    client_id, uid = rfid_data.split('-')
    if uid in df.index():
        in_df = True #This variable stores whether or not the UID is in the dataframe or not (True/False)
        user_info = df.loc[id] #Stores all the information associated with the UID in the user_info variable
        if ((dt.now() - df.loc[id, 'LastUsed']).days > 30 and df.loc['Permission'] != 'Owner'): #Checks if the last time the card was used was within a month ago
            print("Card expired") #Card is expired if the last time the card was used was more than a month (30 days) ago
            time = False #This variable stores whether or not the card expired
        else:
            df.loc[id, "LastUsed"] = dt.now() #Sets the new LastUsed to now, saves all new information/overwrites existing info into a csv/spreadsheet
            df.to_csv('whitelist.csv')
            print(user_info.to_string() + "\nCard recognized, access granted") #Writes message to user
            time = True
            df1.loc[len(df1.index)] = [id, df.loc[id, 'User'], df.loc[id, 'Permission'], dt.now()]
            df1.to_csv('overview.csv')
    else:
        in_df = False
        print("Card not recognized")
    if (in_df == True) and (time == True):
        print("Access Granted")
        client.publish(MQTT_TOPIC_PUB, 'open')
    else:
        print("Acess Denied")
    
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_SERVER, 1863, 60)
client.loop_start()

df1 = pd.DataFrame(data1)
df = pd.DataFrame(data2) #Creates a dataframe using the example csv
df = df.set_index("UID")
df1.to_csv("overview.csv")

try:
    while True:
        pass
except KeyboardInterrupt:
    client.loop.stop()
    client.disconnect()
'''def card_check(df): #use to control access
    print("Tap Card")
    ser = serial.Serial('COM6', 9600) #Links to the arduino program's Serial Monitor (info recorded by the Arduino)
    #time.sleep(2)
    try:
        while True:
            try:
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8').strip() #Converts info from Serial Monitor (utf-8) to regular English
                    if "UID" in line: #Runs below code if "UID" is in the Serial Monitor output
                        id = str(line.split(": ")[1]).strip().upper() #Takes the second half of the output (the UID of the RFID card)
                        if id in df.index: #Runs below code if the UID is in the given dataframe
                            in_df = True #This variable stores whether or not the UID is in the dataframe or not (True/False)
                            user_info = df.loc[id] #Stores all the information associated with the UID in the user_info variable
                            if ((dt.now() - df.loc[id, 'LastUsed']).days > 30 and df.loc['Permission'] != 'Owner'): #Checks if the last time the card was used was within a month ago
                                print("Card expired") #Card is expired if the last time the card was used was more than a month (30 days) ago
                                time = False #This variable stores whether or not the card expired
                            else:
                                df.loc[id, "LastUsed"] = dt.now() #Sets the new LastUsed to now, saves all new information/overwrites existing
                                                                    #info into a csv/spreadsheet
                                df.to_csv('whitelist.csv')
                                print(user_info.to_string() + "\nCard recognized, access granted") #Writes message to user
                                time = True
                                df1.loc[len(df1.index)] = [id, df.loc[id, 'User'], df.loc[id, 'Permission'], dt.now()]
                                df1.to_csv('overview.csv')
                        else:
                            in_df = False
                            print("Card not recognized")
                        if (in_df == True) and (time == True):
                            ser.write(b"ACCESS GRANTED\n") #Tells Arduino to let cardholder if the card isn't expired and is in the dataframe
                        else:
                            ser.write(b"ACCESS DENIED\n")
                        break
            except serial.SerialException as e:
                break  # Exit the loop and try to reinitialize the serial connection
            except Exception as e:
                print(f"Unexpected error: {e}")
                ser.close()
    except KeyboardInterrupt: #You can exit the program with ctrl+C
        print("Exiting Program")
    ser.close()

def add_update(df): #Use for adding cards
    print("Tap card")
    ser = serial.Serial('COM4', 9600)
    try:
        while True:
            try:
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8').strip()
                    if "UID" in line:
                        id = str(line.split(": ")[1]).strip().upper() # Same as in the other function
                        if id in df.index:
                            print("Card already in system")
                            print(df.loc[id])
                            answer = input("Update card? (y/n) ") #If the card is already in the dataframe, the user is prompted to choose to update the card or not
                            if answer.lower() == 'y':
                                update = input("Name or Permission ").upper() #If user types 'y', they're prompted to choose between updating the name or permission associated with the card
                                if update == "NAME":
                                    df.loc[id, 'User'] = input("New name? ") #If user picks name, they're prompted to type in the new name to be associated with the card
                                    print(df.loc[id]) #Prints updated data for the card
                                    df.to_csv('whitelist.csv') #Adds updated data to the whitelist csv
                                    ser.close()
                                elif update == "PERMISSION":
                                    df.loc[id, 'Permission'] = input("New permissions? ") #If user picks permission, they're prompted to type in the new permission to be associated with the card
                                    print(df.loc[id])
                                    df.to_csv('whitelist.csv')
                                    ser.close()
                                else: 
                                    print("Answer not detected, try again")
                                    break #Ends the program if the user doesn't pick name or permission
                            if answer.lower() == 'n':
                                print("Try different card") #Ends the program if the user doesn't want to update the card
                                break
                        else:
                            print("Card not in system")
                            answer = input("Add card? (y/n) ") #If the card isn't already in the system, the user is prompted to choose to add the card or not
                            if answer.lower() == 'y': #If the user picks 'y', the user is prompted to add name and permission
                                df.loc[id, 'User'] = input("Name? ")
                                df.loc[id, 'Permission'] = input("Permissions? ")
                                df.loc[id, 'LastUsed'] = dt.now() #LastUsed is added automatically
                                print("User " + df.loc[id, 'User'] + " added") #Confirmation message
                                print(df.loc[id])
                                df.to_csv('whitelist.csv')
                                ser.close()
                            elif answer.lower() == 'n':
                                print("OK try something else")
                                break #Ends program if the user doesn't want to add the card
            except serial.SerialException as e:
                break  # Exit the loop and try to reinitialize the serial connection
            except Exception as e:
                print(f"Unexpected error: {e}")
                ser.close()
    except KeyboardInterrupt:
        print("Exiting Program")
        ser.close()



#Used these to call functions and test them
#card_check(df)
#add_update(df)

'''