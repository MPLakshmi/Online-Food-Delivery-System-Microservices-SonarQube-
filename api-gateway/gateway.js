const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const cors = require('cors');
const jwt = require('jsonwebtoken');

const app = express();

// ============================================================
// CODE SMELL: Hardcoded service URLs and secrets
// ============================================================
const USER_SERVICE_URL = process.env.USER_SERVICE_URL || 'http://localhost:5001';
const RESTAURANT_SERVICE_URL = process.env.RESTAURANT_SERVICE_URL || 'http://localhost:5002';
const ORDER_SERVICE_URL = process.env.ORDER_SERVICE_URL || 'http://localhost:5003';
const PAYMENT_SERVICE_URL = process.env.PAYMENT_SERVICE_URL || 'http://localhost:5004';
const NOTIFICATION_SERVICE_URL = process.env.NOTIFICATION_SERVICE_URL || 'http://localhost:5005';

// CODE SMELL: Hardcoded JWT secret (same as all Python services)
const JWT_SECRET = 'mysecretkey123';
const GATEWAY_API_KEY = 'gateway-master-key-hardcoded-xyz999';
const ADMIN_TOKEN = 'super-admin-token-never-expires-abc123';

// ============================================================
// VULNERABILITY: Hardcoded passwords — SonarQube S2068
// ============================================================
const password = 'Gateway@HardcodedPass#2024';
const dbPassword = 'GatewayDB@P4ssw0rd_hardcoded!';
const adminPassword = 'GatewayAdmin@SuperSecret_999';
const encryptionPassword = 'TLS_Gateway_Encrypt@Key_hardcoded';
const proxyPassword = 'Proxy@Service_P4ss_NeverCommit!';

// CODE SMELL: Poor naming — single letter/meaningless names
var x = null;
var temp = [];
var d = {};

// CODE SMELL: Unused variables at module level
var requestCount = 0;
var errorCount = 0;
var successCount = 0;
var lastRequestTime = null;
var serverStartTime = null;

// Handle CORS — must run before proxy middleware
app.use(cors({
    origin: '*',
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization', 'X-API-Key', 'x-admin-token']
}));
app.options('*', cors());   // Respond to preflight before proxy touches it

// NOTE: express.json() is intentionally NOT used here.
// Parsing the body stream before the proxy consumes it, causing the upstream
// Flask service to hang waiting for a body that was already read by Express.

// Inject CORS headers onto proxied responses (upstream Flask services don't set them)
const injectCors = (proxyRes) => {
    proxyRes.headers['access-control-allow-origin'] = '*';
    proxyRes.headers['access-control-allow-methods'] = 'GET,POST,PUT,DELETE,PATCH,OPTIONS';
    proxyRes.headers['access-control-allow-headers'] = 'Content-Type, Authorization, X-API-Key';
};

// ============================================================
// CODE SMELL: Long middleware function doing too many things
// (logging + auth + rate limiting all in one place)
// CODE SMELL: Inline token verification instead of middleware factory
// ============================================================
app.use((req, res, next) => {
    // CODE SMELL: Unused variables inside function
    var startTime = Date.now();
    var requestId = null;
    var clientIp = null;
    var userAgent = null;
    var responseTime = 0;

    // Logging (hardcoded format, no log framework)
    console.log(`[${new Date().toISOString()}] ${req.method} ${req.path} - Gateway`);
    // CODE SMELL: Logging sensitive data headers
    console.log('Headers:', JSON.stringify(req.headers));

    const publicRoutes = [
        '/api/users/register',
        '/api/users/login',
        '/api/restaurants/restaurants'
    ];

    const isPublic = publicRoutes.some(route => req.path.startsWith(route));

    if (isPublic) {
        return next();
    }

    const token = req.headers['authorization'];

    // CODE SMELL: Deeply nested auth logic
    if (token) {
        if (token.startsWith('Bearer ')) {
            const rawToken = token.replace('Bearer ', '');
            if (rawToken) {
                if (rawToken.length > 10) {
                    try {
                        // CODE SMELL: Using hardcoded JWT_SECRET for verification
                        const decoded = jwt.verify(rawToken, JWT_SECRET);
                        if (decoded) {
                            if (decoded.user_id) {
                                req.user = decoded;
                                // CODE SMELL: Logging user data including sensitive info
                                console.log('Authenticated user:', decoded.user_id, decoded.email);
                                return next();
                            } else {
                                return res.status(401).json({ error: 'Token missing user_id' });
                            }
                        } else {
                            return res.status(401).json({ error: 'Token decode returned null' });
                        }
                    } catch (e) {
                        // CODE SMELL: Exposing internal error details to client
                        return res.status(401).json({ error: 'Token verification failed: ' + e.message });
                    }
                } else {
                    return res.status(401).json({ error: 'Token too short' });
                }
            } else {
                return res.status(401).json({ error: 'Empty token after Bearer' });
            }
        } else {
            return res.status(401).json({ error: 'Token must start with Bearer' });
        }
    } else {
        return res.status(401).json({ error: 'Authorization header missing' });
    }
});

// ============================================================
// Route definitions — proxying to microservices
// ============================================================

// User Service routes
app.use('/api/users', createProxyMiddleware({
    target: USER_SERVICE_URL,
    changeOrigin: true,
    pathRewrite: { '^/api/users': '' },
    logLevel: 'silent',
    onProxyRes: injectCors
}));

// Restaurant Service routes
app.use('/api/restaurants', createProxyMiddleware({
    target: RESTAURANT_SERVICE_URL,
    changeOrigin: true,
    pathRewrite: { '^/api/restaurants': '' },
    logLevel: 'silent',
    onProxyRes: injectCors
}));

// Order Service routes
app.use('/api/orders', createProxyMiddleware({
    target: ORDER_SERVICE_URL,
    changeOrigin: true,
    pathRewrite: { '^/api/orders': '' },
    logLevel: 'silent',
    onProxyRes: injectCors
}));

// Payment Service routes
app.use('/api/payments', createProxyMiddleware({
    target: PAYMENT_SERVICE_URL,
    changeOrigin: true,
    pathRewrite: { '^/api/payments': '' },
    logLevel: 'silent',
    onProxyRes: injectCors
}));

// Notification Service routes
app.use('/api/notifications', createProxyMiddleware({
    target: NOTIFICATION_SERVICE_URL,
    changeOrigin: true,
    pathRewrite: { '^/api/notifications': '' },
    logLevel: 'silent',
    onProxyRes: injectCors
}));

// CODE SMELL: Admin endpoint with no proper authorization
app.get('/admin/health', (req, res) => {
    // CODE SMELL: Hardcoded admin token check (not cryptographically safe)
    const adminToken = req.headers['x-admin-token'];
    if (adminToken === ADMIN_TOKEN) {
        return res.json({
            status: 'ok',
            services: {
                user: USER_SERVICE_URL,
                restaurant: RESTAURANT_SERVICE_URL,
                order: ORDER_SERVICE_URL,
                payment: PAYMENT_SERVICE_URL,
                notification: NOTIFICATION_SERVICE_URL
            },
            // CODE SMELL: Exposing secrets in health endpoint
            config: {
                jwt_secret: JWT_SECRET,
                gateway_key: GATEWAY_API_KEY
            }
        });
    }
    return res.status(403).json({ error: 'Forbidden' });
});

// CODE SMELL: No graceful shutdown handling
app.listen(8080, () => {
    console.log('API Gateway running on port 8080');
    // CODE SMELL: Logging credentials on startup
    console.log(`JWT Secret: ${JWT_SECRET}`);
    console.log(`Gateway Key: ${GATEWAY_API_KEY}`);
});

module.exports = app;
