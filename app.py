from datetime import datetime
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
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)

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

@app.route('/dashboard/history')
def view_history():
    if 'username' in session:
        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM cab WHERE status='available'")
            cabs = cursor.fetchall()
            cursor.close()
            connection.close()
            return render_template('history.html', cabs=cabs)
        except Error as e:
            return f"An error occurred: {e}"
    else:
        return redirect('/login')

@app.route('/dashboard/bookings')
def view_bookings():
    if 'username' in session:
        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM booking")
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
    return render_template('index-1.html')

@app.route('/save_distance', methods=['POST'])
def save_distance():
    data = request.json
    print("Received data:", data)

    session['distance'] = data.get('distance')
    session['pickup_location'] = data.get('pickupLocation')
    session['dropoff_location'] = data.get('dropoffLocation')

    if not session['pickup_location'] or not session['dropoff_location'] or not session['distance']:
        return jsonify({"error": "Missing location or distance data."}), 400

    return jsonify({"status": "success"})

@app.route('/collect_info')
def collect_info():
    pickup_location = request.args.get('pickup')
    dropoff_location = request.args.get('dropoff')
    distance = request.args.get('distance')
    return render_template('collect_info.html', pickup=pickup_location, dropoff=dropoff_location, distance=distance)

@app.route('/save_booking_details', methods=['POST'])
def save_booking_details():
    data = request.json
    pickup_time = data.get('pickupTime')
    passengers = data.get('passengers')
    amount = data.get('amount')

    print("Session Values:")
    print("Pickup Location:", session.get('pickup_location'))
    print("Dropoff Location:", session.get('dropoff_location'))
    print("Distance:", session.get('distance'))

    if 'pickup_location' not in session or 'dropoff_location' not in session or 'distance' not in session:
        return jsonify({"error": "Session data missing"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    pickup_time_obj = datetime.strptime(pickup_time, '%Y-%m-%dT%H:%M')

    try:
        cursor.execute('''
            INSERT INTO bookings (pickup_location, dropoff_location, distance, pickup_time, passengers, amount)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (session['pickup_location'], session['dropoff_location'], session['distance'], pickup_time_obj, passengers, amount))

        conn.commit()
    except Error as e:
        print("Database error:", e)
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({"status": "success"})

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

