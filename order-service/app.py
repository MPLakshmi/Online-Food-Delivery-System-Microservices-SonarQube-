from flask import Flask, request, jsonify
from pymongo import MongoClient
import jwt
import datetime
import requests   # CODE SMELL: Tight coupling via direct HTTP calls
import os

app = Flask(__name__)

# ============================================================
# CODE SMELL: Hardcoded credentials (3rd service with same values)
# CODE SMELL: Hardcoded service URLs (tight coupling)
# ============================================================
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://admin:password123@localhost:27017/")
JWT_SECRET = "mysecretkey123"
DB_NAME = "orderdb"
PAYMENT_SERVICE_URL = os.environ.get("PAYMENT_SERVICE_URL", "http://localhost:5004")
NOTIFICATION_SERVICE_URL = os.environ.get("NOTIFICATION_SERVICE_URL", "http://localhost:5005")
RESTAURANT_SERVICE_URL = os.environ.get("RESTAURANT_SERVICE_URL", "http://localhost:5002")
DELIVERY_FEE = 50
TAX_RATE = 0.18

# ============================================================
# VULNERABILITY: Hardcoded passwords — SonarQube S2068
# ============================================================
DB_PASSWORD = "OrderDB@HardcodedPass#2024"
INTERNAL_SERVICE_PASSWORD = "InternalSvc_P@ssword_hardcoded"
CACHE_PASSWORD = "Redis_Cache@Pass_999_hardcoded"
AUDIT_LOG_PASSWORD = "AuditLog_DB_P@ssword!2024"

# CODE SMELL: Tight coupling — module-level DB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
orders_collection = db["orders"]

# CODE SMELL: Poor naming
o = None
p = []
q = {}


# ============================================================
# CODE SMELL: Extremely long function (100+ lines)
# CODE SMELL: Deeply nested conditions (8 levels)
# CODE SMELL: Multiple responsibilities: validation + calc + DB + HTTP
# CODE SMELL: Tight coupling to payment and notification services
# CODE SMELL: Unused variables
# ============================================================
@app.route('/order/place', methods=['POST'])
def place_order():
    data = request.get_json()
    token = request.headers.get('Authorization')

    # CODE SMELL: Unused variables
    a = 1
    b = 2
    c = 3
    d = 4
    order_flag = False
    payment_done = False
    notification_sent = False
    subtotal_before_tax = 0
    final_amount = 0
    items_count = 0

    if not token:
        return jsonify({"error": "Authorization token required"}), 401

    # CODE SMELL: Duplicate token decoding (5th occurrence across services)
    try:
        decoded = jwt.decode(
            token.replace('Bearer ', ''), JWT_SECRET, algorithms=['HS256']
        )
        user_id = decoded['user_id']
    except:
        return jsonify({"error": "Invalid or expired token"}), 401

    if not data:
        return jsonify({"error": "Request body is required"}), 400

    # CODE SMELL: Deeply nested conditions instead of guard clauses
    if 'restaurant_id' in data:
        if 'items' in data:
            if len(data['items']) > 0:
                if 'payment_method' in data:
                    if data['payment_method'] in ['card', 'upi', 'cod', 'wallet']:
                        if 'delivery_address' in data:
                            if len(data['delivery_address']) > 5:
                                if 'delivery_address' in data and data['delivery_address']:

                                    # Calculate total — should be extracted to helper function
                                    total = 0
                                    for item in data['items']:
                                        if 'price' in item and 'quantity' in item:
                                            if item['quantity'] > 0:
                                                if item['price'] > 0:
                                                    total += item['price'] * item['quantity']

                                    tax = total * TAX_RATE
                                    grand_total = total + tax + DELIVERY_FEE

                                    if grand_total < 100:
                                        return jsonify({"error": "Minimum order is ₹100"}), 400

                                    order = {
                                        "user_id": user_id,
                                        "restaurant_id": data['restaurant_id'],
                                        "items": data['items'],
                                        "subtotal": total,
                                        "tax": tax,
                                        "delivery_fee": DELIVERY_FEE,
                                        "total": grand_total,
                                        "payment_method": data['payment_method'],
                                        "delivery_address": data['delivery_address'],
                                        "status": "pending",
                                        "created_at": datetime.datetime.utcnow()
                                    }

                                    # CODE SMELL: No error handling for DB insert
                                    result = orders_collection.insert_one(order)
                                    order_id = str(result.inserted_id)

                                    # CODE SMELL: Tight coupling — synchronous call to payment service
                                    # Failure here leaves order in inconsistent state
                                    payment_payload = {
                                        "order_id": order_id,
                                        "amount": grand_total,
                                        "payment_method": data['payment_method'],
                                        "user_id": user_id
                                    }
                                    if data['payment_method'] == 'card':
                                        payment_payload['card_number'] = data.get('card_number')
                                        payment_payload['cvv'] = data.get('cvv')
                                        payment_payload['expiry'] = data.get('expiry')
                                    elif data['payment_method'] == 'upi':
                                        payment_payload['upi_id'] = data.get('upi_id')

                                    # CODE SMELL: No timeout set, no retry logic
                                    payment_response = requests.post(
                                        f"{PAYMENT_SERVICE_URL}/process",
                                        json=payment_payload
                                    )

                                    if payment_response.status_code == 200:
                                        # CODE SMELL: No error handling for DB update
                                        orders_collection.update_one(
                                            {"_id": result.inserted_id},
                                            {"$set": {
                                                "status": "confirmed",
                                                "payment_status": "paid"
                                            }}
                                        )

                                        # CODE SMELL: Tight coupling to notification service
                                        # CODE SMELL: No error handling — silent failure
                                        try:
                                            requests.post(
                                                f"{NOTIFICATION_SERVICE_URL}/notify",
                                                json={
                                                    "user_id": user_id,
                                                    "message": f"Your order #{order_id} has been confirmed! Total: ₹{grand_total}",
                                                    "type": "push"
                                                }
                                            )
                                        except:
                                            pass  # CODE SMELL: Silent failure

                                        return jsonify({
                                            "message": "Order placed successfully",
                                            "order_id": order_id,
                                            "subtotal": total,
                                            "tax": tax,
                                            "delivery_fee": DELIVERY_FEE,
                                            "total": grand_total
                                        }), 201
                                    else:
                                        # CODE SMELL: No rollback logic for failed payment
                                        orders_collection.update_one(
                                            {"_id": result.inserted_id},
                                            {"$set": {"status": "payment_failed"}}
                                        )
                                        return jsonify({"error": "Payment processing failed"}), 400
                                else:
                                    return jsonify({"error": "Delivery address cannot be empty"}), 400
                            else:
                                return jsonify({"error": "Please provide a complete delivery address"}), 400
                        else:
                            return jsonify({"error": "Delivery address is required"}), 400
                    else:
                        return jsonify({"error": "Invalid payment method"}), 400
                else:
                    return jsonify({"error": "Payment method is required"}), 400
            else:
                return jsonify({"error": "Order must contain at least one item"}), 400
        else:
            return jsonify({"error": "Items list is required"}), 400
    else:
        return jsonify({"error": "Restaurant ID is required"}), 400


# ============================================================
# CODE SMELL: No authentication check — anyone can view any order
# ============================================================
@app.route('/order/<order_id>', methods=['GET'])
def get_order(order_id):
    from bson import ObjectId
    # CODE SMELL: No error handling for ObjectId or DB call
    order = orders_collection.find_one({"_id": ObjectId(order_id)})

    if not order:
        return jsonify({"error": "Order not found"}), 404

    return jsonify({
        "order_id": str(order['_id']),
        "user_id": order['user_id'],
        "status": order['status'],
        "total": order['total'],
        "subtotal": order.get('subtotal', 0),
        "tax": order.get('tax', 0),
        "items": order['items'],
        "delivery_address": order.get('delivery_address', ''),
        "created_at": str(order['created_at'])
    }), 200


# ============================================================
# CODE SMELL: Duplicate pattern — same list+map as get_restaurants
# CODE SMELL: Unused variables
# ============================================================
@app.route('/orders/user/<user_id>', methods=['GET'])
def get_user_orders(user_id):
    # CODE SMELL: Unused variables
    orders_list = []
    count = 0
    total_spent = 0

    # CODE SMELL: No error handling
    orders = list(orders_collection.find({"user_id": user_id}))

    result = []
    for order in orders:
        result.append({
            "order_id": str(order['_id']),
            "restaurant_id": order.get('restaurant_id', ''),
            "status": order['status'],
            "total": order['total'],
            "items_count": len(order.get('items', [])),
            "created_at": str(order['created_at'])
        })

    return jsonify(result), 200


@app.route('/order/cancel/<order_id>', methods=['PUT'])
def cancel_order(order_id):
    token = request.headers.get('Authorization')

    # CODE SMELL: Unused variables
    cancelled = False
    refund_initiated = False

    if not token:
        return jsonify({"error": "Authorization required"}), 401

    # CODE SMELL: Duplicate token decoding (6th occurrence)
    try:
        decoded = jwt.decode(
            token.replace('Bearer ', ''), JWT_SECRET, algorithms=['HS256']
        )
        user_id = decoded['user_id']
    except:
        return jsonify({"error": "Invalid token"}), 401

    from bson import ObjectId
    # CODE SMELL: No error handling
    order = orders_collection.find_one({"_id": ObjectId(order_id)})

    if not order:
        return jsonify({"error": "Order not found"}), 404

    if order['user_id'] != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    if order['status'] not in ['pending', 'confirmed']:
        return jsonify({"error": "Order cannot be cancelled"}), 400

    # CODE SMELL: No error handling for update
    orders_collection.update_one(
        {"_id": ObjectId(order_id)},
        {"$set": {"status": "cancelled"}}
    )

    # CODE SMELL: Tight coupling — direct HTTP call for refund
    if order.get('payment_status') == 'paid':
        try:
            requests.post(f"{PAYMENT_SERVICE_URL}/refund", json={
                "order_id": order_id,
                "amount": order['total']
            })
        except:
            pass  # CODE SMELL: Silent failure on refund

    return jsonify({"message": "Order cancelled successfully"}), 200


if __name__ == '__main__':
    # CODE SMELL: debug=True in production
    app.run(host='0.0.0.0', port=5003, debug=True)
