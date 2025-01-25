import requests
from flask import Flask, render_template, request, redirect, session,jsonify
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
app.secret_key = 'your_secret_key'
geolocator = Nominatim(user_agent="cab_booking_app")

ORS_API_KEY = '5b3ce3597851110001cf6248367c5c9fb6ec4f4cb0c564bd4bf6538f'

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
            cursor.execute("INSERT INTO users (username,password) VALUES (%s, %s)", (username, hashed_password))
            cursor.execute("INSERT INTO user (name,phone,address)VALUES (%s,%s, %s)", (username,phone_number,address))
            connection.commit()
            cursor.close()
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
    # Renders the booking page with map
    return render_template('index-1.html')


"""
@app.route('/calculate_route', methods=['GET'])
def calculate_route():
    pickup = request.args.get('pickup')  # e.g., "lat,lng"
    dropoff = request.args.get('dropoff')  # e.g., "lat,lng"

    # Parse pickup and dropoff coordinates
    pickup_coords = pickup.split(',')
    dropoff_coords = dropoff.split(',')

    # API request to OpenRouteService
    url = 'https://api.openrouteservice.org/v2/directions/driving-car'
    headers = {
        'Authorization': ORS_API_KEY,
        'Content-Type': 'application/json'
    }
    data = {
        "coordinates": [
            [float(pickup_coords[1]), float(pickup_coords[0])],  # [lng, lat] for pickup
            [float(dropoff_coords[1]), float(dropoff_coords[0])]  # [lng, lat] for dropoff
        ]
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        response_data = response.json()

        # Check for a successful response
        if 'routes' in response_data:
            # Send the route geometry back to the frontend
            route_geometry = response_data['routes'][0]['geometry']
            return jsonify(route=route_geometry)
        else:
            return jsonify({"error": "No route found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/calculate_route', methods=['GET'])
def calculate_route():
    pickup = request.args.get('pickup')  # e.g., "lat,lng"
    dropoff = request.args.get('dropoff')  # e.g., "lat,lng"

    # Parse pickup and dropoff coordinates
    pickup_coords = pickup.split(',')
    dropoff_coords = dropoff.split(',')

    # API request to OpenRouteService
    url = 'https://api.openrouteservice.org/v2/directions/driving-car'
    headers = {
        'Authorization': ORS_API_KEY,
        'Content-Type': 'application/json'
    }
    data = {
        "coordinates": [
            [float(pickup_coords[1]), float(pickup_coords[0])],  # [lng, lat] for pickup
            [float(dropoff_coords[1]), float(dropoff_coords[0])]  # [lng, lat] for dropoff
        ]
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        response_data = response.json()

        # Check for a successful response
        if 'routes' in response_data and len(response_data['routes']) > 0:
            # Get the route geometry
            route_geometry = response_data['routes'][0]['geometry']
            # Get distance and duration
            distance = response_data['routes'][0]['summary']['distance'] / 1000  # Convert to km
            duration = response_data['routes'][0]['summary']['duration'] / 60  # Convert to minutes

            # Return the route geometry, distance, and duration
            return jsonify({
                'geometry': route_geometry,
                'distance': distance,
                'duration': duration
            })
        else:
            return jsonify({"error": "No route found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/calculate_route', methods=['GET'])
def calculate_route():
    pickup = request.args.get('pickup')
    dropoff = request.args.get('dropoff')

    # Geocode the pickup and dropoff locations
    pickup_coords = geocode(pickup)
    dropoff_coords = geocode(dropoff)

    if not pickup_coords or not dropoff_coords:
        return jsonify({"error": "Invalid pickup or drop-off location."}), 400

    # Prepare the API request for OpenRouteService
    url = 'https://api.openrouteservice.org/v2/directions/driving-car'
    headers = {
        'Authorization': ORS_API_KEY,
        'Content-Type': 'application/json'
    }
    data = {
        "coordinates": [
            [pickup_coords[1], pickup_coords[0]],  # [lng, lat]
            [dropoff_coords[1], dropoff_coords[0]]  # [lng, lat]
        ]
    }

    # Call the OpenRouteService API
    response = requests.post(url, json=data, headers=headers)
    response_data = response.json()

    if 'routes' in response_data and len(response_data['routes']) > 0:
        # Get the route geometry
        route_geometry = response_data['routes'][0]['geometry']
        distance = response_data['routes'][0]['summary']['distance']  # in meters
        duration = response_data['routes'][0]['summary']['duration']  # in seconds

        return jsonify({
            "geometry": route_geometry,
            "distance": distance,
            "duration": duration
        })

    return jsonify({"error": "Could not calculate the route."}), 500

def geocode(location):
    try:
        location = geolocator.geocode(location)
        if location:
            return (location.latitude, location.longitude)
    except Exception as e:
        print(f"Error during geocoding: {e}")
    return None
"""
# @app.route('/calculate_route', methods=['POST'])
# def calculate_route():
#     pickup_location = request.form.get('pickup_location')
#     dropoff_location = request.form.get('dropoff_location')

#     pickup_coords = geocode(pickup_location)
#     dropoff_coords = geocode(dropoff_location)

#     if not pickup_coords:
#         return jsonify({"error": "Invalid pickup location."}), 400
#     if not dropoff_coords:
#         return jsonify({"error": "Invalid drop-off location."}), 400

#     url = 'https://api.openrouteservice.org/v2/directions/driving-car'
#     headers = {
#         'Authorization': ORS_API_KEY,
#         'Content-Type': 'application/json'
#     }
#     data = {
#         "coordinates": [
#             [pickup_coords[1], pickup_coords[0]],  # [lng, lat]
#             [dropoff_coords[1], dropoff_coords[0]]  # [lng, lat]
#         ]
#     }

#     try:
#         response = requests.post(url, json=data, headers=headers)
#         response.raise_for_status()
#     except requests.exceptions.RequestException as e:
#         return jsonify({"error": f"Error contacting the routing service: {e}"}), 500

#     response_data = response.json()

#     if 'routes' in response_data and len(response_data['routes']) > 0:
#         route_geometry = response_data['routes'][0]['geometry']
#         distance = response_data['routes'][0]['summary']['distance']  # in meters
#         duration = response_data['routes'][0]['summary']['duration']  # in seconds

#         return jsonify({
#             "geometry": route_geometry,
#             "distance": distance,
#             "duration": duration
#         })

#     return jsonify({"error": "Could not calculate the route."}), 500


# Route to save the distance and locations
@app.route('/save_distance', methods=['POST'])
def save_distance():
    data = request.json
    session['distance'] = data['distance']
    session['pickup_location'] = data['pickupLocation']
    session['dropoff_location'] = data['dropoffLocation']
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
    session['pickup_time'] = data['pickupTime']
    session['passengers'] = data['passengers']
    session['amount'] = data['amount']
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
    app.run(debug=False,host='0.0.0.0')
