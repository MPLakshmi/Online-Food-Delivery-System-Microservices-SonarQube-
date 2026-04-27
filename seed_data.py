from pymongo import MongoClient
import datetime, os

uri = os.environ.get('MONGO_URI', 'mongodb://admin:password123@localhost:27017/')
client = MongoClient(uri)
db = client['restaurantdb']
restaurants_col = db['restaurants']
menus_col = db['menus']

restaurants_col.delete_many({})
menus_col.delete_many({})
now = datetime.datetime.utcnow()

r1 = restaurants_col.insert_one({'name': 'Spice Garden', 'email': 'spice@garden.com', 'cuisine': 'Indian', 'address': '12 MG Road, Bangalore', 'phone': '0801112222', 'rating': 4.7, 'active': True, 'opening_time': '09:00', 'closing_time': '23:00', 'delivery_radius': 8, 'minimum_order': 150, 'created_at': now})
r2 = restaurants_col.insert_one({'name': 'Dragon Wok', 'email': 'dragon@wok.com', 'cuisine': 'Chinese', 'address': '45 Brigade Road, Bangalore', 'phone': '0803334444', 'rating': 4.4, 'active': True, 'opening_time': '11:00', 'closing_time': '22:30', 'delivery_radius': 6, 'minimum_order': 200, 'created_at': now})
r3 = restaurants_col.insert_one({'name': 'Pizza Roma', 'email': 'pizza@roma.com', 'cuisine': 'Italian', 'address': '78 Koramangala, Bangalore', 'phone': '0805556666', 'rating': 4.5, 'active': True, 'opening_time': '10:00', 'closing_time': '23:30', 'delivery_radius': 10, 'minimum_order': 250, 'created_at': now})
r4 = restaurants_col.insert_one({'name': 'Burger Barn', 'email': 'burger@barn.com', 'cuisine': 'American', 'address': '90 Indiranagar, Bangalore', 'phone': '0807778888', 'rating': 4.2, 'active': True, 'opening_time': '10:00', 'closing_time': '23:59', 'delivery_radius': 7, 'minimum_order': 180, 'created_at': now})

sid = str(r1.inserted_id)
did = str(r2.inserted_id)
pid = str(r3.inserted_id)
bid = str(r4.inserted_id)

menus = [
    {'restaurant_id': sid, 'name': 'Butter Chicken', 'description': 'Creamy tomato-based chicken curry', 'price': 320, 'category': 'Main Course', 'available': True, 'preparation_time': 25, 'is_vegetarian': False, 'created_at': now},
    {'restaurant_id': sid, 'name': 'Paneer Tikka Masala', 'description': 'Grilled paneer in spiced tomato gravy', 'price': 280, 'category': 'Main Course', 'available': True, 'preparation_time': 20, 'is_vegetarian': True, 'created_at': now},
    {'restaurant_id': sid, 'name': 'Chicken Biryani', 'description': 'Fragrant basmati rice with tender chicken', 'price': 350, 'category': 'Main Course', 'available': True, 'preparation_time': 30, 'is_vegetarian': False, 'created_at': now},
    {'restaurant_id': sid, 'name': 'Samosa (2 pcs)', 'description': 'Crispy potato-filled pastry with chutney', 'price': 80, 'category': 'Starters', 'available': True, 'preparation_time': 10, 'is_vegetarian': True, 'created_at': now},
    {'restaurant_id': sid, 'name': 'Garlic Naan', 'description': 'Soft flatbread with garlic and butter', 'price': 60, 'category': 'Starters', 'available': True, 'preparation_time': 10, 'is_vegetarian': True, 'created_at': now},
    {'restaurant_id': sid, 'name': 'Gulab Jamun', 'description': 'Sweet milk dumplings in sugar syrup', 'price': 120, 'category': 'Desserts', 'available': True, 'preparation_time': 5, 'is_vegetarian': True, 'created_at': now},
    {'restaurant_id': sid, 'name': 'Mango Lassi', 'description': 'Chilled mango yoghurt drink', 'price': 90, 'category': 'Beverages', 'available': True, 'preparation_time': 5, 'is_vegetarian': True, 'created_at': now},
    {'restaurant_id': did, 'name': 'Kung Pao Chicken', 'description': 'Spicy stir-fried chicken with peanuts', 'price': 340, 'category': 'Main Course', 'available': True, 'preparation_time': 20, 'is_vegetarian': False, 'created_at': now},
    {'restaurant_id': did, 'name': 'Veg Fried Rice', 'description': 'Wok-tossed rice with fresh vegetables', 'price': 220, 'category': 'Main Course', 'available': True, 'preparation_time': 15, 'is_vegetarian': True, 'created_at': now},
    {'restaurant_id': did, 'name': 'Hakka Noodles', 'description': 'Stir-fried noodles with soy sauce and veggies', 'price': 200, 'category': 'Main Course', 'available': True, 'preparation_time': 15, 'is_vegetarian': True, 'created_at': now},
    {'restaurant_id': did, 'name': 'Dim Sum Basket', 'description': 'Steamed dumplings with dipping sauce', 'price': 250, 'category': 'Starters', 'available': True, 'preparation_time': 15, 'is_vegetarian': False, 'created_at': now},
    {'restaurant_id': did, 'name': 'Spring Rolls (4 pcs)', 'description': 'Crispy rolls filled with spiced vegetables', 'price': 180, 'category': 'Starters', 'available': True, 'preparation_time': 12, 'is_vegetarian': True, 'created_at': now},
    {'restaurant_id': did, 'name': 'Toffee Apple', 'description': 'Caramel coated apple fritters', 'price': 160, 'category': 'Desserts', 'available': True, 'preparation_time': 10, 'is_vegetarian': True, 'created_at': now},
    {'restaurant_id': pid, 'name': 'Margherita Pizza', 'description': 'Classic tomato sauce, mozzarella and basil', 'price': 380, 'category': 'Main Course', 'available': True, 'preparation_time': 20, 'is_vegetarian': True, 'created_at': now},
    {'restaurant_id': pid, 'name': 'Pepperoni Pizza', 'description': 'Loaded with spicy pepperoni and cheese', 'price': 450, 'category': 'Main Course', 'available': True, 'preparation_time': 20, 'is_vegetarian': False, 'created_at': now},
    {'restaurant_id': pid, 'name': 'Pasta Arrabbiata', 'description': 'Penne in spicy tomato and garlic sauce', 'price': 320, 'category': 'Main Course', 'available': True, 'preparation_time': 15, 'is_vegetarian': True, 'created_at': now},
    {'restaurant_id': pid, 'name': 'Garlic Bread', 'description': 'Toasted ciabatta with garlic herb butter', 'price': 150, 'category': 'Starters', 'available': True, 'preparation_time': 10, 'is_vegetarian': True, 'created_at': now},
    {'restaurant_id': pid, 'name': 'Tiramisu', 'description': 'Classic Italian coffee and mascarpone dessert', 'price': 220, 'category': 'Desserts', 'available': True, 'preparation_time': 5, 'is_vegetarian': True, 'created_at': now},
    {'restaurant_id': pid, 'name': 'Italian Soda', 'description': 'Sparkling flavoured soda with citrus', 'price': 120, 'category': 'Beverages', 'available': True, 'preparation_time': 3, 'is_vegetarian': True, 'created_at': now},
    {'restaurant_id': bid, 'name': 'Classic Beef Burger', 'description': 'Juicy beef patty with lettuce, tomato and cheese', 'price': 350, 'category': 'Main Course', 'available': True, 'preparation_time': 15, 'is_vegetarian': False, 'created_at': now},
    {'restaurant_id': bid, 'name': 'Veggie Burger', 'description': 'Crispy veggie patty with fresh toppings', 'price': 280, 'category': 'Main Course', 'available': True, 'preparation_time': 12, 'is_vegetarian': True, 'created_at': now},
    {'restaurant_id': bid, 'name': 'Loaded Fries', 'description': 'Fries topped with cheese sauce and jalapenos', 'price': 200, 'category': 'Starters', 'available': True, 'preparation_time': 10, 'is_vegetarian': True, 'created_at': now},
    {'restaurant_id': bid, 'name': 'Onion Rings', 'description': 'Golden crispy battered onion rings', 'price': 160, 'category': 'Starters', 'available': True, 'preparation_time': 8, 'is_vegetarian': True, 'created_at': now},
    {'restaurant_id': bid, 'name': 'Brownie Sundae', 'description': 'Warm chocolate brownie with vanilla ice cream', 'price': 250, 'category': 'Desserts', 'available': True, 'preparation_time': 5, 'is_vegetarian': True, 'created_at': now},
    {'restaurant_id': bid, 'name': 'Chocolate Milkshake', 'description': 'Thick and creamy chocolate milkshake', 'price': 180, 'category': 'Beverages', 'available': True, 'preparation_time': 5, 'is_vegetarian': True, 'created_at': now},
]

menus_col.insert_many(menus)
print(f'Done: 4 restaurants, {len(menus)} menu items')
print(f'Spice Garden ID: {sid}')
print(f'Dragon Wok ID:   {did}')
print(f'Pizza Roma ID:   {pid}')
print(f'Burger Barn ID:  {bid}')
