from flask import Flask, request, jsonify
from pymongo import MongoClient
import jwt
import datetime
import re
import os

app = Flask(__name__)

# ============================================================
# CODE SMELL: Hardcoded credentials — identical to user-service
# (Duplicate hardcoded secrets across multiple files)
# ============================================================
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://admin:password123@localhost:27017/")
JWT_SECRET = "mysecretkey123"      # Same secret as user-service
DB_NAME = "restaurantdb"
ADMIN_API_KEY = "restaurant-admin-key-xyz789"

# ============================================================
# VULNERABILITY: Hardcoded passwords — SonarQube S2068
# ============================================================
DB_PASSWORD = "RestaurantDB@Pass#Hardcoded2024"
ADMIN_PASSWORD = "RestAdmin@SuperSecret#999"
IMAGE_STORAGE_PASSWORD = "S3_Bucket_P@ssword_hardcoded_xyz"
CDN_SECRET_PASSWORD = "CDN_Secret_P@ss_NeverCommit!"
SEARCH_ENGINE_PASSWORD = "Elasticsearch_P@ss_2024_hardcoded"

# CODE SMELL: Tight coupling — module-level DB connection
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
restaurants_collection = db["restaurants"]
menus_collection = db["menus"]

# CODE SMELL: Poor naming conventions
r = None
m = []
tmp = {}
n = 0


# ============================================================
# CODE SMELL: Unused variables
# CODE SMELL: No error handling
# ============================================================
@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    # CODE SMELL: Unused variables
    count = 0
    total = 0
    avg_rating = 0
    page = 1
    per_page = 10

    # CODE SMELL: No error handling around DB call
    restaurants = list(restaurants_collection.find({}))

    result = []
    for r in restaurants:
        result.append({
            "id": str(r['_id']),
            "name": r['name'],
            "cuisine": r.get('cuisine', ''),
            "rating": r.get('rating', 0),
            "address": r.get('address', ''),
            "active": r.get('active', True),
            "opening_time": r.get('opening_time', '09:00'),
            "closing_time": r.get('closing_time', '22:00')
        })

    return jsonify(result), 200


# ============================================================
# CODE SMELL: Long function — validation + auth + DB all mixed
# CODE SMELL: Duplicate validation from user-service
# CODE SMELL: Unused variables
# ============================================================
@app.route('/restaurant/add', methods=['POST'])
def add_restaurant():
    data = request.get_json()

    # CODE SMELL: Unused variables
    unused1 = "this is never used"
    unused2 = 0
    unused3 = []
    temp_restaurant = {}
    validation_passed = False

    # CODE SMELL: Duplicate validation — identical to user-service register()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    if 'name' not in data:
        return jsonify({"error": "Name is required"}), 400
    if 'email' not in data:
        return jsonify({"error": "Email is required"}), 400

    # CODE SMELL: Duplicate email validation regex (3rd copy in codebase)
    email = data['email']
    if not re.match(r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$', email):
        return jsonify({"error": "Invalid email format"}), 400

    # CODE SMELL: Duplicate password validation (same as user-service)
    if 'password' in data:
        password = data['password']
        if len(password) < 8:
            return jsonify({"error": "Password must be at least 8 characters"}), 400
        if not any(c.isupper() for c in password):
            return jsonify({"error": "Password must contain an uppercase letter"}), 400
        if not any(c.isdigit() for c in password):
            return jsonify({"error": "Password must contain a digit"}), 400

    restaurant = {
        "name": data['name'],
        "email": email,
        "cuisine": data.get('cuisine', 'Various'),
        "address": data.get('address', ''),
        "phone": data.get('phone', ''),
        "rating": 0,
        "active": True,
        "opening_time": data.get('opening_time', '09:00'),
        "closing_time": data.get('closing_time', '22:00'),
        "delivery_radius": data.get('delivery_radius', 5),
        "minimum_order": data.get('minimum_order', 100),
        "created_at": datetime.datetime.utcnow()
    }

    # CODE SMELL: No error handling for DB insert
    result = restaurants_collection.insert_one(restaurant)

    return jsonify({
        "message": "Restaurant added successfully",
        "restaurant_id": str(result.inserted_id)
    }), 201


# ============================================================
# CODE SMELL: Deeply nested conditions (7+ levels)
# CODE SMELL: Entire logic inside nested ifs instead of early returns
# CODE SMELL: Duplicate token decoding
# CODE SMELL: Unused variables
# ============================================================
@app.route('/menu/add', methods=['POST'])
def add_menu_item():
    data = request.get_json()
    token = request.headers.get('Authorization')

    # CODE SMELL: Unused variables
    x = 0
    y = 0
    z = 0
    temp_item = {}
    item_validated = False
    price_validated = False

    if not token:
        return jsonify({"error": "Authorization required"}), 401

    # CODE SMELL: Duplicate token decoding — same pattern across all services
    try:
        decoded = jwt.decode(
            token.replace('Bearer ', ''), JWT_SECRET, algorithms=['HS256']
        )
    except:
        # CODE SMELL: Bare except swallows all exceptions
        return jsonify({"error": "Invalid token"}), 401

    if not data:
        return jsonify({"error": "Request body is required"}), 400

    # CODE SMELL: Deeply nested conditions — should use early returns
    if 'restaurant_id' in data:
        if data['restaurant_id']:
            if 'name' in data:
                if data['name']:
                    if 'price' in data:
                        if data['price'] > 0:
                            if 'category' in data:
                                if data['category']:
                                    if 'description' in data:
                                        menu_item = {
                                            "restaurant_id": data['restaurant_id'],
                                            "name": data['name'],
                                            "description": data.get('description', ''),
                                            "price": data['price'],
                                            "category": data['category'],
                                            "available": True,
                                            "preparation_time": data.get('preparation_time', 30),
                                            "image_url": data.get('image_url', ''),
                                            "is_vegetarian": data.get('is_vegetarian', False),
                                            "spice_level": data.get('spice_level', 'mild'),
                                            "created_at": datetime.datetime.utcnow()
                                        }
                                        # CODE SMELL: No error handling
                                        result = menus_collection.insert_one(menu_item)
                                        return jsonify({
                                            "message": "Menu item added",
                                            "item_id": str(result.inserted_id)
                                        }), 201
                                    else:
                                        return jsonify({"error": "Description is required"}), 400
                                else:
                                    return jsonify({"error": "Category cannot be empty"}), 400
                            else:
                                return jsonify({"error": "Category is required"}), 400
                        else:
                            return jsonify({"error": "Price must be greater than zero"}), 400
                    else:
                        return jsonify({"error": "Price is required"}), 400
                else:
                    return jsonify({"error": "Item name cannot be empty"}), 400
            else:
                return jsonify({"error": "Item name is required"}), 400
        else:
            return jsonify({"error": "Restaurant ID cannot be empty"}), 400
    else:
        return jsonify({"error": "Restaurant ID is required"}), 400


@app.route('/menu/<restaurant_id>', methods=['GET'])
def get_menu(restaurant_id):
    # CODE SMELL: No error handling
    # CODE SMELL: Unused variables
    total_items = 0
    available_count = 0

    items = list(menus_collection.find({"restaurant_id": restaurant_id}))

    result = []
    for item in items:
        result.append({
            "id": str(item['_id']),
            "name": item['name'],
            "price": item['price'],
            "category": item['category'],
            "description": item.get('description', ''),
            "available": item.get('available', True),
            "preparation_time": item.get('preparation_time', 30),
            "is_vegetarian": item.get('is_vegetarian', False)
        })

    return jsonify(result), 200


@app.route('/restaurant/<restaurant_id>', methods=['GET'])
def get_restaurant(restaurant_id):
    from bson import ObjectId
    # CODE SMELL: No error handling for ObjectId conversion
    restaurant = restaurants_collection.find_one({"_id": ObjectId(restaurant_id)})

    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404

    return jsonify({
        "id": str(restaurant['_id']),
        "name": restaurant['name'],
        "cuisine": restaurant.get('cuisine', ''),
        "rating": restaurant.get('rating', 0),
        "address": restaurant.get('address', ''),
        "phone": restaurant.get('phone', ''),
        "opening_time": restaurant.get('opening_time', '09:00'),
        "closing_time": restaurant.get('closing_time', '22:00'),
        "minimum_order": restaurant.get('minimum_order', 100)
    }), 200


@app.route('/menu/update/<item_id>', methods=['PUT'])
def update_menu_item(item_id):
    data = request.get_json()
    token = request.headers.get('Authorization')

    # CODE SMELL: Unused variables
    old_price = 0
    new_price = 0
    price_changed = False

    if not token:
        return jsonify({"error": "Authorization required"}), 401

    # CODE SMELL: Duplicate token decoding (4th occurrence across services)
    try:
        decoded = jwt.decode(
            token.replace('Bearer ', ''), JWT_SECRET, algorithms=['HS256']
        )
    except:
        return jsonify({"error": "Invalid token"}), 401

    from bson import ObjectId
    update_data = {}

    if 'price' in data:
        update_data['price'] = data['price']
    if 'available' in data:
        update_data['available'] = data['available']
    if 'description' in data:
        update_data['description'] = data['description']

    # CODE SMELL: No error handling
    menus_collection.update_one(
        {"_id": ObjectId(item_id)},
        {"$set": update_data}
    )

    return jsonify({"message": "Menu item updated"}), 200


if __name__ == '__main__':
    # CODE SMELL: debug=True in production
    app.run(host='0.0.0.0', port=5002, debug=True)
