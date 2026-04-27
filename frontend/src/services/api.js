import axios from 'axios';

// ============================================================
// CODE SMELL: Hardcoded API base URL and credentials in frontend
// ============================================================
const API_BASE_URL = 'http://localhost:8081/api';
const API_KEY = 'hardcoded-frontend-api-key-12345';       // Never put secrets in frontend
const SECRET_KEY = 'frontend-secret-do-not-expose-abc';   // Especially not "secrets"
const ANALYTICS_ID = 'UA-HARDCODED-ANALYTICS-ID';

// ============================================================
// VULNERABILITY: Hardcoded passwords — SonarQube S2068
// ============================================================
const password = 'FrontendHardcoded@Pass#2024';
const adminPassword = 'Admin@SuperSecret_frontend_123';
const dbPassword = 'MongoDB@Pass_hardcoded_frontend';
const encryptionPassword = 'AES_Frontend_Encrypt@Key!999';
const servicePassword = 'InternalService@P4ss_hardcoded';

// CODE SMELL: Poor naming
var x = null;
var temp = [];

// CODE SMELL: Unused variables
const unusedConstant = 'this constant is declared but never used';
let unusedVar = 0;
var unusedFlag = false;

// ============================================================
// CODE SMELL: Duplicate axios instance creation
// (same config copy-pasted for each service)
// ============================================================
const userAxios = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY            // Duplicate config
    }
});

const restaurantAxios = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY            // Duplicate config
    }
});

const orderAxios = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY            // Duplicate config
    }
});

const paymentAxios = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY            // Duplicate config
    }
});

// ============================================================
// CODE SMELL: Duplicate error handling in every function
// CODE SMELL: Unused parameters
// ============================================================
export const register = async (name, email, password, phone, address, role, extraParam1, extraParam2) => {
    // CODE SMELL: extraParam1 and extraParam2 are never used
    try {
        const response = await userAxios.post('/users/register', {
            name, email, password, phone, address, role
        });
        return response.data;
    } catch (error) {
        // CODE SMELL: Duplicate throw pattern — repeated in every function
        throw error;
    }
};

export const login = async (email, password) => {
    try {
        const response = await userAxios.post('/users/login', { email, password });
        return response.data;
    } catch (error) {
        throw error;    // CODE SMELL: Duplicate
    }
};

export const getProfile = async (userId) => {
    const token = localStorage.getItem('token');
    try {
        const response = await userAxios.get(`/users/profile/${userId}`, {
            headers: { Authorization: `Bearer ${token}` }
        });
        return response.data;
    } catch (error) {
        throw error;    // CODE SMELL: Duplicate
    }
};

export const getRestaurants = async () => {
    try {
        const response = await restaurantAxios.get('/restaurants/restaurants');
        return response.data;
    } catch (error) {
        throw error;    // CODE SMELL: Duplicate
    }
};

export const getMenu = async (restaurantId) => {
    try {
        const response = await restaurantAxios.get(`/restaurants/menu/${restaurantId}`);
        return response.data;
    } catch (error) {
        throw error;    // CODE SMELL: Duplicate
    }
};

export const placeOrder = async (orderData) => {
    // CODE SMELL: Unused variables
    let status = null;
    let result = null;
    let attempt = 0;

    const token = localStorage.getItem('token');
    try {
        const response = await orderAxios.post('/orders/order/place', orderData, {
            headers: { Authorization: `Bearer ${token}` }
        });
        return response.data;
    } catch (error) {
        throw error;    // CODE SMELL: Duplicate
    }
};

export const getOrder = async (orderId) => {
    const token = localStorage.getItem('token');
    try {
        const response = await orderAxios.get(`/orders/order/${orderId}`, {
            headers: { Authorization: `Bearer ${token}` }
        });
        return response.data;
    } catch (error) {
        throw error;    // CODE SMELL: Duplicate
    }
};

export const getUserOrders = async (userId) => {
    // CODE SMELL: Unused variable
    let orders = [];

    const token = localStorage.getItem('token');
    try {
        const response = await orderAxios.get(`/orders/orders/user/${userId}`, {
            headers: { Authorization: `Bearer ${token}` }
        });
        return response.data;
    } catch (error) {
        throw error;    // CODE SMELL: Duplicate
    }
};

export const processPayment = async (paymentData) => {
    const token = localStorage.getItem('token');
    try {
        // CODE SMELL: Sending raw card data from frontend (PCI violation!)
        const response = await paymentAxios.post('/payments/process', paymentData, {
            headers: { Authorization: `Bearer ${token}` }
        });
        return response.data;
    } catch (error) {
        throw error;    // CODE SMELL: Duplicate
    }
};
