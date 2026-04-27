# Screenshots Guide

Place the following screenshots in this folder. File names must match exactly.

| File Name | What to Capture | URL / Location |
|---|---|---|
| `01-sonarqube-login.png` | SonarQube login page | http://localhost:9000 |
| `02-sonarqube-token-generation.png` | My Account → Security → Generate Tokens page showing a generated token | http://localhost:9000/account/security |
| `03-docker-containers-running.png` | Docker Desktop Containers tab showing all 8 containers with green Running status | Docker Desktop app |
| `04-app-login-page.png` | FoodExpress login screen with email/password fields | http://localhost:3000 |
| `05-app-restaurant-list.png` | Restaurant listing page after logging in (showing Spice Garden, Dragon Wok, etc.) | http://localhost:3000 |
| `06-sonarqube-scanner-success.png` | PowerShell window showing scanner output ending with EXECUTION SUCCESS | PowerShell terminal |
| `07-sonarqube-dashboard.png` | SonarQube project overview dashboard showing Bugs, Code Smells, Security Hotspots counts | http://localhost:9000/dashboard?id=Food-Delivery-System |
| `08-sonarqube-security-hotspots.png` | Security Hotspots list page showing 29 hotspots with HIGH/MEDIUM categories | http://localhost:9000/security_hotspots?id=Food-Delivery-System |
| `09-sonarqube-hotspot-detail.png` | Click the MD5 / weak hashing hotspot — shows the code highlighted in user-service/app.py | http://localhost:9000/security_hotspots?id=Food-Delivery-System |
| `10-sonarqube-csrf-hotspot.png` | Click the CSRF hotspot — shows the Flask route code | http://localhost:9000/security_hotspots?id=Food-Delivery-System |

## How to take screenshots on Windows

- **Full screen:** `PrtScn` key
- **Active window:** `Alt + PrtScn`
- **Region select:** `Win + Shift + S` → drag to select → paste into Paint and save as PNG
