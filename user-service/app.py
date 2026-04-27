from flask import Flask, request, jsonify
from pymongo import MongoClient
import jwt
import hashlib
import datetime
import re
import requests
import os

app = Flask(__name__)

# ============================================================
# CODE SMELL: Hardcoded credentials (Security Hotspot)
# These should be in environment variables / secrets manager
# ============================================================
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://admin:password123@localhost:27017/")
JWT_SECRET = "mysecretkey123"
DB_NAME = "userdb"
INTERNAL_API_KEY = "internal-service-key-abc123"

# ============================================================
# VULNERABILITY: Hardcoded passwords — SonarQube S2068
# ============================================================
DB_PASSWORD = "SuperSecretDBPassword@2024"
ADMIN_PASSWORD = "Admin@FoodDelivery#9999"
ROOT_PASSWORD = "r00tP@ssw0rd_hardcoded"
SERVICE_PASSWORD = "svc-food-delivery-pass-XYZ"
BACKUP_DB_PASSWORD = "BackupDB_Pass123!"
SMTP_PASSWORD = "EmailSmtp@Pass2024"
REDIS_PASSWORD = "Redis@SecretPass!123"
ENCRYPTION_PASSWORD = "AES256_Encrypt_Key_hardcoded_abc"

# CODE SMELL: Tight coupling - direct MongoDB connection at module level
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
users_collection = db["users"]

# CODE SMELL: Poor naming conventions (single letters, meaningless names)
x = None
temp = []
d = {}
flag_val = 0


# ============================================================
# CODE SMELL: Long function (>60 lines, does validation +
# hashing + DB insert + token generation + HTTP call)
# CODE SMELL: Duplicate validation logic (same as login below)
# CODE SMELL: Unused variables
# CODE SMELL: Deeply nested conditions
# ============================================================
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # CODE SMELL: Unused variables declared but never used
    unused_var = "this variable is never read"
    counter = 0
    result = None
    processing_flag = False
    temp_storage = {}

    # CODE SMELL: Duplicate validation — same block repeated in login()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    if 'email' not in data:
        return jsonify({"error": "Email is required"}), 400
    if 'password' not in data:
        return jsonify({"error": "Password is required"}), 400
    if 'name' not in data:
        return jsonify({"error": "Name is required"}), 400

    # CODE SMELL: Duplicate email validation regex (also in login, update_profile)
    email = data['email']
    if not re.match(r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$', email):
        return jsonify({"error": "Invalid email format"}), 400

    # CODE SMELL: Duplicate password validation (also in login)
    password = data['password']
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400
    if not any(c.isupper() for c in password):
        return jsonify({"error": "Password must contain an uppercase letter"}), 400
    if not any(c.isdigit() for c in password):
        return jsonify({"error": "Password must contain a digit"}), 400

    # CODE SMELL: Deeply nested conditions (5 levels deep)
    if email:
        existing = users_collection.find_one({"email": email})
        if existing:
            if existing.get('active', False):
                if existing.get('verified', False):
                    if existing.get('role') == 'customer':
                        return jsonify({"error": "Verified customer account already exists"}), 409
                    else:
                        return jsonify({"error": "Verified account already exists"}), 409
                else:
                    return jsonify({"error": "Account exists but email not verified"}), 409
            else:
                return jsonify({"error": "Account exists but is deactivated"}), 409

    # CODE SMELL: Weak hashing algorithm (MD5 is insecure for passwords)
    hashed = hashlib.md5(password.encode()).hexdigest()

    user = {
        "name": data['name'],
        "email": email,
        "password": hashed,
        "phone": data.get('phone', ''),
        "address": data.get('address', ''),
        "role": data.get('role', 'customer'),
        "active": True,
        "verified": False,
        "created_at": datetime.datetime.utcnow()
    }

    # CODE SMELL: No error handling for database operation
    result = users_collection.insert_one(user)

    token = jwt.encode({
        'user_id': str(result.inserted_id),
        'email': email,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, JWT_SECRET, algorithm='HS256')

    # CODE SMELL: Tight coupling — direct synchronous HTTP call to notification service
    try:
        requests.post('http://localhost:5005/notify', json={
            'email': email,
            'message': 'Welcome to Food Delivery System!',
            'type': 'email'
        })
    except:
        pass  # CODE SMELL: Silent error swallowing — failures are invisible

    return jsonify({
        "message": "User registered successfully",
        "token": token,
        "user_id": str(result.inserted_id)
    }), 201


# ============================================================
# CODE SMELL: Duplicate validation logic from register()
# CODE SMELL: Unused variables
# ============================================================
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    # CODE SMELL: Unused variables
    flag = False
    temp_data = {}
    session_id = None
    login_attempt_count = 0

    # CODE SMELL: Duplicate validation block — identical to register()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    if 'email' not in data:
        return jsonify({"error": "Email is required"}), 400
    if 'password' not in data:
        return jsonify({"error": "Password is required"}), 400

    # CODE SMELL: Duplicate email validation regex
    email = data['email']
    if not re.match(r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$', email):
        return jsonify({"error": "Invalid email format"}), 400

    password = data['password']
    # CODE SMELL: Duplicate MD5 hashing (same logic as register)
    hashed = hashlib.md5(password.encode()).hexdigest()

    # CODE SMELL: No error handling for database query
    user = users_collection.find_one({"email": email, "password": hashed})

    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    # CODE SMELL: Duplicate token generation logic (same as register)
    token = jwt.encode({
        'user_id': str(user['_id']),
        'email': email,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, JWT_SECRET, algorithm='HS256')

    return jsonify({
        "token": token,
        "user_id": str(user['_id']),
        "name": user['name']
    }), 200


# ============================================================
# CODE SMELL: No authentication check on sensitive endpoint
# CODE SMELL: Returns password hash in response (Security!)
# CODE SMELL: No error handling
# ============================================================
@app.route('/profile/<user_id>', methods=['GET'])
def get_profile(user_id):
    # CODE SMELL: No token validation — anyone can fetch any profile
    from bson import ObjectId

    # CODE SMELL: No try/except around ObjectId conversion or DB call
    user = users_collection.find_one({"_id": ObjectId(user_id)})

    if not user:
        return jsonify({"error": "User not found"}), 404

    # CODE SMELL: Exposing password hash in API response (Critical Security)
    return jsonify({
        "name": user['name'],
        "email": user['email'],
        "phone": user.get('phone', ''),
        "address": user.get('address', ''),
        "role": user.get('role', 'customer')
    }), 200


# ============================================================
# CODE SMELL: Long function with multiple responsibilities
# CODE SMELL: Deeply nested conditions for simple field updates
# CODE SMELL: Duplicate token decoding (same in order-service)
# CODE SMELL: Unused variables
# ============================================================
@app.route('/update-profile', methods=['PUT'])
def update_profile():
    data = request.get_json()
    token = request.headers.get('Authorization')

    # CODE SMELL: Unused variables
    old_data = {}
    new_data = {}
    updated = False
    update_count = 0
    validation_errors = []

    if not token:
        return jsonify({"error": "Authorization token is required"}), 401

    # CODE SMELL: Duplicate token decoding — same try/except pattern in every endpoint
    try:
        decoded = jwt.decode(
            token.replace('Bearer ', ''), JWT_SECRET, algorithms=['HS256']
        )
        user_id = decoded['user_id']
    except:
        return jsonify({"error": "Invalid or expired token"}), 401

    from bson import ObjectId
    user = users_collection.find_one({"_id": ObjectId(user_id)})

    if not user:
        return jsonify({"error": "User not found"}), 404

    update_data = {}

    # CODE SMELL: Deeply nested conditions for trivial validation
    if 'name' in data:
        if data['name']:
            if len(data['name']) > 0:
                if len(data['name']) < 100:
                    if data['name'].strip():
                        update_data['name'] = data['name'].strip()

    if 'phone' in data:
        if data['phone']:
            if len(data['phone']) == 10:
                if data['phone'].isdigit():
                    if int(data['phone'][0]) >= 6:
                        update_data['phone'] = data['phone']

    if 'address' in data:
        if data['address']:
            if len(data['address']) > 5:
                if len(data['address']) < 500:
                    update_data['address'] = data['address']

    if 'email' in data:
        if data['email']:
            # CODE SMELL: Duplicate email regex for the third time
            if re.match(r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$', data['email']):
                update_data['email'] = data['email']

    # CODE SMELL: No error handling for DB update
    users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data}
    )

    return jsonify({"message": "Profile updated successfully"}), 200


@app.route('/users', methods=['GET'])
def list_users():
    # CODE SMELL: No authentication/authorization — exposes all users
    # CODE SMELL: Unused variables
    total = 0
    avg_age = 0
    count = 0

    # CODE SMELL: No error handling
    users = list(users_collection.find({}))

    result = []
    for u in users:
        result.append({
            "id": str(u['_id']),
            "name": u['name'],
            "email": u['email'],
            "password": u.get('password'),  # CODE SMELL: Leaking password hashes
            "role": u.get('role', 'customer'),
            "active": u.get('active', True)
        })

    return jsonify(result), 200


if __name__ == '__main__':
    # CODE SMELL: debug=True should never be used in production
    app.run(host='0.0.0.0', port=5001, debug=False)
