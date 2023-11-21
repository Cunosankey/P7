from flask import Flask, render_template, request, redirect, url_for
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
    return render_template("BookRoom.html")

@app.route('/information')
def information():
    return render_template("Information.html")
@app.route('/fake_booking')
def fake_booking():
    return fake_group_room()

@app.route('/submit_booking', methods=['POST']) #This function is used to handle a POST request when a user submits a booking form. It takes the room number and timeslot from the form data, generates a fake booking ID and user ID, and inserts these into the bookings table in the database.
@app.route('/submit_booking', methods=['POST'])
def submit_booking():
    if request.method == 'POST':
        room_number = request.form.get('room')
        timeslot = request.form.get('timeslot')

        fake_user_id = fake.random_int(min=1000, max=9999)  # Generate a fake user ID

        fake_booking_id = fake.random_int(min=10000, max=99999)
        
        conn = sqlite3.connect('booking.db')
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO bookings (BookingID, UserID, RoomNO, Day, Time) VALUES (?, ?, ?, ?, ?)",
               (fake_booking_id, fake_user_id, room_number, timeslot.strftime('%Y-%m-%d'), timeslot.strftime('%H:%M:%S')))

            conn.commit()
            return 'Booking successfully added'
        except Exception as e:
            print("Error adding booking:", e)
            conn.rollback()
            return 'Error adding the booking'
        finally:
            conn.close()

@app.route('/booked_room') #This function is used to display all the booked rooms. It retrieves the booked rooms from the database and passes them to the BookedRooms.html template.
def booked_room():
    booked_rooms = get_booked_rooms()
    return render_template("BookedRooms.html", booked_rooms=booked_rooms)

def fake_group_room(): #This function is used to generate fake booking data for testing purposes. It generates fake booking IDs, user IDs, and booking times, and inserts these into the bookings table for each room number.
    fake_bookings = [fake.date_time_this_year() for _ in range(25)] # Generate 5 fake booking dates
    fake_user_ids = [fake.random_int(min=1000, max=9999) for _ in range(5)] # Generate 5 fake user IDs

    conn = sqlite3.connect('booking.db') # Connect to the database
    cursor = conn.cursor() # Cursor is a pointer to the database. It is used to execute SQL commands
 
    try:
        booking_ids = set()  # Keep track of unique BookingIDs
        for RoomNO in [4118, 4119, 4120, 4121, 4122]:
            for _ in range(5):
                fake_booking_id = fake.random_int(min=10000, max=99999)
                while fake_booking_id in booking_ids:
                    fake_booking_id = fake.random_int(min=10000, max=99999)
                booking_ids.add(fake_booking_id)

                fake_user_id = fake.random_int(min=1000, max=9999)
                timeslot = fake_bookings.pop(0)

                cursor.execute("INSERT INTO bookings (BookingID, UserID, RoomNO, Day, Time) VALUES (?, ?, ?, ?, ?)",
                               (fake_booking_id, fake_user_id, RoomNO, timeslot.date().strftime('%Y-%m-%d'),
                                timeslot.time().strftime('%H:%M:%S')))
        conn.commit()
        return 'Fake bookings successfully added'
    except Exception as e:
        print("Error adding fake bookings:", e)
        conn.rollback()
        return 'Error adding the fake bookings'
    finally:
        conn.close()

def get_booked_timeslots():
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

    if __name__ == '__main__':
        app.run(debug=True) #debug=True means that the server will reload itself each time you make a change to the code
