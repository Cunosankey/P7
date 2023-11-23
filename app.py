from flask import Flask, render_template, request, redirect, url_for, jsonify
from accordion import accordion_function
import sqlite3
from faker import Faker
from dateutil.parser import parse


app = Flask(__name__)
fake = Faker()


@app.route('/')
def home():
    room_data = accordion_function()
    room_numbers = [4118, 4119, 4120, 4121, 4122]
    room_info = [{'room': room_number, 'status': status} for room_number, status in zip(room_numbers, room_data)]
    return render_template("home.html", room_info=room_info)

@app.route('/booking')
def booking():
    reserved_timeslots = get_reserved_timeslots()
    return render_template("BookRoom.html", reserved_timeslots=reserved_timeslots)

@app.route('/information')
def information():
    return render_template("Information.html")

def insert_booking(timeslots, room): #This function is used to insert a booking into the database. It takes a list of timeslots and a room number as parameters, and inserts each timeslot into the bookings table in the database.
    conn = sqlite3.connect('booking.db')
    cursor = conn.cursor()

    try:
        for timeslot in timeslots:
            cursor.execute("INSERT INTO bookings (Time, RoomNO) VALUES (?, ?)", (timeslot, room))
        conn.commit()
    except Exception as e:
        print('Error inserting booking:', e)
    finally:
        conn.close()

@app.route('/submit_booking', methods=['POST']) #This function is used to handle a POST request when a user submits a booking form. It takes the room number and timeslot from the form data, generates a fake booking ID and user ID, and inserts these into the bookings table in the database.
def submit_booking():
    data = request.get_json()
    timeslots = data.get('timeslots')
    room = data.get('Room')

    insert_booking(timeslots, room)

    return jsonify({'message': 'Booking submitted successfully'}), 200


@app.route('/booked_room') #This function is used to display all the booked rooms. It retrieves the booked rooms from the database and passes them to the BookedRooms.html template.
def booked_room(): #We keep this for now, but probably have to delete this route since it shows the same on the front page.
    booked_rooms = get_booked_rooms()
    return render_template("BookedRooms.html", booked_rooms=booked_rooms)

def get_booked_timeslots(): # This function connects to the SQLite database 'booking.db', retrieves all the times (TIME) from the bookings table, and returns a list of timeslots.
    conn =sqlite3.connect('booking.db')
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT Time FROM bookings")
        booked_timeslots=[row[0] for row in cursor.fetchall()] #fetchall() returns a list of tuples, where each tuple is a row in the database. We only want the first element of each tuple, which is the timeslot
        return booked_timeslots
    except Exception as e:
        print('Error retrieving booked timeslots:', e)
    finally:
        conn.close()

def get_booked_rooms(): #This function connects to the SQLite database 'booking.db', retrieves all the room numbers (RoomNO) and times (TIME) from the bookings table, and returns a list of dictionaries where each dictionary represents a booked room with its room number and timeslot.
    conn =sqlite3.connect('booking.db')
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT RoomNO, TIME FROM bookings")
        booked_rooms = [{'room number': row[0], 'timeslot': parse(row[1]).strftime("%Y-%m-%d %H:%M")} for row in cursor.fetchall()] #fetchall() returns a list of tuples, where each tuple is a row in the database. We only want the first element of each tuple, which is the timeslot
        return booked_rooms
    except Exception as e:
        print('Error retrieving booked timeslots:', e)
    finally:
        conn.close()

def get_reserved_timeslots():
    conn = sqlite3.connect('booking.db')
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT DISTINCT Time FROM bookings")
        reserved_timeslots = [row[0] for row in cursor.fetchall()]
        return reserved_timeslots
    except Exception as e:
        print('Error retrieving reserved timeslots:', e)
    finally:
        conn.close()


    if __name__ == '__main__':
        app.run(debug=True) #debug=True means that the server will reload itself each time you make a change to the code
