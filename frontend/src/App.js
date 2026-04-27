import React, { useState } from 'react';
import Login from './components/Login';
import RestaurantList from './components/RestaurantList';
import OrderForm from './components/OrderForm';

// ============================================================
// CODE SMELL: Hardcoded config values in application code
// ============================================================
const APP_VERSION = '1.0.0';
const DEBUG_MODE = true;                                       // Should be env variable
const ANALYTICS_KEY = 'GA-HARDCODED-UA-123456789-1';          // Google Analytics key
const SENTRY_DSN = 'https://fakekey@o123456.ingest.sentry.io/1234567'; // Sentry DSN
const FEATURE_FLAG_NEW_UI = true;                              // Hardcoded feature flag

// CODE SMELL: Poor naming at module level
var x = null;
var d = {};

function App() {
    const [user, setUser] = useState(null);
    const [selectedRestaurant, setSelectedRestaurant] = useState(null);
    const [cartItems, setCartItems] = useState([]);
    const [currentView, setCurrentView] = useState('login');
    const [orderHistory, setOrderHistory] = useState([]);

    // CODE SMELL: Unused state variables
    const [notifications, setNotifications] = useState([]);
    const [lastActivity, setLastActivity] = useState(null);
    const [userPreferences, setUserPreferences] = useState({});
    const [appError, setAppError] = useState(null);

    const handleLogin = (userData) => {
        setUser(userData);
        setCurrentView('restaurants');

        // CODE SMELL: console.log in production code
        if (DEBUG_MODE) {
            console.log('User logged in:', userData);  // Logs user data to console
            console.log('Analytics:', ANALYTICS_KEY);  // Exposes analytics key
        }
    };

    // CODE SMELL: Duplicate cart logic (same pattern also in RestaurantList)
    const handleAddToCart = (restaurant, item) => {
        // CODE SMELL: Unused variable
        var itemAdded = false;

        if (selectedRestaurant && selectedRestaurant.id !== restaurant.id) {
            if (!window.confirm('Adding from a different restaurant will clear your cart. Continue?')) {
                return;
            }
            setCartItems([]);
        }

        setSelectedRestaurant(restaurant);

        // CODE SMELL: Duplicate add-to-cart logic (same in potential CartComponent)
        const existingItem = cartItems.find(i => i.id === item.id);
        if (existingItem) {
            setCartItems(cartItems.map(i =>
                i.id === item.id ? { ...i, quantity: i.quantity + 1 } : i
            ));
        } else {
            setCartItems([...cartItems, { ...item, quantity: 1 }]);
        }

        setCurrentView('order');
    };

    const handleLogout = () => {
        // CODE SMELL: Unused variable capturing user before clear
        var previousUser = user;

        setUser(null);
        setCurrentView('login');
        setCartItems([]);
        setSelectedRestaurant(null);
        setOrderHistory([]);

        localStorage.removeItem('token');
        localStorage.removeItem('user_id');
        localStorage.removeItem('user_name');
        localStorage.removeItem('user_email');

        // CODE SMELL: console.log in production
        console.log('User logged out. Previous user:', previousUser?.user_id);
    };

    const handleOrderSuccess = (orderResult) => {
        // CODE SMELL: Unused variable
        var successTime = Date.now();

        setOrderHistory(prev => [...prev, orderResult]);
        setCartItems([]);
        setCurrentView('restaurants');
    };

    const cartCount = cartItems.reduce((sum, item) => sum + (item.quantity || 0), 0);

    return (
        <div style={{ fontFamily: 'Arial, sans-serif', minHeight: '100vh', background: '#f5f5f5' }}>
            {/* Header */}
            <header style={{
                background: '#ff6b35', color: 'white', padding: '0 20px',
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                height: '60px', boxShadow: '0 2px 8px rgba(0,0,0,0.15)'
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <span style={{ fontSize: '24px' }}>🍔</span>
                    <h1 style={{ margin: 0, fontSize: '22px' }}>FoodExpress</h1>
                    {/* CODE SMELL: Debug info visible in production UI */}
                    {DEBUG_MODE && (
                        <span style={{ fontSize: '11px', background: 'rgba(0,0,0,0.3)', padding: '2px 6px', borderRadius: '4px' }}>
                            v{APP_VERSION} | DEBUG
                        </span>
                    )}
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
                    {user && (
                        <>
                            <span style={{ fontSize: '14px' }}>Hello, {user.name || 'User'}</span>

                            {cartCount > 0 && (
                                <button
                                    onClick={() => setCurrentView('order')}
                                    style={{ background: 'white', color: '#ff6b35', border: 'none', padding: '6px 14px', borderRadius: '20px', cursor: 'pointer', fontWeight: 'bold' }}
                                >
                                    🛒 Cart ({cartCount})
                                </button>
                            )}

                            {currentView !== 'restaurants' && (
                                <button
                                    onClick={() => setCurrentView('restaurants')}
                                    style={{ background: 'rgba(255,255,255,0.2)', color: 'white', border: '1px solid rgba(255,255,255,0.5)', padding: '6px 14px', borderRadius: '4px', cursor: 'pointer' }}
                                >
                                    Browse
                                </button>
                            )}

                            <button
                                onClick={handleLogout}
                                style={{ background: 'rgba(0,0,0,0.2)', color: 'white', border: 'none', padding: '6px 14px', borderRadius: '4px', cursor: 'pointer' }}
                            >
                                Logout
                            </button>
                        </>
                    )}
                </div>
            </header>

            {/* Main Content */}
            <main style={{ maxWidth: '1200px', margin: '0 auto', padding: '20px' }}>
                {currentView === 'login' && (
                    <Login onLogin={handleLogin} />
                )}

                {currentView === 'restaurants' && user && (
                    <RestaurantList
                        onSelectRestaurant={(r, item) => handleAddToCart(r, item)}
                        onAddToCart={handleAddToCart}
                    />
                )}

                {currentView === 'order' && user && (
                    <OrderForm
                        restaurant={selectedRestaurant}
                        cartItems={cartItems}
                        user={user}
                        onOrderSuccess={handleOrderSuccess}
                    />
                )}
            </main>

            {/* Footer */}
            <footer style={{ textAlign: 'center', padding: '20px', color: '#888', fontSize: '13px', marginTop: '40px' }}>
                <p>© 2024 FoodExpress | v{APP_VERSION}</p>
                {/* CODE SMELL: Exposing internal config in footer */}
                {DEBUG_MODE && <p style={{ fontSize: '11px' }}>Analytics: {ANALYTICS_KEY}</p>}
            </footer>
        </div>
    );
}

export default App;
