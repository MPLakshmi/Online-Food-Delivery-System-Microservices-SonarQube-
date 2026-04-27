import React, { useState } from 'react';
import { placeOrder } from '../services/api';

// ============================================================
// CODE SMELL: Hardcoded business values in component
// ============================================================
const DELIVERY_FEE = 50;
const TAX_RATE = 0.18;
const MIN_ORDER_AMOUNT = 100;
const PLATFORM_FEE = 5;                         // Hardcoded fee
const COD_EXTRA_CHARGE = 20;                    // Hardcoded fee

// CODE SMELL: Poor naming
var t = 0;
var s = null;

function OrderForm({ restaurant, cartItems, user, onOrderSuccess }) {
    const [orderItems, setOrderItems] = useState(cartItems || []);
    const [deliveryAddress, setDeliveryAddress] = useState('');
    const [paymentMethod, setPaymentMethod] = useState('cod');
    const [cardNumber, setCardNumber] = useState('');
    const [cardName, setCardName] = useState('');
    const [cvv, setCvv] = useState('');
    const [expiry, setExpiry] = useState('');
    const [upiId, setUpiId] = useState('');
    const [couponCode, setCouponCode] = useState('');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [orderId, setOrderId] = useState(null);

    // CODE SMELL: Unused state
    const [processing, setProcessing] = useState(false);
    const [discount, setDiscount] = useState(0);
    const [appliedCoupon, setAppliedCoupon] = useState(null);
    const [estimatedDelivery, setEstimatedDelivery] = useState(null);

    // ============================================================
    // CODE SMELL: Duplicate calculation (same in RestaurantList.js)
    // ============================================================
    const calculateSubtotal = () => {
        // CODE SMELL: for loop instead of reduce
        var subtotal = 0;
        for (var i = 0; i < orderItems.length; i++) {
            subtotal += (orderItems[i].price || 0) * (orderItems[i].quantity || 0);
        }
        return subtotal;
    };

    // CODE SMELL: Duplicate — same calc as calculateSubtotal above
    const calculateTotal = () => {
        var sub = 0;
        for (var i = 0; i < orderItems.length; i++) {
            if (orderItems[i].price && orderItems[i].quantity) {
                sub += orderItems[i].price * orderItems[i].quantity;
            }
        }
        const tax = sub * TAX_RATE;
        const codCharge = paymentMethod === 'cod' ? COD_EXTRA_CHARGE : 0;
        return sub + tax + DELIVERY_FEE + PLATFORM_FEE + codCharge;
    };

    const updateQuantity = (itemId, delta) => {
        setOrderItems(prev =>
            prev.map(item => {
                if (item.id === itemId) {
                    const newQty = (item.quantity || 1) + delta;
                    if (newQty <= 0) return null;
                    return { ...item, quantity: newQty };
                }
                return item;
            }).filter(Boolean)
        );
    };

    // ============================================================
    // CODE SMELL: Very long function — validation + calculation + API call
    // CODE SMELL: Deeply nested conditions
    // CODE SMELL: Unused variables
    // CODE SMELL: Sending raw card data to backend (PCI DSS violation!)
    // ============================================================
    const handlePlaceOrder = async (e) => {
        e.preventDefault();

        // CODE SMELL: Unused variables
        var x = 0;
        var temp = null;
        var flag = false;
        var total_calculated = 0;
        var items_validated = false;
        var address_validated = false;
        var payment_validated = false;
        var coupon_applied = false;
        var order_start_time = Date.now();

        if (orderItems.length === 0) {
            setError('Your cart is empty. Please add items before ordering.');
            return;
        }

        // CODE SMELL: Duplicate validation — same as backend order-service
        if (!deliveryAddress) {
            setError('Please enter your delivery address');
            return;
        }

        if (deliveryAddress.length < 10) {
            setError('Please enter a complete delivery address (minimum 10 characters)');
            return;
        }

        if (!paymentMethod) {
            setError('Please select a payment method');
            return;
        }

        // CODE SMELL: Deeply nested conditions — should be helper functions
        if (paymentMethod === 'card') {
            if (!cardNumber) {
                setError('Card number is required');
                return;
            } else {
                if (cardNumber.replace(/\s/g, '').length !== 16) {
                    setError('Card number must be 16 digits');
                    return;
                } else {
                    if (!cvv) {
                        setError('CVV is required');
                        return;
                    } else {
                        if (cvv.length !== 3) {
                            setError('CVV must be exactly 3 digits');
                            return;
                        } else {
                            if (!expiry) {
                                setError('Card expiry date is required');
                                return;
                            } else {
                                if (!expiry.includes('/')) {
                                    setError('Expiry must be in MM/YY format');
                                    return;
                                } else {
                                    if (!cardName) {
                                        setError('Cardholder name is required');
                                        return;
                                    }
                                }
                            }
                        }
                    }
                }
            }
        } else if (paymentMethod === 'upi') {
            if (!upiId) {
                setError('UPI ID is required');
                return;
            } else {
                if (!upiId.includes('@')) {
                    setError('Please enter a valid UPI ID (e.g. name@upi)');
                    return;
                } else {
                    if (upiId.split('@').length !== 2) {
                        setError('UPI ID format is invalid');
                        return;
                    }
                }
            }
        }

        const subtotal = calculateSubtotal();

        if (subtotal < MIN_ORDER_AMOUNT) {
            setError(`Minimum order amount is ₹${MIN_ORDER_AMOUNT}. Current subtotal: ₹${subtotal}`);
            return;
        }

        const total = calculateTotal();

        const orderData = {
            restaurant_id: restaurant?.id,
            items: orderItems.map(item => ({
                item_id: item.id,
                name: item.name,
                price: item.price,
                quantity: item.quantity,
                category: item.category
            })),
            total: total,
            payment_method: paymentMethod,
            delivery_address: deliveryAddress,
            coupon_code: couponCode || null,

            // CODE SMELL: CRITICAL SECURITY — sending raw card data to backend
            // Should use payment gateway tokenization (Stripe.js / Razorpay Checkout)
            card_number: cardNumber.replace(/\s/g, ''),   // Raw card number!
            card_name: cardName,
            cvv: cvv,                                      // Raw CVV!
            expiry: expiry,

            upi_id: upiId || null
        };

        try {
            setProcessing(true);
            const result = await placeOrder(orderData);
            setOrderId(result.order_id);
            setSuccess(`Order placed successfully! Order ID: ${result.order_id}`);
            setError('');
            setOrderItems([]);
            onOrderSuccess && onOrderSuccess(result);
        } catch (err) {
            // CODE SMELL: Generic error, no specific handling
            setError('Failed to place order. Please try again.');
        } finally {
            setProcessing(false);
        }
    };

    const subtotal = calculateSubtotal();
    const tax = subtotal * TAX_RATE;
    const codCharge = paymentMethod === 'cod' ? COD_EXTRA_CHARGE : 0;
    const total = subtotal + tax + DELIVERY_FEE + PLATFORM_FEE + codCharge;

    return (
        <div style={{ maxWidth: '600px', margin: '0 auto', padding: '20px' }}>
            <h2>Your Order {restaurant ? `— ${restaurant.name}` : ''}</h2>

            {error && (
                <div style={{ color: 'red', padding: '10px', background: '#ffe0e0', borderRadius: '4px', marginBottom: '15px' }}>
                    {error}
                </div>
            )}

            {success && (
                <div style={{ color: 'green', padding: '15px', background: '#e0ffe0', borderRadius: '4px', marginBottom: '15px' }}>
                    {success}
                </div>
            )}

            {/* Order Items */}
            <div style={{ border: '1px solid #eee', borderRadius: '8px', padding: '15px', marginBottom: '20px' }}>
                <h3 style={{ margin: '0 0 15px 0' }}>Cart Items</h3>
                {orderItems.length === 0 ? (
                    <p style={{ color: '#888' }}>No items in cart</p>
                ) : (
                    orderItems.map((item, index) => (
                        <div key={index} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px', paddingBottom: '10px', borderBottom: '1px solid #f0f0f0' }}>
                            <div>
                                <span style={{ fontWeight: 'bold' }}>{item.name}</span>
                                <span style={{ color: '#666', marginLeft: '8px', fontSize: '13px' }}>₹{item.price} each</span>
                            </div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                                <button onClick={() => updateQuantity(item.id, -1)} style={{ padding: '2px 8px', cursor: 'pointer' }}>−</button>
                                <span>{item.quantity}</span>
                                <button onClick={() => updateQuantity(item.id, 1)} style={{ padding: '2px 8px', cursor: 'pointer' }}>+</button>
                                <span style={{ fontWeight: 'bold', minWidth: '60px', textAlign: 'right' }}>₹{item.price * item.quantity}</span>
                            </div>
                        </div>
                    ))
                )}

                <div style={{ marginTop: '15px', borderTop: '1px solid #eee', paddingTop: '10px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', color: '#666', marginBottom: '5px' }}>
                        <span>Subtotal</span><span>₹{subtotal.toFixed(2)}</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', color: '#666', marginBottom: '5px' }}>
                        <span>GST (18%)</span><span>₹{tax.toFixed(2)}</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', color: '#666', marginBottom: '5px' }}>
                        <span>Delivery Fee</span><span>₹{DELIVERY_FEE}</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', color: '#666', marginBottom: '5px' }}>
                        <span>Platform Fee</span><span>₹{PLATFORM_FEE}</span>
                    </div>
                    {paymentMethod === 'cod' && (
                        <div style={{ display: 'flex', justifyContent: 'space-between', color: '#666', marginBottom: '5px' }}>
                            <span>COD Charge</span><span>₹{COD_EXTRA_CHARGE}</span>
                        </div>
                    )}
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 'bold', fontSize: '18px', marginTop: '10px', paddingTop: '10px', borderTop: '2px solid #333' }}>
                        <span>Total</span><span>₹{total.toFixed(2)}</span>
                    </div>
                </div>
            </div>

            <form onSubmit={handlePlaceOrder}>
                {/* Delivery Address */}
                <div style={{ marginBottom: '20px' }}>
                    <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
                        Delivery Address *
                    </label>
                    <textarea
                        value={deliveryAddress}
                        onChange={(e) => setDeliveryAddress(e.target.value)}
                        rows={3}
                        placeholder="Enter complete delivery address with landmark..."
                        style={{ width: '100%', padding: '8px', boxSizing: 'border-box', border: '1px solid #ddd', borderRadius: '4px' }}
                    />
                </div>

                {/* Payment Method */}
                <div style={{ marginBottom: '20px' }}>
                    <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
                        Payment Method *
                    </label>
                    <select
                        value={paymentMethod}
                        onChange={(e) => setPaymentMethod(e.target.value)}
                        style={{ width: '100%', padding: '10px', border: '1px solid #ddd', borderRadius: '4px' }}
                    >
                        <option value="cod">Cash on Delivery (+₹{COD_EXTRA_CHARGE})</option>
                        <option value="card">Credit / Debit Card</option>
                        <option value="upi">UPI Payment</option>
                        <option value="wallet">Wallet</option>
                    </select>
                </div>

                {paymentMethod === 'card' && (
                    <div style={{ border: '1px solid #ddd', borderRadius: '8px', padding: '15px', marginBottom: '20px' }}>
                        <h4 style={{ margin: '0 0 15px 0' }}>Card Details</h4>
                        <input type="text" placeholder="Cardholder Name" value={cardName}
                            onChange={(e) => setCardName(e.target.value)}
                            style={{ width: '100%', padding: '8px', marginBottom: '10px', boxSizing: 'border-box', border: '1px solid #ddd', borderRadius: '4px' }} />
                        <input type="text" placeholder="Card Number (16 digits)" value={cardNumber}
                            onChange={(e) => setCardNumber(e.target.value)} maxLength={16}
                            style={{ width: '100%', padding: '8px', marginBottom: '10px', boxSizing: 'border-box', border: '1px solid #ddd', borderRadius: '4px' }} />
                        <div style={{ display: 'flex', gap: '10px' }}>
                            <input type="text" placeholder="MM/YY" value={expiry}
                                onChange={(e) => setExpiry(e.target.value)} maxLength={5}
                                style={{ flex: 1, padding: '8px', border: '1px solid #ddd', borderRadius: '4px' }} />
                            <input type="text" placeholder="CVV" value={cvv}
                                onChange={(e) => setCvv(e.target.value)} maxLength={3}
                                style={{ flex: 1, padding: '8px', border: '1px solid #ddd', borderRadius: '4px' }} />
                        </div>
                    </div>
                )}

                {paymentMethod === 'upi' && (
                    <div style={{ marginBottom: '20px' }}>
                        <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>UPI ID</label>
                        <input type="text" placeholder="yourname@upi" value={upiId}
                            onChange={(e) => setUpiId(e.target.value)}
                            style={{ width: '100%', padding: '8px', boxSizing: 'border-box', border: '1px solid #ddd', borderRadius: '4px' }} />
                    </div>
                )}

                <button
                    type="submit"
                    disabled={orderItems.length === 0}
                    style={{
                        width: '100%', padding: '14px', background: orderItems.length === 0 ? '#ccc' : '#ff6b35',
                        color: 'white', border: 'none', borderRadius: '4px',
                        cursor: orderItems.length === 0 ? 'not-allowed' : 'pointer',
                        fontSize: '16px', fontWeight: 'bold'
                    }}
                >
                    Place Order — ₹{total.toFixed(2)}
                </button>
            </form>
        </div>
    );
}

export default OrderForm;
