from flask import Flask, request, jsonify
from pymongo import MongoClient
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime
import requests   # CODE SMELL: Tight coupling via HTTP
import os

app = Flask(__name__)

# ============================================================
# CODE SMELL: Hardcoded credentials — email + SMS + push keys
# ============================================================
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://admin:password123@localhost:27017/")
DB_NAME = "notificationdb"

# CODE SMELL: Hardcoded email credentials
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USER = "fooddeliveryapp@gmail.com"
EMAIL_PASSWORD = "MyHardcodedEmailPassword@2024"    # Critical security issue

# ============================================================
# VULNERABILITY: Hardcoded passwords — SonarQube S2068
# ============================================================


# CODE SMELL: Hardcoded SMS gateway API key
SMS_API_KEY = "LIVE_SMS_KEY_abc123xyz789_HARDCODED"
SMS_SENDER_ID = "FOODDL"

# CODE SMELL: Hardcoded Firebase/Push notification key
FIREBASE_SERVER_KEY = "AAAABCDEFGHijklmnop:APA91bHardcodedFirebaseKey_NeverDoThis"
FIREBASE_PROJECT_ID = "food-delivery-prod-12345"

# CODE SMELL: Module-level DB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
notifications_collection = db["notifications"]

# CODE SMELL: Unused globals with poor names
notification_queue = []
failed_notifications = []
x = None
y = None


# ============================================================
# CODE SMELL: Long function with deeply nested conditions
# CODE SMELL: All notification types in single function (no SRP)
# CODE SMELL: Unused variables
# CODE SMELL: Exposing API keys in responses
# ============================================================
@app.route('/notify', methods=['POST'])
def send_notification():
    data = request.get_json()

    # CODE SMELL: Unused variables
    x = None
    y = None
    temp = {}
    count = 0
    attempt = 0
    max_attempt = 3
    notification_id = None

    if not data:
        return jsonify({"error": "No data provided"}), 400

    notification_type = data.get('type', 'email')
    user_id = data.get('user_id', '')
    message = data.get('message', '')
    email = data.get('email', '')
    subject = data.get('subject', 'Food Delivery Notification')

    # CODE SMELL: Deeply nested — should use strategy/factory pattern
    if notification_type == 'email':
        if email:
            if message:
                if subject:
                    if EMAIL_USER and EMAIL_PASSWORD:
                        # CODE SMELL: Sending email with hardcoded credentials
                        try:
                            msg = MIMEMultipart('alternative')
                            msg['Subject'] = subject
                            msg['From'] = EMAIL_USER
                            msg['To'] = email

                            text_part = MIMEText(message, 'plain')
                            html_part = MIMEText(
                                f"<html><body><p>{message}</p></body></html>", 'html'
                            )
                            msg.attach(text_part)
                            msg.attach(html_part)

                            # CODE SMELL: Using hardcoded EMAIL_PASSWORD
                            server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
                            server.ehlo()
                            server.starttls()
                            server.login(EMAIL_USER, EMAIL_PASSWORD)
                            server.sendmail(EMAIL_USER, email, msg.as_string())
                            server.quit()

                            # CODE SMELL: Duplicate DB insert pattern (repeated below for SMS/push)
                            notifications_collection.insert_one({
                                "type": "email",
                                "recipient": email,
                                "subject": subject,
                                "message": message,
                                "status": "sent",
                                "created_at": datetime.datetime.utcnow()
                            })

                            return jsonify({"message": "Email notification sent"}), 200

                        except Exception as e:
                            # CODE SMELL: Poor error handling — printing raw exception
                            print("Email sending error: " + str(e))
                            # CODE SMELL: Duplicate DB insert for failure case
                            notifications_collection.insert_one({
                                "type": "email",
                                "recipient": email,
                                "message": message,
                                "status": "failed",
                                "error": str(e),
                                "created_at": datetime.datetime.utcnow()
                            })
                            return jsonify({"error": "Failed to send email notification"}), 500
                    else:
                        return jsonify({"error": "Email configuration is missing"}), 500
                else:
                    return jsonify({"error": "Email subject is required"}), 400
            else:
                return jsonify({"error": "Notification message is required"}), 400
        else:
            return jsonify({"error": "Recipient email is required"}), 400

    elif notification_type == 'sms':
        if 'phone' in data:
            if data['phone']:
                if len(data['phone']) == 10:
                    if data['phone'].isdigit():
                        if message:
                            # CODE SMELL: Using SMS_API_KEY (hardcoded) to make API call
                            sms_payload = {
                                "api_key": SMS_API_KEY,   # Hardcoded key in payload
                                "sender": SMS_SENDER_ID,
                                "to": data['phone'],
                                "message": message
                            }

                            # Simulate SMS send (real call commented for demo)
                            # response = requests.post("https://sms-provider.com/send", json=sms_payload)

                            # CODE SMELL: Duplicate DB insert pattern (3rd time)
                            notifications_collection.insert_one({
                                "type": "sms",
                                "recipient": data['phone'],
                                "message": message,
                                "status": "sent",
                                # CODE SMELL: Logging API key in DB record
                                "api_key_used": SMS_API_KEY,
                                "created_at": datetime.datetime.utcnow()
                            })

                            return jsonify({
                                "message": "SMS notification sent",
                                # CODE SMELL: Exposing API key in HTTP response
                                "debug_info": {"api_key": SMS_API_KEY, "sender": SMS_SENDER_ID}
                            }), 200
                        else:
                            return jsonify({"error": "SMS message cannot be empty"}), 400
                    else:
                        return jsonify({"error": "Phone number must contain only digits"}), 400
                else:
                    return jsonify({"error": "Phone number must be 10 digits"}), 400
            else:
                return jsonify({"error": "Phone number cannot be empty"}), 400
        else:
            return jsonify({"error": "Phone number is required for SMS"}), 400

    elif notification_type == 'push':
        if user_id:
            if message:
                # CODE SMELL: Using FIREBASE_SERVER_KEY (hardcoded)
                push_payload = {
                    "to": f"/topics/user_{user_id}",
                    "notification": {
                        "title": "Food Delivery Update",
                        "body": message
                    },
                    "data": {
                        "user_id": user_id,
                        "timestamp": str(datetime.datetime.utcnow())
                    }
                }

                # Simulate push notification send
                # requests.post(
                #     "https://fcm.googleapis.com/fcm/send",
                #     headers={"Authorization": f"key={FIREBASE_SERVER_KEY}"},
                #     json=push_payload
                # )

                # CODE SMELL: Duplicate DB insert (4th time — same structure)
                notifications_collection.insert_one({
                    "type": "push",
                    "recipient": user_id,
                    "message": message,
                    "status": "sent",
                    "firebase_key": FIREBASE_SERVER_KEY,   # Storing key in DB
                    "created_at": datetime.datetime.utcnow()
                })

                return jsonify({
                    "message": "Push notification sent",
                    # CODE SMELL: Exposing Firebase server key in response
                    "firebase_project": FIREBASE_PROJECT_ID
                }), 200
            else:
                return jsonify({"error": "Message is required for push notification"}), 400
        else:
            return jsonify({"error": "User ID is required for push notification"}), 400

    elif notification_type == 'all':
        # CODE SMELL: Calling own endpoints — should reuse shared logic
        results = []
        if email and message:
            try:
                r1 = requests.post('http://localhost:5005/notify', json={
                    "type": "email", "email": email, "message": message, "subject": subject
                })
                results.append({"email": r1.status_code})
            except:
                results.append({"email": "failed"})

        if 'phone' in data and message:
            try:
                r2 = requests.post('http://localhost:5005/notify', json={
                    "type": "sms", "phone": data['phone'], "message": message
                })
                results.append({"sms": r2.status_code})
            except:
                results.append({"sms": "failed"})

        return jsonify({"message": "Multi-channel notification dispatched", "results": results}), 200

    return jsonify({"error": "Invalid notification type"}), 400


# ============================================================
# CODE SMELL: Duplicate fetch-and-map pattern from other services
# CODE SMELL: No authentication check
# CODE SMELL: Unused variables
# ============================================================
@app.route('/notifications/<user_id>', methods=['GET'])
def get_notifications(user_id):
    # CODE SMELL: Unused variables
    notifications_list = []
    total_count = 0
    unread_count = 0

    # CODE SMELL: No error handling
    notifications = list(notifications_collection.find({"recipient": user_id}))

    result = []
    for n in notifications:
        result.append({
            "id": str(n['_id']),
            "type": n['type'],
            "message": n['message'],
            "status": n['status'],
            "created_at": str(n['created_at'])
        })

    return jsonify(result), 200


if __name__ == '__main__':
    # CODE SMELL: debug=True in production
    app.run(host='0.0.0.0', port=5005, debug=True)
