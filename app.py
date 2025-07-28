def create_location_schema():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS township (
            townshipID INTEGER PRIMARY KEY AUTOINCREMENT,
            townshipName TEXT NOT NULL UNIQUE,
            townshipArea REAL,
            townshipDescription TEXT
        );
        CREATE TABLE IF NOT EXISTS category (
            categoryID INTEGER PRIMARY KEY AUTOINCREMENT,
            categoryType TEXT NOT NULL UNIQUE,
            categoryDescription TEXT,
            categoryQty INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS location (
            locationID INTEGER PRIMARY KEY AUTOINCREMENT,
            locationName TEXT NOT NULL,
            locationAddress TEXT,
            locationLatitude REAL,
            locationLongitude REAL,
            townshipID INTEGER NOT NULL,
            categoryID INTEGER NOT NULL,
            FOREIGN KEY(townshipID) REFERENCES township(townshipID),
            FOREIGN KEY(categoryID) REFERENCES category(categoryID)
        );
    """)
    conn.commit()
    conn.close()


JSON_LOCATIONS_PATH = 'locations.json'  # Your JSON file path

def create_admin_table():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS admin (
            adminID INTEGER PRIMARY KEY AUTOINCREMENT,
            adminName TEXT NOT NULL,
            adminEmail TEXT NOT NULL UNIQUE,
            adminPassword TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()



# dijkstra's algorithm and haversine
import os
import json
import heapq
import sqlite3
from math import radians, sin, cos, sqrt, atan2
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.utils import secure_filename  # for file
# Path to save uploaded images
UPLOAD_FOLDER = 'static/images/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.secret_key = "your_secret_key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}


# JSON_LOCATIONS_PATH = "locations.json"
JSON_ADMINS_PATH = "admins.json"
MANDALAY_UNIVERSITY = "Mandalay University"

MILES_CONVERSION = 0.000621371

# Utility function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

DB_PATH = 'locations.db'  # ✅ Define your DB path

def load_locations():
    try:
        with open(JSON_LOCATIONS_PATH, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        # Return empty dict if JSON file not found
        return {}
    except json.JSONDecodeError:
        # Handle invalid JSON format gracefully
        return {}
   

def load_admin():
    with open(JSON_ADMINS_PATH, "r", encoding="utf-8") as file:
        return json.load(file)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth's radius in km
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def build_graph(locations):
    graph = {MANDALAY_UNIVERSITY: {}}
    for township, categories in locations.items():
        for category, places in categories.items():
            for place in places:
                node = place["name"]
                lat, lng = place["lat"], place["lng"]
                distance = haversine(21.9743, 96.0895, lat, lng)
                graph[MANDALAY_UNIVERSITY][node] = distance
                graph[node] = {}
                for other_township, other_categories in locations.items():
                    for other_category, other_places in other_categories.items():
                        for other_place in other_places:
                            if node != other_place["name"]:
                                dist = haversine(lat, lng, other_place["lat"], other_place["lng"])
                                graph[node][other_place["name"]] = dist
    return graph

# def dijkstra(graph, start):
#     queue = [(0, start, [])]
#     visited = set()
#     while queue:
#         (cost, node, path) = heapq.heappop(queue)
#         if node in visited:
#             continue
#         path = path + [node]
#         visited.add(node)
#         for neighbor, distance in graph.get(node, {}).items():
#             heapq.heappush(queue, (cost + distance, neighbor, path))
#     return {node: cost for cost, node, _ in queue}

def dijkstra(graph, start):
    queue = [(0, start)]  # (distance, node)
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    visited = set()

    while queue:
        cost, node = heapq.heappop(queue)
        if node in visited:
            continue
        visited.add(node)

        for neighbor, distance in graph.get(node, {}).items():
            new_cost = cost + distance
            if new_cost < distances[neighbor]:  # Update with the shortest found distance
                distances[neighbor] = new_cost
                heapq.heappush(queue, (new_cost, neighbor))

    return distances


@app.route('/')
def index():
    return render_template('index.html')



# @app.route('/locations/<township>/<category>')
# def locations(township, category):
#     data = load_locations()
#     if township not in data or category not in data[township]:
#         return jsonify({'locations': []})
#     graph = build_graph(data)
#     results = []
#     for location in data[township][category]:
#         name = location['name']
#         distance_meters = dijkstra(graph, MANDALAY_UNIVERSITY).get(name, 99999)  # Replace Infinity with a large number
#         distance_miles = round(distance_meters * MILES_CONVERSION, 2)
        
#         # Calculate cycling time instead of walking time
#         cycling_time_minutes = round((distance_miles / CYCLING_SPEED_MPH) * 60)

#         results.append({
#             'name': name,
#             'latitude': location['lat'],
#             'longitude': location['lng'],
#             'address': location['address'],
#             'image': location.get('image', 'https://via.placeholder.com/150'),
#             'distance': f"{cycling_time_minutes} min ({distance_miles} miles)"
#         })
#     results.sort(key=lambda x: x['distance'])
#     return jsonify({'locations': results})
# @app.route('/locations/<township>/<category>')
# def locations(township, category):
#     data = load_locations()
#     if township not in data or category not in data[township]:
#         return jsonify({'locations': []})
    
#     graph = build_graph(data)
#     shortest_paths = dijkstra(graph, MANDALAY_UNIVERSITY)  # Get shortest distances from Mandalay University

#     def format_time(minutes_float):
#         total_seconds = int(minutes_float * 60)
#         mins = total_seconds // 60
#         secs = total_seconds % 60
#         return f"{mins} min {secs} sec" if mins > 0 else f"{secs} sec"

#     def get_minutes_seconds(time_string):
#         parts = time_string.split()
#         mins = int(parts[0]) if "min" in parts else 0
#         secs = int(parts[2]) if "sec" in parts else 0
#         return mins * 60 + secs
    
#     results = []


#     for location in data[township][category]:
#         name = location['name']
#         distance_meters = shortest_paths.get(name, float('inf'))  # Get shortest distance
#         if distance_meters == float('inf'):
#             continue  # Skip unreachable locations

#         distance_km = round(distance_meters / 1000, 2)

#         motorbike_time = format_time(distance_km / 30)  # 30 km/h motorbike
#         car_time = format_time(distance_km / 45)        # 45 km/h car

#         results.append({
#             'name': name,
#             'latitude': location['lat'],
#             'longitude': location['lng'],
#             'address': location['address'],
#             'image': location.get('image', 'https://via.placeholder.com/150'),
#             'distance_km': distance_km,
#             'motorbike_time': motorbike_time,
#             'car_time':  car_time
#         })

#     results.sort(key=lambda x: get_minutes_seconds(x['motorbike_time']))

#     return jsonify({'locations': results})
@app.route('/locations/<township>/<category>')
def locations(township, category):
    data = load_locations()
    
    if township not in data:
        return jsonify({'error': f"Township '{township}' not found.", 'locations': []}), 404
    
    if category not in data[township]:
        return jsonify({'error': f"Category '{category}' not found in '{township}'.", 'locations': []}), 404
    
    graph = build_graph(data)
    shortest_paths = dijkstra(graph, MANDALAY_UNIVERSITY)

    def format_time(hours_float):
        total_seconds = int(hours_float * 3600)
        mins = total_seconds // 60
        secs = total_seconds % 60
        if mins > 0:
            return f"{mins} min {secs} sec" if secs > 0 else f"{mins} min"
        else:
            return f"{secs} sec"
        
    def get_minutes_seconds(time_string):
        # Safer parsing
        mins = 0
        secs = 0
        parts = time_string.split()
        for i, part in enumerate(parts):
            if part == "min":
                try:
                    mins = int(parts[i-1])
                except:
                    mins = 0
            elif part == "sec":
                try:
                    secs = int(parts[i-1])
                except:
                    secs = 0
        return mins * 60 + secs
    
    results = []

    for location in data[township][category]:
        name = location['name']
        distance_meters = shortest_paths.get(name)
        
        if distance_meters is None or distance_meters == float('inf'):
            # Skip if no path found
            continue
        
        distance_km = round(distance_meters / 1000, 2)
        motorbike_time = format_time(distance_km / 30)  # 30 km/h motorbike
        car_time = format_time(distance_km / 45)        # 45 km/h car

        results.append({
            'name': name,
            'latitude': location['lat'],
            'longitude': location['lng'],
            'address': location['address'],
            'image': location.get('image', 'https://via.placeholder.com/150'),
            'distance_km': distance_km,
            'motorbike_time': motorbike_time,
            'car_time': car_time
        })

    # Sort by motorbike time in seconds
    results.sort(key=lambda x: get_minutes_seconds(x['motorbike_time']))

    # return jsonify({'locations': results})


    # Handle pagination
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 100))
    start = (page - 1) * limit
    end = start + limit

    paginated_results = results[start:end]
    total_pages = (len(results) + limit - 1) // limit

    return jsonify({
        'locations': paginated_results,
        'total': len(results),
        'page': page,
        'total_pages': total_pages
    })

# walking time
# @app.route('/locations/<township>/<category>')
# def locations(township, category):
#     data = load_locations()
#     if township not in data or category not in data[township]:
#         return jsonify({'locations': []})
#     graph = build_graph(data)
#     results = []
#     for location in data[township][category]:
#         name = location['name']
#         distance_meters = dijkstra(graph, MANDALAY_UNIVERSITY).get(name, 99999)  # Replace Infinity with a large number
#         distance_miles = round(distance_meters * MILES_CONVERSION, 2)
#         walking_time_minutes = round((distance_miles / WALKING_SPEED_MPH) * 60)

#         results.append({
#             'name': name,
#             'latitude': location['lat'],
#             'longitude': location['lng'],
#             'address': location['address'],
#             'distance': f"{walking_time_minutes} min ({distance_miles} miles)"
#         })
#     results.sort(key=lambda x: x['distance'])
#     return jsonify({'locations': results})

def migrate_admins_json_to_db(json_path='admins.json', db_path=DB_PATH):
    if not os.path.exists(json_path):
        print(f"[INFO] Skipping admin migration: '{json_path}' not found.")
        return

    with open(json_path, 'r', encoding='utf-8') as file:
        admins = json.load(file)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for admin in admins.values():
        cursor.execute('''
            INSERT OR IGNORE INTO admin (adminName, adminEmail, adminPassword)
            VALUES (?, ?, ?)
        ''', (admin['name'], admin['email'], admin['password']))

    conn.commit()
    conn.close()
    if not os.path.exists(json_path):
        print(f"[INFO] Skipping admin migration: '{json_path}' not found.")
        return

    with open(json_path, 'r', encoding='utf-8') as file:
        admins = json.load(file)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for admin in admins.values():
        cursor.execute('''
            INSERT OR IGNORE INTO admin (adminName, adminEmail, adminPassword)
            VALUES (?, ?, ?)
        ''', (admin['name'], admin['email'], admin['password']))

    conn.commit()
    conn.close()

migrate_admins_json_to_db()

@app.route('/admin')
def admin_login_page():
        if "admin_name" in session:
            return redirect(url_for('admin_dashboard'))
        return render_template('admin_login.html')

@app.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.json
    username_or_email = data.get('username_or_email')
    password = data.get("password")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT adminName FROM admin
        WHERE (adminEmail = ? OR adminName = ?) AND adminPassword = ?
    ''', (username_or_email, username_or_email, password))
    result = cursor.fetchone()
    conn.close()

    if result:
        admin_name = result[0]
        session['admin_name'] = admin_name
        return jsonify({'status': 'success', 'message': f'Welcome {admin_name}!'})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid admin name/email or password'}), 401

@app.route('/admin/dashboard')
def admin_dashboard():
        if 'admin_name' not in session:
            return redirect(url_for('admin_login_page'))

        admin_name = session['admin_name']
        data = load_locations()

        # Extract all townships and categories
        townships = list(data.keys())
        categories = list({cat for township in data.values() for cat in township.keys()})

        return render_template('admin_dashboard.html', admin_name=admin_name, townships=townships, categories=categories)

@app.route('/admin/logout')
def logout():
        session.pop("admin_name", None)
        return redirect(url_for('admin_login_page'))


@app.route('/admin/create_location', methods=['POST'])
def create_location():
    if "admin_name" not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403

    # Get the form data
    township = request.form['township']
    category = request.form['category']
    name = request.form['name']
    lat = float(request.form['latitude'])
    lng = float(request.form['longitude'])
    address = request.form['address']

    # Handle the file upload
    image_file = request.files['imageFile']
    # if image_file and allowed_file(image_file.filename):
    #     filename = secure_filename(image_file.filename)
    #     image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    #     image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    # else:
    #     image_path = 'default.png'  # Use a default image if no file is uploaded
    if image_file and allowed_file(image_file.filename):
        filename = secure_filename(image_file.filename)
        image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        image_path = f"/{app.config['UPLOAD_FOLDER']}{filename}"  # ✅ FIX HERE
    else:
        image_path = '/static/images/default.png'  # Must be inside your static folder

    data = load_locations()
    if township not in data:
        data[township] = {}
    if category not in data[township]:
        data[township][category] = []

    data[township][category].append({
        'name': name,
        'lat': lat,
        'lng': lng,
        'address': address,
        'image': image_path  # Save the image path
    })

    with open(JSON_LOCATIONS_PATH, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    return jsonify({'status': 'success', 'message': 'Location added successfully!'})

#edit
@app.route('/admin/edit_location/<township>/<category>/<old_name>', methods=['POST'])
def edit_location(township, category, old_name):
    data = load_locations()
    req = request.get_json()
    new_name = req.get("new_name")

    if not new_name:
        return jsonify({"status": "error", "message": "New name is required"}), 400

    locations = data.get(township, {}).get(category, [])

    for loc in locations:
        if loc["name"] == old_name:
            loc["name"] = new_name

            with open('locations.json', 'w') as file:
                json.dump(data, file)
                
            return jsonify({"status": "success", "message": "Location updated"}), 200

    return jsonify({"status": "error", "message": "Location not found"}), 404

# delete
@app.route('/admin/delete_location/<township>/<category>/<name>', methods=['POST'])
def delete_location(township, category, name):
    if request.method == 'POST' and request.json.get('action') == 'delete':
        # Load the current data
        with open('locations.json', 'r') as file:
            data = json.load(file)

        # Find and remove the location
        if township in data and category in data[township]:
            data[township][category] = [
                loc for loc in data[township][category] if loc['name'] != name
            ]

        # Save the updated data
        with open('locations.json', 'w') as file:
            json.dump(data, file)

        return jsonify({'status': 'success', 'message': 'Location deleted successfully!'})
    return jsonify({'status': 'error', 'message': 'Location not found or invalid request.'})

if __name__ == '__main__':
    create_admin_table()
    migrate_admins_json_to_db()
    create_location_schema()
    # app.run(debug=True)
    # from os import getenv
    # app.run(host="0.0.0.0", port=int(getenv("PORT", 5000)))
    pass
