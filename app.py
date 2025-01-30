from datetime import datetime
import requests
from flask import Flask, render_template, request, redirect, session, jsonify
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash
from geopy.geocoders import Nominatim

host = 'b6pvycldyedsyrjrdnom-mysql.services.clever-cloud.com'
user = 'uuksqqmvg93rwh6f'
password = 'I052xaxHKOAm9DOxq4Ik'
database = 'b6pvycldyedsyrjrdnom'
port = 3306  

app = Flask(__name__)
app.secret_key = 'supersecretkey'
geolocator = Nominatim(user_agent="cab_booking_app")

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=host,  
            database=database,  
            user=user,  
            password=password 
        )
        return connection
    except Error as e:
        print(f"Database connection error: {e}")
        return None

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])  
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        connection = get_db_connection()
        if connection:
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
        return "Database connection error."
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        phone_number = request.form['phone_number']
        address = request.form['address']
        hashed_password = generate_password_hash(password)
        
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            try:
                cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
                cursor.execute("INSERT INTO user (name, phone, address) VALUES (%s, %s, %s)", (username, phone_number, address))
                connection.commit()
                return redirect('/login')
            except Error as e:
                return f"An error occurred: {e}"
            finally:
                cursor.close()
                connection.close()
        return "Database connection error."
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html', username=session['username'])
    return redirect('/login')

@app.route('/dashboard/drivers')
def view_drivers():
    if 'username' in session:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM driver")
            drivers = cursor.fetchall()
            cursor.close()
            connection.close()
            return render_template('availabledriver.html', drivers=drivers)
        return "Database connection error."
    return redirect('/login')

@app.route('/dashboard/cabs')
def view_cabs():
    if 'username' in session:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM cab WHERE status='available'")
            cabs = cursor.fetchall()
            cursor.close()
            connection.close()
            return render_template('viewcabs.html', cabs=cabs)
        return "Database connection error."
    return redirect('/login')

@app.route('/dashboard/bookings')
def view_bookings():
    if 'username' in session:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute('SELECT userid FROM users WHERE username = %s',(session['username'],))
            result = cursor.fetchone()
            if result is None:
                return jsonify({"error": "Invalid session credentials"}), 401

            cursor.execute("SELECT * FROM booking where userid= %s", (result['userid'],))  
            bookings = cursor.fetchall()
            cursor.close()
            connection.close()
            return render_template('viewbooking.html', bookings=bookings)
        return "Database connection error."
    return redirect('/login')

@app.route('/dashboard/book')
def book_cab():
    return render_template('index-1.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)