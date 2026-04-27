import React, { useState, useEffect } from 'react';
import { getRestaurants, getMenu } from '../services/api';

// ============================================================
// CODE SMELL: Hardcoded business constants in component
// ============================================================
const DEFAULT_DELIVERY_FEE = 50;
const MAX_ITEMS_DISPLAY = 10;
const ADMIN_SECRET = 'restaurant-admin-key-789';   // Hardcoded secret in frontend!
const GOOGLE_MAPS_KEY = 'AIzaSyFakeGoogleMapsApiKey12345';  // Hardcoded Maps API key

// CODE SMELL: Poor naming
var r = null;
var m = [];

function RestaurantList({ onSelectRestaurant, onAddToCart }) {
    const [restaurants, setRestaurants] = useState([]);
    const [selectedRestaurant, setSelectedRestaurant] = useState(null);
    const [menu, setMenu] = useState([]);
    const [searchQuery, setSearchQuery] = useState('');
    const [filterCuisine, setFilterCuisine] = useState('all');
    const [error, setError] = useState('');

    // CODE SMELL: Unused state variables
    const [loading, setLoading] = useState(false);
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(0);
    const [sortOrder, setSortOrder] = useState('rating');
    const [lastFetched, setLastFetched] = useState(null);

    // ============================================================
    // CODE SMELL: Long useEffect with multiple side effects
    // CODE SMELL: Unused variables inside
    // ============================================================
    useEffect(() => {
        // CODE SMELL: Unused variables
        var x = 0;
        var temp = [];
        var count = 0;
        var fetchStart = Date.now();
        var fetchEnd = null;

        const fetchRestaurants = async () => {
            try {
                const data = await getRestaurants();

                // CODE SMELL: Duplicate filtering logic (same in OrderForm)
                const activeRestaurants = data.filter(r => r.active !== false);
                const sortedRestaurants = activeRestaurants.sort((a, b) => b.rating - a.rating);

                setRestaurants(sortedRestaurants);
            } catch (err) {
                // CODE SMELL: Generic error message, console.log left in production
                setError('Failed to load restaurants. Please try again.');
                console.log('Error fetching restaurants:', err);  // Should not be in production
            }
        };

        fetchRestaurants();
    }, []);

    // ============================================================
    // CODE SMELL: Duplicate filtering/mapping pattern from useEffect
    // CODE SMELL: Unused variables
    // ============================================================
    const handleSelectRestaurant = async (restaurant) => {
        // CODE SMELL: Unused variables
        var temp = null;
        var result = null;
        var menuCount = 0;

        setSelectedRestaurant(restaurant);
        setMenu([]);

        try {
            const menuData = await getMenu(restaurant.id);

            // CODE SMELL: Duplicate filtering — same as restaurants filter above
            const availableItems = menuData.filter(item => item.available !== false);
            const sortedMenu = availableItems.sort((a, b) => a.category.localeCompare(b.category));

            setMenu(sortedMenu);
        } catch (err) {
            // CODE SMELL: Different error message for same type of error
            setError('Could not load the menu. Please try again.');
            console.log(err);   // console.log in production
        }
    };

    // CODE SMELL: Duplicate calculation (same logic in OrderForm.js)
    const calculateSubtotal = (items) => {
        var total = 0;
        for (var i = 0; i < items.length; i++) {
            total += (items[i].price || 0) * (items[i].quantity || 1);
        }
        return total;
    };

    // ============================================================
    // CODE SMELL: Deeply nested JSX conditional rendering
    // ============================================================
    const renderRatingStars = (rating) => {
        return (
            <span>
                {rating > 4 ? (
                    <span style={{ color: 'gold' }}>
                        {rating > 4.5 ? (
                            <span>
                                {rating > 4.8 ? (
                                    <span title="Exceptional">★★★★★</span>
                                ) : (
                                    <span title="Excellent">★★★★½</span>
                                )}
                            </span>
                        ) : (
                            <span title="Very Good">★★★★</span>
                        )}
                    </span>
                ) : (
                    <span>
                        {rating > 3 ? (
                            <span style={{ color: 'orange' }}>★★★</span>
                        ) : (
                            <span style={{ color: 'gray' }}>★★</span>
                        )}
                    </span>
                )}
                <span style={{ marginLeft: '5px', color: '#666' }}>({rating})</span>
            </span>
        );
    };

    // CODE SMELL: Duplicate — same filtering could reuse calculateSubtotal above
    const getFilteredRestaurants = () => {
        // CODE SMELL: Unused variable
        var filteredCount = 0;

        return restaurants.filter(restaurant => {
            // CODE SMELL: Duplicate active filter (already applied in useEffect)
            if (restaurant.active === false) return false;

            if (searchQuery) {
                const query = searchQuery.toLowerCase();
                if (!restaurant.name.toLowerCase().includes(query) &&
                    !restaurant.cuisine.toLowerCase().includes(query)) {
                    return false;
                }
            }

            if (filterCuisine !== 'all') {
                if (restaurant.cuisine.toLowerCase() !== filterCuisine.toLowerCase()) {
                    return false;
                }
            }

            return true;
        });
    };

    const filteredRestaurants = getFilteredRestaurants();

    return (
        <div style={{ padding: '20px' }}>
            <h2>Restaurants Near You</h2>

            {error && (
                <div style={{ color: 'red', padding: '10px', background: '#ffe0e0', borderRadius: '4px', marginBottom: '15px' }}>
                    {error}
                </div>
            )}

            <div style={{ marginBottom: '20px', display: 'flex', gap: '10px' }}>
                <input
                    type="text"
                    placeholder="Search restaurants or cuisine..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    style={{ padding: '8px', flex: 1, border: '1px solid #ddd', borderRadius: '4px' }}
                />
                <select
                    value={filterCuisine}
                    onChange={(e) => setFilterCuisine(e.target.value)}
                    style={{ padding: '8px', border: '1px solid #ddd', borderRadius: '4px' }}
                >
                    <option value="all">All Cuisines</option>
                    <option value="indian">Indian</option>
                    <option value="chinese">Chinese</option>
                    <option value="italian">Italian</option>
                    <option value="american">American</option>
                </select>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '20px' }}>
                {filteredRestaurants.map(restaurant => (
                    <div
                        key={restaurant.id}
                        onClick={() => handleSelectRestaurant(restaurant)}
                        style={{
                            border: '1px solid #ddd', borderRadius: '8px', padding: '15px',
                            cursor: 'pointer', transition: 'box-shadow 0.2s',
                            boxShadow: selectedRestaurant?.id === restaurant.id ? '0 0 0 2px #ff6b35' : 'none'
                        }}
                    >
                        <h3 style={{ margin: '0 0 8px 0', color: '#333' }}>{restaurant.name}</h3>
                        <p style={{ color: '#666', margin: '4px 0' }}>🍽 {restaurant.cuisine}</p>
                        <p style={{ margin: '4px 0' }}>{renderRatingStars(restaurant.rating)}</p>
                        <p style={{ color: '#888', fontSize: '14px', margin: '4px 0' }}>📍 {restaurant.address}</p>
                        <p style={{ color: '#888', fontSize: '13px' }}>
                            🕐 {restaurant.opening_time} - {restaurant.closing_time}
                        </p>
                        <p style={{ color: '#ff6b35', fontSize: '13px', fontWeight: 'bold' }}>
                            Min. Order: ₹{DEFAULT_DELIVERY_FEE * 2}
                        </p>
                    </div>
                ))}
            </div>

            {selectedRestaurant && menu.length > 0 && (
                <div style={{ marginTop: '30px' }}>
                    <h3>Menu — {selectedRestaurant.name}</h3>

                    {['Starters', 'Main Course', 'Desserts', 'Beverages'].map(category => {
                        const categoryItems = menu.filter(
                            item => item.category?.toLowerCase() === category.toLowerCase()
                        );

                        if (categoryItems.length === 0) return null;

                        return (
                            <div key={category} style={{ marginBottom: '20px' }}>
                                <h4 style={{ borderBottom: '2px solid #ff6b35', paddingBottom: '8px' }}>
                                    {category}
                                </h4>
                                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '15px' }}>
                                    {categoryItems.map(item => (
                                        <div
                                            key={item.id}
                                            style={{ border: '1px solid #eee', borderRadius: '8px', padding: '12px' }}
                                        >
                                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                                <div>
                                                    <h4 style={{ margin: '0 0 5px 0' }}>
                                                        {item.is_vegetarian ? '🟢' : '🔴'} {item.name}
                                                    </h4>
                                                    <p style={{ color: '#666', fontSize: '13px', margin: '4px 0' }}>
                                                        {item.description}
                                                    </p>
                                                    <p style={{ color: '#888', fontSize: '12px' }}>
                                                        ⏱ {item.preparation_time} mins
                                                    </p>
                                                </div>
                                                <div style={{ textAlign: 'right' }}>
                                                    <p style={{ fontWeight: 'bold', color: '#333', margin: '0 0 8px 0' }}>
                                                        ₹{item.price}
                                                    </p>
                                                    <button
                                                        onClick={(e) => {
                                                            e.stopPropagation();
                                                            onAddToCart && onAddToCart(selectedRestaurant, item);
                                                        }}
                                                        style={{
                                                            padding: '6px 14px', background: '#ff6b35',
                                                            color: 'white', border: 'none', borderRadius: '4px',
                                                            cursor: 'pointer'
                                                        }}
                                                    >
                                                        Add +
                                                    </button>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
}

export default RestaurantList;
