from datetime import datetime
import requests
from flask import Flask, render_template, request, redirect, session, jsonify
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash
from geopy.geocoders import Nominatim

# Database and API configuration  

host = 'b6pvycldyedsyrjrdnom-mysql.services.clever-cloud.com'
user = 'uuksqqmvg93rwh6f'
password = 'I052xaxHKOAm9DOxq4Ik'
database = 'b6pvycldyedsyrjrdnom'
port = 3306  

app = Flask(__name__)
app.secret_key = 'your_secret_key'
geolocator = Nominatim(user_agent="cab_booking_app")

# Function to get a database connection
def get_db_connection():
    connection = mysql.connector.connect(
        host=host,  
        database=database,  
        user=user,  
        password=password 
    )
    return connection

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])  
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            cursor.close()
            connection.close()

            if user and check_password_hash(user['password'], password):
                session['username'] = user['username']
                return redirect('/dashboard')
            else:
                return "Invalid username or password."

        except Error as e:
            return f"An error occurred: {e}"

    return render_template('login.html')

@app.route('/register.html', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        phone_number = request.form['phone_number']
        address = request.form['address']
        hashed_password = generate_password_hash(password)

        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
            cursor.execute("INSERT INTO user (name, phone, address) VALUES (%s, %s, %s)", (username, phone_number, address))
            connection.commit()
            cursor.close()
            connection.close()
            return redirect('/login')
        except Error as e:
            return f"An error occurred: {e}"

    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html', username=session['username'])
    else:
        return redirect('/login')

@app.route('/dashboard/drivers')
def view_drivers():
    if 'username' in session:
        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM driver")
            drivers = cursor.fetchall()
            cursor.close()
            connection.close()
            return render_template('availabledriver.html', drivers=drivers)
        except Error as e:
            return f"An error occurred: {e}"
    else:
        return redirect('/login')

@app.route('/dashboard/cabs')
def view_cabs():
    if 'username' in session:
        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM cab WHERE status='available'")
            cabs = cursor.fetchall()
            cursor.close()
            connection.close()
            return render_template('viewcabs.html', cabs=cabs)
        except Error as e:
            return f"An error occurred: {e}"
    else:
        return redirect('/login')

@app.route('/dashboard/bookings')
def view_bookings():
    if 'username' in session:
        try:
            username = session.get('username')
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute('SELECT userid FROM users WHERE username = %s',(username,))
            result = cursor.fetchone()
            if result is None:
                return jsonify({"error": "Invalid session credentials"}), 401

            userid = result['userid']
            cursor.execute("SELECT * FROM booking where userid= %s",(userid,))  
            bookings = cursor.fetchall()
            cursor.close()
            connection.close()
            return render_template('viewbooking.html', bookings=bookings)
        except Error as e:
            return f"An error occurred: {e}"
    else:
        return redirect('/login')

@app.route('/dashboard/book')
def book_cab():
    # Renders the booking page with map
    return render_template('index-1.html')


@app.route('/save_distance', methods=['POST'])
def save_distance():
    data = request.json
    session['pickup_location'] = data.get('pickupLocation')
    session['drop_location'] = data.get('dropoffLocation')
    session['distance'] = data.get('distance')

    if not all([session['pickup_location'], session['drop_location'], session['distance']]):
        return jsonify({"error": "Missing location or distance data."}), 400

    return jsonify({"status": "success"})

@app.route('/collect_info')
def collect_info():
    pickup_location = request.args.get('pickup')
    drop_location = request.args.get('dropoff')
    distance = request.args.get('distance')
    return render_template('collect_info.html', pickup=pickup_location, dropoff=drop_location, distance=distance)

@app.route('/save_booking_details', methods=['POST'])
def save_booking_details():
    data = request.json
    pickup_location = data.get('pickup_location')
    pickup_time = data.get('pickup_time')
    pickup_date = data.get('pickup_date')
    drop_location = data.get('drop_location')
    no_of_people = data.get('no_of_people')
    amount = data.get('amount')
    username = session.get('username')

    if not all([pickup_location, pickup_time, pickup_date, drop_location, no_of_people, amount]):
        return jsonify({"error": "Required booking details missing"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        pickup_time_obj = datetime.strptime(pickup_time, '%H:%M').time()
        pickup_date_obj = datetime.strptime(pickup_date, '%Y-%m-%d').date()
        cursor.execute('SELECT userid FROM users WHERE username = %s', (username,))
        result = cursor.fetchone()
        userid = result[0]
        if result is None:
            return jsonify({"error": "Invalid session credentials"}), 401
        
        cursor.execute('''
            INSERT INTO booking (userid,pickup_location, pickup_time, pickup_date, drop_location, no_of_people, amount)
            VALUES (%s,%s, %s, %s, %s, %s, %s)
        ''', (
            userid,
            pickup_location,
            pickup_time_obj,
            pickup_date_obj,
            drop_location,
            no_of_people,
            amount
        ))

        conn.commit()
        booking_id = cursor.lastrowid

        return jsonify({"status": "success", "booking_id": booking_id})

    except Error as e:
        print("Database error:", e)
        return jsonify({"error": "Database error"}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/payment')
def payment():
    amount = request.args.get('amount')
    return render_template('payment.html', amount=amount)

@app.route('/booking_success')
def booking_success():
    return render_template('booking_success.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')

if __name__ == '__main__':
    app.secret_key = 'supersecretkey'
    app.run(debug=True)
