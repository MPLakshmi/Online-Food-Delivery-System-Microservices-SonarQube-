# Online Food Delivery System — SonarQube Demo

> A microservices-based food delivery application intentionally built with **code smells, security vulnerabilities, and quality issues** for SonarQube static analysis demonstration.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Tech Stack](#tech-stack)
4. [Project Structure](#project-structure)
5. [Getting Started](#getting-started)
6. [Running the Application](#running-the-application)
7. [Seeding Demo Data](#seeding-demo-data)
8. [SonarQube Analysis](#sonarqube-analysis)
9. [Intentional Code Issues](#intentional-code-issues)
10. [Security Hotspots Walkthrough](#security-hotspots-walkthrough)
11. [API Reference](#api-reference)
12. [Fixing the Issues](#fixing-the-issues)

---

## Project Overview

**FoodExpress** is a fully functional online food delivery platform built using a microservices architecture. The system allows customers to browse restaurants, add items to cart, place orders, and make payments.

The project is designed as a **SonarQube training tool** — every service contains realistic, intentional code quality issues across three categories:

| Category | Count | Examples |
|---|---|---|
| Bugs | ~8 | Silent exception swallowing, no error handling on DB ops |
| Vulnerabilities / Security Hotspots | ~29+ | Hardcoded passwords, MD5 hashing, debug mode, CSRF |
| Code Smells | ~60+ | Long functions, unused variables, duplicate logic, poor naming |

---

## Architecture

```
                        ┌─────────────────┐
                        │   React Frontend │
                        │   (Port 3000)    │
                        └────────┬────────┘
                                 │ HTTP
                        ┌────────▼────────┐
                        │   API Gateway   │
                        │  Node.js/Express│
                        │   (Port 8081)   │
                        └──┬──┬──┬──┬──┬─┘
              ┌────────────┘  │  │  │  └──────────────┐
              │      ┌────────┘  │  └────────┐         │
              ▼      ▼           ▼           ▼         ▼
       ┌──────────┐ ┌──────────┐ ┌─────────┐ ┌──────────┐ ┌──────────────┐
       │  User    │ │Restaurant│ │  Order  │ │ Payment  │ │Notification  │
       │ Service  │ │ Service  │ │ Service │ │ Service  │ │  Service     │
       │ :5001    │ │  :5002   │ │  :5003  │ │  :5004   │ │   :5005      │
       │ (Flask)  │ │ (Flask)  │ │ (Flask) │ │ (Flask)  │ │  (Flask)     │
       └────┬─────┘ └────┬─────┘ └────┬────┘ └────┬─────┘ └──────┬───────┘
            │             │            │            │               │
            └─────────────┴────────────┴────────────┴───────────────┘
                                       │
                              ┌────────▼────────┐
                              │    MongoDB       │
                              │   (Port 27017)   │
                              └─────────────────┘
```

### Service Responsibilities

| Service | Port | Database | Responsibility |
|---|---|---|---|
| API Gateway | 8081 | — | JWT auth, request routing, CORS |
| User Service | 5001 | userdb | Registration, login, profile management |
| Restaurant Service | 5002 | restaurantdb | Restaurant listing, menu management |
| Order Service | 5003 | orderdb | Order placement, cancellation, history |
| Payment Service | 5004 | paymentdb | Payment processing (Stripe/Razorpay/UPI/COD) |
| Notification Service | 5005 | notificationdb | Email, SMS, push notifications |
| React Frontend | 3000 | — | Customer-facing web UI |

---

## Tech Stack

### Backend
- **Python 3.9** + **Flask 2.3** — all 5 microservices
- **Node.js 18** + **Express** — API Gateway
- **MongoDB** — primary database for all services
- **PyJWT** — JWT token generation and verification
- **PyMongo** — MongoDB driver for Python
- **http-proxy-middleware** — request proxying in the gateway

### Frontend
- **React 18** — component-based UI
- **Axios** — HTTP client for API calls

### Infrastructure
- **Docker** + **Docker Compose** — containerised deployment
- **SonarQube 9.9 LTS Community** — static code analysis
- **sonar-scanner-cli** (Docker image) — scanner execution

---

## Project Structure

```
SonarQube_Demo/
├── api-gateway/
│   ├── Dockerfile
│   ├── gateway.js              ← Node.js proxy + JWT auth
│   └── package.json
├── user-service/
│   ├── Dockerfile
│   ├── app.py                  ← Flask REST API
│   └── requirements.txt
├── restaurant-service/
│   ├── Dockerfile
│   ├── app.py
│   └── requirements.txt
├── order-service/
│   ├── Dockerfile
│   ├── app.py
│   └── requirements.txt
├── payment-service/
│   ├── Dockerfile
│   ├── app.py
│   └── requirements.txt
├── notification-service/
│   ├── Dockerfile
│   ├── app.py
│   └── requirements.txt
├── frontend/
│   ├── Dockerfile
│   ├── public/
│   └── src/
│       ├── App.js
│       ├── components/
│       │   ├── Login.js
│       │   ├── RestaurantList.js
│       │   └── OrderForm.js
│       └── services/
│           └── api.js
├── postman/
│   └── Food_Delivery_API.postman_collection.json
├── docker-compose.yml
├── seed_data.py                ← Populates MongoDB with demo data
└── sonar-project.properties    ← SonarQube scanner config
```

---

## Getting Started

### Prerequisites

| Tool | Version | Purpose |
|---|---|---|
| Docker Desktop | Latest | Container runtime |
| Docker Compose | v2.x | Multi-container orchestration |
| SonarQube | 9.9 LTS | Code analysis server |
| PowerShell | 5.1+ | Running scanner commands |

### 1. Start SonarQube

Run SonarQube in Docker before starting the application:

```powershell
docker run -d --name sonarqube -p 9000:9000 sonarqube:9.9-community
```

Wait ~2 minutes, then open: **http://localhost:9000**

Default credentials: `admin` / `admin` (you will be prompted to change the password on first login)

**SonarQube Login Page:**

![SonarQube Login Page](screenshots/SonarQube-1.png)

### 2. Generate a SonarQube Token

1. Click your avatar (top right) → **My Account**
2. Go to **Security** tab
3. Under **Generate Tokens**, enter name: `food-delivery-token`
4. Click **Generate**
5. Copy the token — it looks like: `sqa_f979d8aeb30eb97b6020f05c5b199ab81a847ce6`

**Token Generation — My Account → Security → Generate Tokens:**

![SonarQube Token Generation](screenshots/SonarQube-1.png)

### 3. Update sonar-project.properties

Open `sonar-project.properties` and paste your token:

```properties
sonar.projectKey=Food-Delivery-System
sonar.projectName=Online Food Delivery System
sonar.projectVersion=1.0.0
sonar.sources=.
sonar.host.url=http://localhost:9000
sonar.login=sqa_YOUR_TOKEN_HERE
```

---

## Running the Application

### Start All Services

```powershell
cd "c:\Users\prasa\Downloads\SonarQube_Demo"
docker-compose up --build -d
```

This starts 7 containers:

| Container | Image | Port |
|---|---|---|
| food-delivery-mongo | mongo:latest | 27017 |
| food-delivery-gateway | custom Node.js | 8081→8080 |
| food-delivery-user | custom Python | 5001 |
| food-delivery-restaurant | custom Python | 5002 |
| food-delivery-order | custom Python | 5003 |
| food-delivery-payment | custom Python | 5004 |
| food-delivery-notification | custom Python | 5005 |
| food-delivery-frontend | custom React | 3000 |

### Verify Services

```powershell
docker-compose ps
```

Open the application: **http://localhost:3000**

**FoodExpress Login Page — http://localhost:3000:**

![FoodExpress Login Page](screenshots/FoodService-App.png)

---

## Seeding Demo Data

The application needs restaurant and menu data. Run the seed script:

```powershell
docker exec food-delivery-restaurant python /app/seed_data.py
```

Or from outside the container:

```powershell
cd "c:\Users\prasa\Downloads\SonarQube_Demo"
python seed_data.py
```

This creates **4 restaurants** and **25 menu items**:

| Restaurant | Cuisine | Min Order | Rating |
|---|---|---|---|
| Spice Garden | Indian | ₹150 | 4.7 ⭐ |
| Dragon Wok | Chinese | ₹200 | 4.4 ⭐ |
| Pizza Roma | Italian | ₹250 | 4.5 ⭐ |
| Burger Barn | American | ₹180 | 4.2 ⭐ |

**Restaurant Listing Page — after login:**

![Restaurant Listing Page](screenshots/FoodService-App.png)

### Demo Login Credentials

| Field | Value |
|---|---|
| Email | `demo@foodexpress.com` |
| Password | `Demo@1234` |

To create this account, use the **Register** tab on the login screen.

---

## SonarQube Analysis

### Run the Scanner

Open **PowerShell** (not Git Bash — path mangling causes issues) and run:

```powershell
docker run --rm --network host `
  -v "c:\Users\prasa\Downloads\SonarQube_Demo:/usr/src" `
  sonarsource/sonar-scanner-cli `
  "-Dsonar.projectKey=Food-Delivery-System" `
  "-Dsonar.host.url=http://localhost:9000" `
  "-Dsonar.login=sqa_YOUR_TOKEN_HERE"
```

> **Important:** Wrap each `-Dsonar.*` argument in quotes to prevent PowerShell from splitting them.

### View Results in SonarQube

Open: **http://localhost:9000/dashboard?id=Food-Delivery-System**

**SonarQube Project Dashboard — http://localhost:9000/dashboard?id=Food-Delivery-System:**

![SonarQube Project Dashboard](screenshots/SonarQube-1.png)

**Security Hotspots Page — 29 hotspots to review:**

![SonarQube Security Hotspots](screenshots/SonarQube-Hotspots.png)

---

## Intentional Code Issues

This project contains the following intentional issues for SonarQube demonstration:

### Security Hotspots (29 total)

#### 1. Hardcoded Passwords — `python:S2068` / `javascript:S2068`

**Files affected:** All 5 Python services + gateway.js + api.js

```python
# user-service/app.py
DB_PASSWORD = "SuperSecretDBPassword@2024"         # ← VULNERABILITY
ADMIN_PASSWORD = "Admin@FoodDelivery#9999"         # ← VULNERABILITY
ROOT_PASSWORD = "r00tP@ssw0rd_hardcoded"           # ← VULNERABILITY
JWT_SECRET = "mysecretkey123"                      # ← VULNERABILITY
```

```javascript
// api-gateway/gateway.js
const password = 'Gateway@HardcodedPass#2024';     // ← VULNERABILITY
const adminPassword = 'GatewayAdmin@SuperSecret_999'; // ← VULNERABILITY
```

**Risk:** Credentials committed to source control can be found by anyone with repo access.

#### 2. Weak Password Hashing — `python:S4790`

**File:** `user-service/app.py` — Line 91

```python
# INSECURE — MD5 is not suitable for password hashing
hashed = hashlib.md5(password.encode()).hexdigest()
```

**Risk:** MD5 is a fast hash — attackers can brute-force billions of attempts per second. Use bcrypt instead.

#### 3. CSRF Protection Disabled — `python:S4502`

**Files:** All 5 Flask service files

```python
# Flask has no built-in CSRF protection for REST APIs
# SonarQube flags this as a hotspot requiring review
app = Flask(__name__)
# No CSRFProtect() configured
```

**Risk:** Form-based endpoints are vulnerable to cross-site request forgery without explicit protection.

#### 4. Debug Mode in Production — `python:S5659`

**Files:** All 5 Flask services

```python
# INSECURE — debug=True exposes stack traces and the Werkzeug debugger
app.run(host='0.0.0.0', port=5001, debug=True)
```

**Risk:** The Werkzeug debugger allows arbitrary code execution in development mode.

#### 5. Sensitive Data in Logs

**File:** `api-gateway/gateway.js`

```javascript
// Logs entire request headers including Authorization tokens
console.log('Headers:', JSON.stringify(req.headers));

// Logs credentials on startup
console.log(`JWT Secret: ${JWT_SECRET}`);
console.log(`Gateway Key: ${GATEWAY_API_KEY}`);
```

---

### Code Smells (60+)

| Smell | Pattern | Files |
|---|---|---|
| Long functions | Functions > 100 lines | order-service, user-service |
| Deeply nested conditions | 8 levels deep | order-service (place_order) |
| Unused variables | `a=1; b=2; c=3` declared but never read | All services |
| Poor naming | `x`, `d`, `temp`, single letters | All files |
| Duplicate code | Token decode copied 6 times | All Python services |
| Silent exceptions | `except: pass` | order-service, notification-service |
| Dead code | Hardcoded feature flags | frontend/App.js |
| Magic numbers | Inline constants | order-service (TAX_RATE) |

---

## Security Hotspots Walkthrough

### How to Review a Hotspot in SonarQube

1. Go to **http://localhost:9000/security_hotspots?id=Food-Delivery-System**
2. Click any hotspot in the left panel
3. Review the four tabs:
   - **Where is the risk?** — exact file and line number
   - **What's the risk?** — explanation of the vulnerability
   - **Assess the risk** — questions to determine if it's a real issue
   - **How can I fix it?** — recommended remediation steps
4. Change the status:
   - **To Review** → default, not yet assessed
   - **Acknowledged** → risk confirmed, will be fixed later
   - **Fixed** → code has been remediated
   - **Safe** → risk assessed and accepted (e.g., CSRF on JWT API)

**Hotspot Detail View — showing the MD5 weak hashing issue:**

![SonarQube Hotspot Detail](screenshots/SonarQube-Hotspots.png)

---

## API Reference

All requests go through the API Gateway at `http://localhost:8081`.

### Public Endpoints (no auth required)

| Method | URL | Description |
|---|---|---|
| POST | `/api/users/register` | Register new user |
| POST | `/api/users/login` | Login and get JWT token |
| GET | `/api/restaurants/restaurants` | List all restaurants |
| GET | `/api/restaurants/menu/<restaurant_id>` | Get menu for a restaurant |

### Protected Endpoints (requires `Authorization: Bearer <token>`)

| Method | URL | Description |
|---|---|---|
| GET | `/api/users/profile/<user_id>` | Get user profile |
| PUT | `/api/users/update-profile` | Update profile |
| POST | `/api/orders/order/place` | Place a new order |
| GET | `/api/orders/order/<order_id>` | Get order by ID |
| GET | `/api/orders/orders/user/<user_id>` | Get user's order history |
| PUT | `/api/orders/order/cancel/<order_id>` | Cancel an order |
| POST | `/api/payments/process` | Process payment |

### Example: Register a User

```bash
curl -X POST http://localhost:8081/api/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "Secure@Pass123",
    "phone": "9876543210"
  }'
```

Response:
```json
{
  "message": "User registered successfully",
  "token": "eyJhbGciOiJIUzI1NiJ9...",
  "user_id": "64f1a2b3c4d5e6f7a8b9c0d1"
}
```

### Example: Place an Order

```bash
curl -X POST http://localhost:8081/api/orders/order/place \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9..." \
  -d '{
    "restaurant_id": "64f1a2b3c4d5e6f7a8b9c0d1",
    "items": [
      {"name": "Butter Chicken", "price": 320, "quantity": 2},
      {"name": "Garlic Naan", "price": 60, "quantity": 3}
    ],
    "payment_method": "upi",
    "upi_id": "john@upi",
    "delivery_address": "12 MG Road, Bangalore"
  }'
```

### Postman Collection

Import `postman/Food_Delivery_API.postman_collection.json` into Postman to get all endpoints pre-configured with examples.

---

## Fixing the Issues

### Priority 1 — Replace MD5 with bcrypt (CRITICAL)

**File:** `user-service/app.py`

```python
# Before (insecure)
import hashlib
hashed = hashlib.md5(password.encode()).hexdigest()

# After (secure)
import bcrypt
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
```

Add to `user-service/requirements.txt`:
```
bcrypt==4.0.1
```

### Priority 2 — Move Secrets to Environment Variables

**All Python services:**
```python
# Before
JWT_SECRET = "mysecretkey123"

# After
JWT_SECRET = os.environ.get("JWT_SECRET", "change-me-in-production")
```

**api-gateway/gateway.js:**
```javascript
// Before
const JWT_SECRET = 'mysecretkey123';

// After
const JWT_SECRET = process.env.JWT_SECRET || 'change-me-in-production';
```

### Priority 3 — Disable Debug Mode

**All 5 Flask services:**
```python
# Before
app.run(host='0.0.0.0', port=5001, debug=True)

# After
app.run(host='0.0.0.0', port=5001, debug=False)
```

### Priority 4 — Remove Credential Logging

**api-gateway/gateway.js:**
```javascript
// Remove these lines:
console.log('Headers:', JSON.stringify(req.headers));  // DELETE
console.log(`JWT Secret: ${JWT_SECRET}`);              // DELETE
console.log(`Gateway Key: ${GATEWAY_API_KEY}`);        // DELETE
```

### Priority 5 — Add .dockerignore Files

Create `.dockerignore` in each service folder:
```
.env
*.env
__pycache__/
*.pyc
node_modules/
*.log
.git
```

### After Fixes — Re-run Scanner

```powershell
docker run --rm --network host `
  -v "c:\Users\prasa\Downloads\SonarQube_Demo:/usr/src" `
  sonarsource/sonar-scanner-cli `
  "-Dsonar.projectKey=Food-Delivery-System" `
  "-Dsonar.host.url=http://localhost:9000" `
  "-Dsonar.login=sqa_YOUR_TOKEN_HERE"
```

Expected result after all fixes:

| Metric | Before | After |
|---|---|---|
| Security Hotspots | 29 | ~5 (CSRF — acceptable for JWT APIs) |
| Hardcoded Passwords | 25+ | 0 |
| Weak Hashing | 2 | 0 |
| Debug Mode | 5 | 0 |

---

## Troubleshooting

### Port 8080 Already in Use

Change the gateway port in `docker-compose.yml`:
```yaml
api-gateway:
  ports:
    - "8081:8080"   # host:container
```

Update `frontend/src/services/api.js`:
```javascript
const API_BASE_URL = 'http://localhost:8081/api';
```

### MongoDB Connection Refused

Ensure the MONGO_URI uses the Docker service name, not `localhost`:
```yaml
# docker-compose.yml
user-service:
  environment:
    MONGO_URI: mongodb://admin:password123@mongodb:27017/
```

### SonarQube Scanner Argument Error

Use PowerShell (not Git Bash) and quote each `-D` flag:
```powershell
# Wrong (Git Bash — path mangling)
-Dsonar.projectKey=Food-Delivery-System

# Correct (PowerShell — quoted)
"-Dsonar.projectKey=Food-Delivery-System"
```

### Login Button Not Working

This happens if `express.json()` is added to the gateway — it consumes the HTTP body stream before the proxy can forward it to Flask. The gateway must **not** parse the body.

---

## License

This project is for educational and demonstration purposes only. The intentional security vulnerabilities are artificial and designed to trigger SonarQube rules — do not deploy this application to a production environment.

---

## Disclaimer

> **FOR EDUCATIONAL USE ONLY**
>
> This codebase was purpose-built to demonstrate static code analysis using SonarQube. Every security issue, vulnerability, and code smell present in this project is **deliberate and artificial**.
>
> | What it is | What it is NOT |
> |---|---|
> | A SonarQube training tool | A production-ready application |
> | A collection of intentional bad practices | A reference for real development |
> | A local/lab-only demo | A deployable product |
> | Uses fake/test credentials | Uses real or sensitive secrets |
>
> **By using this project you acknowledge that:**
>
> 1. You will run it **only in an isolated local environment** (localhost / lab network).
> 2. You will **not commit real credentials, tokens, or keys** into this repository.
> 3. You understand that the patterns shown are **anti-patterns** — the opposite of what should be done in real projects.
> 4. The authors and contributors are **not responsible** for any security incidents arising from misuse or improper deployment of this codebase.
>
> If you are looking for a secure, production-grade microservices template, this project is **not** the right starting point.
