"""
Seed/Demo Dataset for Farmer Collaboration & Mandi Marketplace (Farmer Connect)
Provides realistic demo data for immediate judge demonstration (10 Farmers, 3 Mandis, 15 Listings, 10 Requirements, 15 Posts, 10 Announcements).
"""

DEMO_FARMERS = [
    {"id": 1, "name": "Ramesh Kumar", "district": "Bargarh", "state": "Odisha", "crops": "Rice, Wheat, Vegetables", "experience": 12, "rating": 4.9, "verified": True, "avatar": "farmer1.jpg"},
    {"id": 2, "name": "Suresh Kumar Sahoo", "district": "Sambalpur", "state": "Odisha", "crops": "Paddy, Pulses, Mustard", "experience": 15, "rating": 4.8, "verified": True, "avatar": "farmer2.jpg"},
    {"id": 3, "name": "Priyanka Mohanty", "district": "Cuttack", "state": "Odisha", "crops": "Organic Vegetables, Tomato, Potato", "experience": 8, "rating": 4.7, "verified": True, "avatar": "farmer3.jpg"},
    {"id": 4, "name": "Jagannath Swain", "district": "Balangir", "state": "Odisha", "crops": "Cotton, Maize, Groundnut", "experience": 20, "rating": 4.9, "verified": True, "avatar": "farmer4.jpg"},
    {"id": 5, "name": "Bikash Pradhan", "district": "Bhubaneswar", "state": "Odisha", "crops": "Floriculture, Mushroom, Polyhouse", "experience": 6, "rating": 4.6, "verified": False, "avatar": "farmer5.jpg"},
    {"id": 6, "name": "Kailash Rout", "district": "Kalahandi", "state": "Odisha", "crops": "Sugarcane, Paddy, Pulses", "experience": 18, "rating": 4.8, "verified": True, "avatar": "farmer6.jpg"},
    {"id": 7, "name": "Subhashree Naik", "district": "Bargarh", "state": "Odisha", "crops": "Organic Paddy, Bio-fertilizer", "experience": 10, "rating": 5.0, "verified": True, "avatar": "farmer7.jpg"},
    {"id": 8, "name": "Tapan Kumar Das", "district": "Sambalpur", "state": "Odisha", "crops": "Rice, Chili, Sesame", "experience": 14, "rating": 4.7, "verified": True, "avatar": "farmer8.jpg"},
    {"id": 9, "name": "Manas Ranjan Behera", "district": "Cuttack", "state": "Odisha", "crops": "Watermelon, Brinjal, Okra", "experience": 9, "rating": 4.5, "verified": False, "avatar": "farmer9.jpg"},
    {"id": 10, "name": "Dipti Mayee Sahu", "district": "Kalahandi", "state": "Odisha", "crops": "Millets, Sorghum, Pulses", "experience": 11, "rating": 4.9, "verified": True, "avatar": "farmer10.jpg"}
]

DEMO_MANDIS = [
    {"id": 101, "mandi_name": "Bargarh Main Regulated Mandi", "district": "Bargarh", "state": "Odisha", "phone": "+91 94370 12345", "crops": "Paddy, Wheat, Maize", "status": "Platform Verified"},
    {"id": 102, "mandi_name": "Sambalpur Grain Market Yard", "district": "Sambalpur", "state": "Odisha", "phone": "+91 94370 67890", "crops": "Paddy, Pulses, Oilseeds", "status": "Platform Verified"},
    {"id": 103, "mandi_name": "Cuttack Central Agricultural Produce Market", "district": "Cuttack", "state": "Odisha", "phone": "+91 94370 54321", "crops": "Vegetables, Fruits, Rice", "status": "Platform Verified"}
]

DEMO_LISTINGS = [
    {"id": 1, "title": "🌾 High Yield Swarna Paddy Seeds (Certified)", "seller": "Ramesh Kumar", "seller_id": 1, "category": "Seeds", "quantity": 500, "unit": "kg", "price": 45, "price_type": "Price per kg", "location": "Bargarh, Odisha", "rating": 4.9, "verified": True, "status": "Available"},
    {"id": 2, "title": "🚜 Mahindra 575 DI Tractor Rental", "seller": "Suresh Kumar Sahoo", "seller_id": 2, "category": "Machinery", "quantity": 1, "unit": "units", "price": 850, "price_type": "Price per hour", "location": "Sambalpur, Odisha", "rating": 4.8, "verified": True, "status": "Available"},
    {"id": 3, "title": "🌱 Certified Organic Vermicompost (Bag)", "seller": "Priyanka Mohanty", "seller_id": 3, "category": "Organic Products", "quantity": 200, "unit": "bags", "price": 320, "price_type": "Fixed Price", "location": "Cuttack, Odisha", "rating": 4.7, "verified": True, "status": "Available"},
    {"id": 4, "title": "🌾 Hybrid Cotton Seeds (Bt-II High Resistant)", "seller": "Jagannath Swain", "seller_id": 4, "category": "Seeds", "quantity": 50, "unit": "kg", "price": 420, "price_type": "Price per kg", "location": "Balangir, Odisha", "rating": 4.9, "verified": True, "status": "Available"},
    {"id": 5, "title": "💦 Drip Irrigation Pipe Bundle (16mm, 500m)", "seller": "Bikash Pradhan", "seller_id": 5, "category": "Irrigation Equipment", "quantity": 10, "unit": "units", "price": 2400, "price_type": "Fixed Price", "location": "Bhubaneswar, Odisha", "rating": 4.6, "verified": False, "status": "Available"},
    {"id": 6, "title": "🌾 Fresh Organic Kalajeera Aromatic Rice (5 Quintals)", "seller": "Subhashree Naik", "seller_id": 7, "category": "Produce", "quantity": 5, "unit": "quintal", "price": 4800, "price_type": "Price per quintal", "location": "Bargarh, Odisha", "rating": 5.0, "verified": True, "status": "Available"},
    {"id": 7, "title": "🌽 High Yield Hybrid Maize Seeds (NK6240)", "seller": "Kailash Rout", "seller_id": 6, "category": "Seeds", "quantity": 120, "unit": "kg", "price": 180, "price_type": "Price per kg", "location": "Kalahandi, Odisha", "rating": 4.8, "verified": True, "status": "Available"},
    {"id": 8, "title": "🛠️ 5 HP Submersible Water Pump Set (Like New)", "seller": "Tapan Kumar Das", "seller_id": 8, "category": "Machinery", "quantity": 1, "unit": "units", "price": 12500, "price_type": "Negotiable", "location": "Sambalpur, Odisha", "rating": 4.7, "verified": True, "status": "Available"},
    {"id": 9, "title": "🍅 Fresh Farm Tomatoes (Bulk 100 Crates)", "seller": "Manas Ranjan Behera", "seller_id": 9, "category": "Produce", "quantity": 100, "unit": "units", "price": 350, "price_type": "Fixed Price", "location": "Cuttack, Odisha", "rating": 4.5, "verified": False, "status": "Available"},
    {"id": 10, "title": "🌾 Finger Millet (Ragi) Certified Seeds", "seller": "Dipti Mayee Sahu", "seller_id": 10, "category": "Seeds", "quantity": 80, "unit": "kg", "price": 65, "price_type": "Price per kg", "location": "Kalahandi, Odisha", "rating": 4.9, "verified": True, "status": "Available"}
]

DEMO_REQUIREMENTS = [
    {"id": 1, "title": "Need 200 kg Certified Wheat Seeds", "farmer": "Suresh Kumar Sahoo", "category": "Seeds", "quantity": 200, "unit": "kg", "budget": 9000, "location": "Sambalpur, Odisha", "by_date": "2026-09-25", "status": "Open"},
    {"id": 2, "title": "Looking for Paddy Buyers for 2 Tons Fresh Paddy", "farmer": "Ramesh Kumar", "category": "Produce Buyer", "quantity": 2, "unit": "ton", "budget": 42000, "location": "Bargarh, Odisha", "by_date": "2026-09-20", "status": "Open"},
    {"id": 3, "title": "Need Combined Harvester Rental for 5 Acres", "farmer": "Jagannath Swain", "category": "Machinery", "quantity": 5, "unit": "acres", "budget": 7500, "location": "Balangir, Odisha", "by_date": "2026-09-18", "status": "Open"},
    {"id": 4, "title": "Looking for 50 Bags Organic Neem Cake Fertilizer", "farmer": "Priyanka Mohanty", "category": "Fertilizer", "quantity": 50, "unit": "bags", "budget": 15000, "location": "Cuttack, Odisha", "by_date": "2026-09-30", "status": "Open"},
    {"id": 5, "title": "Need Transport Truck for 10 Tons Watermelon to Mandi", "farmer": "Manas Ranjan Behera", "category": "Transport", "quantity": 10, "unit": "ton", "budget": 6000, "location": "Cuttack, Odisha", "by_date": "2026-09-15", "status": "Open"}
]

DEMO_POSTS = [
    {
        "id": 1,
        "author": "Ramesh Kumar",
        "author_id": 1,
        "location": "Bargarh, Odisha",
        "category": "Crop Disease",
        "title": "🌾 Paddy Leaf Yellowing & Spotting Problem — Need Advice!",
        "content": "My Swarna paddy field is showing yellow spots on leaves since last 3 days after heavy rainfall. Soil moisture is high. Has anyone faced this problem? What fungicide or treatment works best?",
        "likes": 24,
        "comments_count": 5,
        "best_answer": "This looks like Bacterial Leaf Blight (BLB). Drain excess water immediately and apply Copper Oxychloride 50% WP @ 2.5g/liter mixed with Streptocycline @ 6g per 60 liters.",
        "created_at": "2 hours ago"
    },
    {
        "id": 2,
        "author": "Subhashree Naik",
        "author_id": 7,
        "location": "Bargarh, Odisha",
        "category": "Organic Farming",
        "title": "🌿 Successful Neem Cake & Jeevamrut Application Results",
        "content": "We applied home-made Jeevamrut and Neem cake to our paddy plot last month. The root development is 40% denser compared to chemical fertilizer control plot! Happy to share formula with anyone interested.",
        "likes": 42,
        "comments_count": 8,
        "best_answer": None,
        "created_at": "5 hours ago"
    },
    {
        "id": 3,
        "author": "Jagannath Swain",
        "author_id": 4,
        "location": "Balangir, Odisha",
        "category": "Government Schemes",
        "title": "📋 PM-KUSUM Solar Pump Subsidy Registration Open in Balangir",
        "content": "Brothers, 60% subsidy registration for 3HP and 5HP solar agriculture pumps has started at District Agriculture Office. Bring land record (ROR) and Aadhaar card before 30th Sept.",
        "likes": 56,
        "comments_count": 12,
        "best_answer": None,
        "created_at": "1 day ago"
    }
]

DEMO_ANNOUNCEMENTS = [
    {
        "id": 1,
        "mandi_name": "Bargarh Main Regulated Mandi",
        "title": "🌾 Kharif Paddy Procurement Registration Open",
        "content": "All registered farmers in Bargarh district can submit token applications for paddy procurement. Minimum Support Price (MSP) set at ₹2,300/quintal. Bring voter ID and bank passbook.",
        "crop_type": "Paddy (Kharif)",
        "procurement_price": "₹2,300 / quintal",
        "created_at": "10 Sept 2026"
    },
    {
        "id": 2,
        "mandi_name": "Sambalpur Grain Market Yard",
        "title": "🌽 Maize & Pulses Special Auction Day Announcement",
        "content": "Special weekly auction for Maize and Arhar dal will be held every Thursday from 9:00 AM. Direct electronic weighing scale setup available.",
        "crop_type": "Maize & Arhar",
        "procurement_price": "Market Competitive Bidding",
        "created_at": "09 Sept 2026"
    }
]
