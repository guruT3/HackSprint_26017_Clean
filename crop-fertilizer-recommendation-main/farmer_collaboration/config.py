import os

class CollaborationConfig:
    """Configuration parameters for Farmer Collaboration & Mandi Marketplace."""
    
    SECRET_KEY = os.getenv("SECRET_KEY", "farmer_connect_secret_2026")
    UPLOAD_FOLDER = os.getenv("FARMER_CONNECT_UPLOADS", "static/uploads/farmer_collaboration")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB upload limit
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
    
    # Agronomic Categories
    COMMUNITY_CATEGORIES = [
        "General Farming", "Crop Problems", "Seeds", "Fertilizers",
        "Irrigation", "Machinery", "Market Prices", "Government Schemes",
        "Weather", "Organic Farming", "Crop Disease", "Buy/Sell", "Mandi", "Other"
    ]
    
    MARKETPLACE_CATEGORIES = [
        "Seeds", "Fertilizers", "Pesticides", "Farming Equipment",
        "Machinery", "Produce", "Organic Products", "Animal Feed",
        "Irrigation Equipment", "Other Approved Agricultural Items"
    ]
    
    REQUIREMENT_CATEGORIES = [
        "Seeds", "Fertilizer", "Machinery", "Labour",
        "Transport", "Storage", "Produce Buyer", "Equipment", "Other"
    ]
    
    COLLABORATION_PURPOSES = [
        "Bulk Purchase", "Bulk Sale", "Equipment Sharing",
        "Transport", "Labour", "Knowledge Sharing", "Seed Exchange", "Other"
    ]
    
    PRICE_TYPES = ["Fixed Price", "Negotiable", "Price per kg", "Price per quintal", "Price per unit"]
    UNITS = ["kg", "quintal", "ton", "acres", "hours", "units", "bags", "liters"]
