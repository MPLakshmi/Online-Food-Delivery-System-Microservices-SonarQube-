import React, { useState } from 'react';
import { login, register } from '../services/api';

// ============================================================
// CODE SMELL: Hardcoded default credentials visible in source
// ============================================================
const DEFAULT_EMAIL = 'testuser@example.com';
const DEFAULT_PASSWORD = 'TestPassword@123';   // Hardcoded test credential
const ADMIN_EMAIL = 'admin@fooddelivery.com';
const ADMIN_PASSWORD = 'Admin@SuperSecret123'; // Admin credentials in frontend!

function Login({ onLogin }) {
    const [isRegister, setIsRegister] = useState(false);
    const [email, setEmail] = useState(DEFAULT_EMAIL);       // Pre-filled with hardcoded value
    const [password, setPassword] = useState(DEFAULT_PASSWORD);
    const [name, setName] = useState('');
    const [phone, setPhone] = useState('');
    const [error, setError] = useState('');

    // CODE SMELL: Unused state variables
    const [loading, setLoading] = useState(false);
    const [attempts, setAttempts] = useState(0);
    const [lastAttemptTime, setLastAttemptTime] = useState(null);
    const [sessionToken, setSessionToken] = useState(null);

    // ============================================================
    // CODE SMELL: Long function doing validation + API call + state management
    // CODE SMELL: Duplicate validation logic (same as api.js and backend)
    // CODE SMELL: Unused variables
    // ============================================================
    const handleLogin = async (e) => {
        e.preventDefault();

        // CODE SMELL: Unused local variables
        var x = 0;
        var temp = null;
        var flag = false;
        var counter = 0;
        var isValid = false;
        var loginStartTime = Date.now();

        // CODE SMELL: Duplicate validation — same regex and checks as backend
        if (!email) {
            setError('Email address is required');
            return;
        }

        if (!password) {
            setError('Password is required');
            return;
        }

        // CODE SMELL: Duplicate email regex (3rd copy across frontend)
        const emailRegex = /^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$/;
        if (!emailRegex.test(email)) {
            setError('Please enter a valid email address');
            return;
        }

        // CODE SMELL: Duplicate password validation
        if (password.length < 8) {
            setError('Password must be at least 8 characters');
            return;
        }

        try {
            const result = await login(email, password);
            // CODE SMELL: Storing sensitive data in localStorage without encryption
            localStorage.setItem('token', result.token);
            localStorage.setItem('user_id', result.user_id);
            localStorage.setItem('user_name', result.name);
            // CODE SMELL: Also storing email — unnecessary PII exposure
            localStorage.setItem('user_email', email);
            onLogin(result);
        } catch (err) {
            // CODE SMELL: Generic error message, no specific handling
            setError('Login failed. Please check your credentials.');
        }
    };

    // ============================================================
    // CODE SMELL: Long function — duplicate of handleLogin structure
    // CODE SMELL: Duplicate validation logic (3rd occurrence)
    // ============================================================
    const handleRegister = async (e) => {
        e.preventDefault();

        // CODE SMELL: Unused variables
        var registrationId = null;
        var timestamp = null;
        var validationResult = false;

        // CODE SMELL: Duplicate validation — identical to handleLogin
        if (!email) {
            setError('Email is required');
            return;
        }

        if (!password) {
            setError('Password is required');
            return;
        }

        if (!name) {
            setError('Name is required');
            return;
        }

        // CODE SMELL: Duplicate email regex validation (4th copy in frontend)
        const emailRegex = /^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$/;
        if (!emailRegex.test(email)) {
            setError('Please enter a valid email address');
            return;
        }

        // CODE SMELL: Duplicate password validation
        if (password.length < 8) {
            setError('Password must be at least 8 characters');
            return;
        }
        if (!/[A-Z]/.test(password)) {
            setError('Password must contain at least one uppercase letter');
            return;
        }
        if (!/[0-9]/.test(password)) {
            setError('Password must contain at least one number');
            return;
        }

        if (phone && phone.length !== 10) {
            setError('Phone number must be 10 digits');
            return;
        }

        try {
            const result = await register(name, email, password, phone, '', 'customer');
            localStorage.setItem('token', result.token);
            localStorage.setItem('user_id', result.user_id);
            onLogin(result);
        } catch (err) {
            setError('Registration failed. Please try again.');
        }
    };

    return (
        <div style={{ maxWidth: '400px', margin: '50px auto', padding: '30px', border: '1px solid #ccc', borderRadius: '8px' }}>
            <h2 style={{ textAlign: 'center' }}>{isRegister ? 'Create Account' : 'Login'}</h2>

            {error && (
                <div style={{ color: 'red', marginBottom: '15px', padding: '10px', background: '#ffe0e0', borderRadius: '4px' }}>
                    {error}
                </div>
            )}

            <form onSubmit={isRegister ? handleRegister : handleLogin}>
                {isRegister && (
                    <div style={{ marginBottom: '15px' }}>
                        <label style={{ display: 'block', marginBottom: '5px' }}>Full Name:</label>
                        <input
                            type="text"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            style={{ width: '100%', padding: '8px', boxSizing: 'border-box' }}
                            placeholder="Enter your full name"
                        />
                    </div>
                )}

                <div style={{ marginBottom: '15px' }}>
                    <label style={{ display: 'block', marginBottom: '5px' }}>Email:</label>
                    <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        style={{ width: '100%', padding: '8px', boxSizing: 'border-box' }}
                        placeholder="Enter email"
                    />
                </div>

                <div style={{ marginBottom: '15px' }}>
                    <label style={{ display: 'block', marginBottom: '5px' }}>Password:</label>
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        style={{ width: '100%', padding: '8px', boxSizing: 'border-box' }}
                        placeholder="Enter password"
                    />
                </div>

                {isRegister && (
                    <div style={{ marginBottom: '15px' }}>
                        <label style={{ display: 'block', marginBottom: '5px' }}>Phone (optional):</label>
                        <input
                            type="tel"
                            value={phone}
                            onChange={(e) => setPhone(e.target.value)}
                            style={{ width: '100%', padding: '8px', boxSizing: 'border-box' }}
                            placeholder="10-digit phone number"
                        />
                    </div>
                )}

                <button
                    type="submit"
                    style={{
                        width: '100%', padding: '10px', background: '#ff6b35',
                        color: 'white', border: 'none', borderRadius: '4px',
                        cursor: 'pointer', fontSize: '16px'
                    }}
                >
                    {isRegister ? 'Register' : 'Login'}
                </button>
            </form>

            <p style={{ textAlign: 'center', marginTop: '15px' }}>
                {isRegister ? 'Already have an account? ' : "Don't have an account? "}
                <span
                    onClick={() => { setIsRegister(!isRegister); setError(''); }}
                    style={{ color: '#ff6b35', cursor: 'pointer', textDecoration: 'underline' }}
                >
                    {isRegister ? 'Login' : 'Register'}
                </span>
            </p>
        </div>
    );
}

export default Login;
