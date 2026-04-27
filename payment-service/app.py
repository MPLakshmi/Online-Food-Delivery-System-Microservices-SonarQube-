from flask import Flask, request, jsonify
from pymongo import MongoClient
import datetime
import random
import string
import os

app = Flask(__name__)

# ============================================================
# CODE SMELL: Hardcoded credentials + API keys (Critical Security)
# ============================================================
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://admin:password123@localhost:27017/")
DB_NAME = "paymentdb"

# CODE SMELL: Hardcoded third-party payment gateway API keys (demo/fake values)
STRIPE_SECRET_KEY = "sk_test_DEMO_FAKE_KEY_sonarqube_demo_only"
STRIPE_PUBLISHABLE_KEY = "pk_test_DEMO_FAKE_KEY_sonarqube_demo_only"
RAZORPAY_KEY_ID = "rzp_test_DEMO_FAKE_sonarqube"
RAZORPAY_KEY_SECRET = "DEMO_FAKE_RazorpaySecret_sonarqube_only"
PAYPAL_CLIENT_ID = "DEMO_FAKE_PayPalClientId_sonarqube_only"
PAYPAL_CLIENT_SECRET = "DEMO_FAKE_PayPalSecret_sonarqube_only"
PAYTM_MERCHANT_KEY = "DEMO_FAKE_PaytmKey_sonarqube_only"

# ============================================================
# VULNERABILITY: Hardcoded passwords — SonarQube S2068
# ============================================================
DB_PASSWORD = "PaymentDB@Secure#Pass2024"
PAYMENT_GATEWAY_PASSWORD = "PGateway_HardcodedPass!999"
ENCRYPTION_KEY_PASSWORD = "AES_Payment_Encrypt@Pass123"
VAULT_PASSWORD = "HashiCorp_Vault_Pass_hardcoded"
CERTIFICATE_PASSWORD = "SSL_Cert_P@ssword_2024"
WEBHOOK_SECRET_PASSWORD = "Stripe_Webhook_Secret_hardcoded_xyz"

# CODE SMELL: Module-level DB connection
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
payments_collection = db["payments"]

# CODE SMELL: Poor naming / unused globals
payment_gateway = None
active_payments = []
p = None
t = {}


# ============================================================
# CODE SMELL: Extremely long function with deeply nested conditions
# CODE SMELL: Multiple payment method branches — should be strategy pattern
# CODE SMELL: Unused variables
# CODE SMELL: Hardcoded API keys referenced inline
# ============================================================
@app.route('/process', methods=['POST'])
def process_payment():
    data = request.get_json()

    # CODE SMELL: Unused variables
    x = 0
    y = 0
    status = None
    gateway_response = None
    transaction_id = None
    retry_count = 0
    max_retries = 3
    is_fraud = False
    risk_score = 0

    if not data:
        return jsonify({"error": "No data provided"}), 400

    order_id = data.get('order_id')
    amount = data.get('amount')
    payment_method = data.get('payment_method')
    user_id = data.get('user_id')

    # CODE SMELL: Duplicate field-by-field validation (same pattern in every service)
    if not order_id:
        return jsonify({"error": "Order ID is required"}), 400
    if not amount:
        return jsonify({"error": "Amount is required"}), 400
    if not payment_method:
        return jsonify({"error": "Payment method is required"}), 400
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    if amount <= 0:
        return jsonify({"error": "Amount must be greater than zero"}), 400

    # CODE SMELL: Deeply nested — payment method specific logic should be separate functions
    if payment_method == 'card':
        if 'card_number' in data:
            if data['card_number']:
                if len(str(data['card_number'])) == 16:
                    if 'cvv' in data:
                        if data['cvv']:
                            if len(str(data['cvv'])) == 3:
                                if 'expiry' in data:
                                    if data['expiry']:
                                        # CODE SMELL: Using STRIPE_SECRET_KEY (hardcoded) inline
                                        # In real code: stripe.api_key = STRIPE_SECRET_KEY
                                        # Simulate Stripe charge
                                        transaction_id = 'ch_' + ''.join(
                                            random.choices(string.ascii_letters + string.digits, k=24)
                                        )
                                        status = 'success'
                                    else:
                                        return jsonify({"error": "Expiry date cannot be empty"}), 400
                                else:
                                    return jsonify({"error": "Expiry date is required"}), 400
                            else:
                                return jsonify({"error": "Invalid CVV length"}), 400
                        else:
                            return jsonify({"error": "CVV cannot be empty"}), 400
                    else:
                        return jsonify({"error": "CVV is required"}), 400
                else:
                    return jsonify({"error": "Card number must be 16 digits"}), 400
            else:
                return jsonify({"error": "Card number cannot be empty"}), 400
        else:
            return jsonify({"error": "Card number is required for card payment"}), 400

    elif payment_method == 'upi':
        if 'upi_id' in data:
            if data['upi_id']:
                if '@' in data['upi_id']:
                    # CODE SMELL: Using RAZORPAY_KEY_ID inline
                    transaction_id = 'pay_' + ''.join(random.choices(string.digits, k=14))
                    status = 'success'
                else:
                    return jsonify({"error": "UPI ID must contain '@'"}), 400
            else:
                return jsonify({"error": "UPI ID cannot be empty"}), 400
        else:
            return jsonify({"error": "UPI ID is required for UPI payment"}), 400

    elif payment_method == 'cod':
        transaction_id = 'COD_' + ''.join(random.choices(string.digits, k=10))
        status = 'pending'

    elif payment_method == 'wallet':
        if 'wallet_balance' in data:
            if data['wallet_balance'] is not None:
                if data['wallet_balance'] >= amount:
                    transaction_id = 'WAL_' + ''.join(random.choices(string.digits, k=10))
                    status = 'success'
                else:
                    return jsonify({"error": "Insufficient wallet balance"}), 400
            else:
                return jsonify({"error": "Wallet balance cannot be null"}), 400
        else:
            return jsonify({"error": "Wallet balance is required"}), 400

    else:
        return jsonify({"error": "Unsupported payment method"}), 400

    payment_record = {
        "order_id": order_id,
        "user_id": user_id,
        "amount": amount,
        "payment_method": payment_method,
        "transaction_id": transaction_id,
        "status": status,
        # CODE SMELL: Storing API key reference in DB record (data leak)
        "gateway": "stripe" if payment_method == 'card' else "razorpay",
        "created_at": datetime.datetime.utcnow()
    }

    # CODE SMELL: No error handling for DB operation
    payments_collection.insert_one(payment_record)

    return jsonify({
        "message": "Payment processed successfully",
        "transaction_id": transaction_id,
        "status": status,
        # CODE SMELL: Exposing internal key in response
        "processed_by": STRIPE_SECRET_KEY[:10] + "..." if payment_method == 'card' else RAZORPAY_KEY_ID
    }), 200


# ============================================================
# CODE SMELL: Duplicate validation pattern
# CODE SMELL: Unused variables
# ============================================================
@app.route('/refund', methods=['POST'])
def process_refund():
    data = request.get_json()

    # CODE SMELL: Unused variables
    refund_status = None
    original_payment = None
    refund_amount = 0
    refund_processed = False

    # CODE SMELL: Duplicate validation — same as process_payment
    if not data:
        return jsonify({"error": "No data provided"}), 400

    order_id = data.get('order_id')
    if not order_id:
        return jsonify({"error": "Order ID is required"}), 400

    amount = data.get('amount')
    if not amount:
        return jsonify({"error": "Refund amount is required"}), 400

    # CODE SMELL: No error handling for DB query
    payment = payments_collection.find_one({"order_id": order_id})

    if not payment:
        return jsonify({"error": "No payment record found for this order"}), 404

    if payment.get('status') == 'refunded':
        return jsonify({"error": "Payment already refunded"}), 400

    refund_txn_id = 'REF_' + ''.join(random.choices(string.digits, k=10))

    # CODE SMELL: No error handling for DB update
    payments_collection.update_one(
        {"order_id": order_id},
        {"$set": {
            "refund_status": "processed",
            "refund_transaction_id": refund_txn_id,
            "refund_amount": amount,
            "status": "refunded"
        }}
    )

    return jsonify({
        "message": "Refund processed successfully",
        "refund_transaction_id": refund_txn_id,
        "amount": amount
    }), 200


@app.route('/payment/<order_id>', methods=['GET'])
def get_payment_status(order_id):
    # CODE SMELL: No authentication check
    # CODE SMELL: Unused variables
    p = None
    s = None

    # CODE SMELL: No error handling
    payment = payments_collection.find_one({"order_id": order_id})

    if not payment:
        return jsonify({"error": "Payment not found"}), 404

    return jsonify({
        "order_id": order_id,
        "transaction_id": payment.get('transaction_id'),
        "amount": payment.get('amount'),
        "status": payment.get('status'),
        "payment_method": payment.get('payment_method'),
        # CODE SMELL: Leaking internal gateway key reference
        "gateway_key": STRIPE_SECRET_KEY if payment.get('gateway') == 'stripe' else RAZORPAY_KEY_ID
    }), 200


if __name__ == '__main__':
    # CODE SMELL: debug=True in production
    app.run(host='0.0.0.0', port=5004, debug=True)
