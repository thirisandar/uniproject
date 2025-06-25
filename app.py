# only using openstreet map leaflet.js and haversine() formula
# import json
# import math
# from flask import Flask, render_template, request, jsonify, session, redirect, url_for

# app = Flask(__name__)
# app.secret_key = "your_secret_key"  # Needed for session management

# # Mandalay University coordinates (starting point)
# MANDALAY_UNIVERSITY = (21.9743, 96.0895)

# # Paths to JSON files
# JSON_LOCATIONS_PATH = 'locations.json'
# JSON_ADMINS_PATH = 'admins.json'

# # Function to calculate distance using Haversine formula
# def haversine(lat1, lon1, lat2, lon2):
#     R = 6371  # Radius of the Earth in km
#     dlat = math.radians(lat2 - lat1)
#     dlon = math.radians(lon2 - lon1)
#     a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
#     c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
#     distance = R * c
#     return distance

# # Load admin data
# def load_admins():
#     with open(JSON_ADMINS_PATH, 'r') as file:
#         return json.load(file)

# # Load location data
# def load_locations():
#     with open(JSON_LOCATIONS_PATH, 'r') as file:
#         return json.load(file)

# # Route for the homepage (open for all users)
# @app.route('/')
# def index():
#     return render_template('index.html')

# # Route to get locations based on township and category
# @app.route('/locations/<township>/<category>')
# def locations(township, category):
#     with open(JSON_LOCATIONS_PATH, 'r') as file:
#         data = json.load(file)

#     if township not in data or category not in data[township]:
#         return jsonify({'locations': []})

#     locations = [
#         {
#             'name': loc['name'],
#             'latitude': loc['lat'],
#             'longitude': loc['lng'],
#             'address': loc['address'],
#             'distance': haversine(MANDALAY_UNIVERSITY[0], MANDALAY_UNIVERSITY[1], loc['lat'], loc['lng'])
#         }
#         for loc in data[township][category]
#     ]

#     locations.sort(key=lambda loc: loc['distance'])
#     return jsonify({'locations': locations})

# # Admin login page
# @app.route('/admin')
# def admin_login_page():
#     if "admin_name" in session:
#         return redirect(url_for('admin_dashboard'))
#     return render_template('admin_login.html')

# # Admin login API
# @app.route('/admin/login', methods=['POST'])
# def admin_login():
#     data = request.json
#     email = data.get("email")
#     password = data.get("password")

#     admins = load_admins()
#     for admin in admins.values():
#         if admin["email"] == email and admin["password"] == password:
#             session["admin_name"] = admin["name"]
#             return jsonify({"status": "success", "message": "Login Successful", "admin_name": admin["name"]})
#     return jsonify({"status": "error", "message": "Invalid credentials.Please try again."}), 401

# # Admin dashboard (only accessible if logged in)
# @app.route('/admin/dashboard')
# def admin_dashboard():
#     if "admin_name" not in session:
#         return redirect(url_for('admin_login_page'))  # Redirect to login page if not logged in
    
#     # Load the location data from the JSON file
#     data = load_locations()

#     # Extract townships and categories
#     townships = list(data.keys())  # Get a list of all townships
#     categories = list({category for township in data.values() for category in township.keys()})  # Get a list of all unique categories

#     return render_template('admin_dashboard.html', townships=townships, categories=categories)

   

# # Logout API
# @app.route('/admin/logout')
# def logout():
#     session.pop("admin_name", None)
#     return redirect(url_for('admin_login_page'))

# # CRUD operations for locations
# @app.route('/admin/locations/<township>/<category>', methods=['GET'])
# def view_locations(township, category):
#     if "admin_name" not in session:
#         return redirect(url_for('admin_login_page'))

#     # Load location data from the JSON file
#     with open(JSON_LOCATIONS_PATH, 'r') as file:
#         data = json.load(file)

#     # Debugging: Print the loaded data to verify it
#     print("Loaded data:", data)

#     # Check if the township exists in the data
#     if township not in data:
#         return jsonify({"status": "error", "message": f"Township '{township}' not found in the data."}), 404

#     # Check if the category exists in the given township
#     if category not in data[township]:
#         return jsonify({"status": "error", "message": f"Category '{category}' not found in township '{township}'."}), 404

#     # Get the locations for the given township and category
#     locations = data[township][category]

#     # Return the view_locations.html template, passing the locations, township, and category
#     return render_template('view_locations.html', locations=locations, township=township, category=category)


# @app.route('/admin/create_location', methods=['POST'])
# def create_location():
#     if "admin_name" not in session:
#         return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403

#     new_location = request.json
#     township = new_location['township']
#     category = new_location['category']
#     name = new_location['name']
#     lat = new_location['lat']
#     lng = new_location['lng']
#     address = new_location['address']

#     data = load_locations()

#     if township not in data:
#         data[township] = {}

#     if category not in data[township]:
#         data[township][category] = []

#     data[township][category].append({
#         'name': name,
#         'lat': lat,
#         'lng': lng,
#         'address':address
#     })

#     with open(JSON_LOCATIONS_PATH, 'w') as file:
#         json.dump(data, file, indent=4)

#     return jsonify({'status': 'success', 'message': 'Location added successfully!'})

# @app.route('/admin/delete_location/<township>/<category>/<name>', methods=['POST'])
# def delete_location(township, category, name):
#     if "admin_name" not in session:
#         return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403

#     data = load_locations()

#     if township in data and category in data[township]:
#         original_length = len(data[township][category])
#         data[township][category] = [loc for loc in data[township][category] if loc['name'] != name]

#         if len(data[township][category]) == original_length:
#             return jsonify({'status': 'error', 'message': 'Location not found!'}), 404

#         # Save updated data
#         with open(JSON_LOCATIONS_PATH, 'w') as file:
#             json.dump(data, file, indent=4)

#         return jsonify({'status': 'success', 'message': 'Location deleted successfully!'})

#     return jsonify({'status': 'error', 'message': 'Invalid Township or Category!'}), 404

# if __name__ == '__main__':
#     app.run(debug=True)


# dijkstra's algorithm and haversine
import os
import json
import heapq
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

JSON_LOCATIONS_PATH = "locations.json"
JSON_ADMINS_PATH = "admins.json"
MANDALAY_UNIVERSITY = "Mandalay University"

MILES_CONVERSION = 0.000621371

# Utility function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def load_locations():
    with open(JSON_LOCATIONS_PATH, "r", encoding="utf-8") as file:
        return json.load(file)

def load_admins():
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

    def format_time(minutes_float):
        total_seconds = int(minutes_float * 60)
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
        motorbike_time = format_time((distance_km / 30) * 60)  # 30 km/h motorbike
        car_time = format_time((distance_km / 45) * 60)         # 45 km/h car

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

@app.route('/admin')
def admin_login_page():
    if "admin_name" in session:
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_login.html')

@app.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    admins = load_admins()
    for admin in admins.values():
        if admin["email"] == email and admin["password"] == password:
            session["admin_name"] = admin["name"]
            return jsonify({"status": "success", "message": "Login Successful", "admin_name": admin["name"]})
    return jsonify({"status": "error", "message": "Invalid credentials. Please try again."}), 401

@app.route('/admin/dashboard')
def admin_dashboard():
    if "admin_name" not in session:
        return redirect(url_for('admin_login_page'))
    admin_name = session["admin_name"]
    data = load_locations()
    townships = list(data.keys())
    categories = list({category for township in data.values() for category in township.keys()})
    return render_template('admin_dashboard.html',admin_name=admin_name ,  townships=townships, categories=categories)

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
    if image_file and allowed_file(image_file.filename):
        filename = secure_filename(image_file.filename)
        image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    else:
        image_path = 'default_image.jpg'  # Use a default image if no file is uploaded

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
    app.run(debug=True)
