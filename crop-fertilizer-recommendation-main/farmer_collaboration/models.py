from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

try:
    from flask_sqlalchemy import SQLAlchemy
    db = SQLAlchemy()
except ImportError:
    db = None


class User(db.Model if db else object):
    __tablename__ = 'fc_users'
    
    id = db.Column(db.Integer, primary_key=True) if db else None
    username = db.Column(db.String(80), unique=True, nullable=False) if db else None
    password_hash = db.Column(db.String(255), nullable=False) if db else None
    role = db.Column(db.String(20), default="FARMER") if db else None  # FARMER, MANDI, ADMIN
    is_verified = db.Column(db.Boolean, default=False) if db else None
    is_suspended = db.Column(db.Boolean, default=False) if db else None
    created_at = db.Column(db.DateTime, default=datetime.utcnow) if db else None

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class FarmerProfile(db.Model if db else object):
    __tablename__ = 'fc_farmer_profiles'
    
    id = db.Column(db.Integer, primary_key=True) if db else None
    user_id = db.Column(db.Integer, db.ForeignKey('fc_users.id'), nullable=False) if db else None
    name = db.Column(db.String(100), nullable=False) if db else None
    village = db.Column(db.String(100)) if db else None
    district = db.Column(db.String(100), nullable=False) if db else None
    state = db.Column(db.String(100), nullable=False) if db else None
    preferred_language = db.Column(db.String(50), default="Odia") if db else None
    crops_grown = db.Column(db.String(255), default="Rice, Wheat") if db else None
    farm_size = db.Column(db.String(50), default="5 Acres") if db else None
    experience_years = db.Column(db.Integer, default=5) if db else None
    about = db.Column(db.Text) if db else None
    rating = db.Column(db.Float, default=4.8) if db else None
    total_transactions = db.Column(db.Integer, default=0) if db else None
    avatar = db.Column(db.String(255), default="default_farmer.png") if db else None


class MandiProfile(db.Model if db else object):
    __tablename__ = 'fc_mandi_profiles'
    
    id = db.Column(db.Integer, primary_key=True) if db else None
    user_id = db.Column(db.Integer, db.ForeignKey('fc_users.id'), nullable=False) if db else None
    mandi_name = db.Column(db.String(150), nullable=False) if db else None
    district = db.Column(db.String(100), nullable=False) if db else None
    state = db.Column(db.String(100), nullable=False) if db else None
    contact_phone = db.Column(db.String(30)) if db else None
    operating_hours = db.Column(db.String(100), default="8:00 AM - 6:00 PM") if db else None
    supported_crops = db.Column(db.String(255), default="Paddy, Maize, Pulses") if db else None
    verification_status = db.Column(db.String(50), default="Platform Verified") if db else None
    notice = db.Column(db.Text) if db else None


class Post(db.Model if db else object):
    __tablename__ = 'fc_posts'
    
    id = db.Column(db.Integer, primary_key=True) if db else None
    user_id = db.Column(db.Integer, db.ForeignKey('fc_users.id'), nullable=False) if db else None
    title = db.Column(db.String(200), nullable=False) if db else None
    content = db.Column(db.Text, nullable=False) if db else None
    category = db.Column(db.String(50), default="General Farming") if db else None
    crop_name = db.Column(db.String(100)) if db else None
    image_path = db.Column(db.String(255)) if db else None
    likes_count = db.Column(db.Integer, default=0) if db else None
    comments_count = db.Column(db.Integer, default=0) if db else None
    created_at = db.Column(db.DateTime, default=datetime.utcnow) if db else None


class Comment(db.Model if db else object):
    __tablename__ = 'fc_comments'
    
    id = db.Column(db.Integer, primary_key=True) if db else None
    post_id = db.Column(db.Integer, db.ForeignKey('fc_posts.id'), nullable=False) if db else None
    user_id = db.Column(db.Integer, db.ForeignKey('fc_users.id'), nullable=False) if db else None
    content = db.Column(db.Text, nullable=False) if db else None
    is_best_answer = db.Column(db.Boolean, default=False) if db else None
    created_at = db.Column(db.DateTime, default=datetime.utcnow) if db else None


class PostLike(db.Model if db else object):
    __tablename__ = 'fc_post_likes'
    
    id = db.Column(db.Integer, primary_key=True) if db else None
    post_id = db.Column(db.Integer, db.ForeignKey('fc_posts.id'), nullable=False) if db else None
    user_id = db.Column(db.Integer, db.ForeignKey('fc_users.id'), nullable=False) if db else None


class Listing(db.Model if db else object):
    __tablename__ = 'fc_listings'
    
    id = db.Column(db.Integer, primary_key=True) if db else None
    seller_id = db.Column(db.Integer, db.ForeignKey('fc_users.id'), nullable=False) if db else None
    title = db.Column(db.String(150), nullable=False) if db else None
    category = db.Column(db.String(50), nullable=False) if db else None
    description = db.Column(db.Text, nullable=False) if db else None
    quantity = db.Column(db.Float, nullable=False) if db else None
    unit = db.Column(db.String(20), default="kg") if db else None
    price = db.Column(db.Float, nullable=False) if db else None
    price_type = db.Column(db.String(30), default="Fixed Price") if db else None
    location_district = db.Column(db.String(100), nullable=False) if db else None
    state = db.Column(db.String(100), nullable=False) if db else None
    condition = db.Column(db.String(50), default="New / Certified") if db else None
    image_path = db.Column(db.String(255)) if db else None
    status = db.Column(db.String(30), default="Available") if db else None
    created_at = db.Column(db.DateTime, default=datetime.utcnow) if db else None


class Requirement(db.Model if db else object):
    __tablename__ = 'fc_requirements'
    
    id = db.Column(db.Integer, primary_key=True) if db else None
    farmer_id = db.Column(db.Integer, db.ForeignKey('fc_users.id'), nullable=False) if db else None
    title = db.Column(db.String(150), nullable=False) if db else None
    description = db.Column(db.Text, nullable=False) if db else None
    category = db.Column(db.String(50), nullable=False) if db else None
    quantity = db.Column(db.Float, nullable=False) if db else None
    unit = db.Column(db.String(20), default="kg") if db else None
    max_budget = db.Column(db.Float, nullable=False) if db else None
    location_district = db.Column(db.String(100), nullable=False) if db else None
    state = db.Column(db.String(100), nullable=False) if db else None
    required_by_date = db.Column(db.String(30)) if db else None
    status = db.Column(db.String(30), default="Open") if db else None
    created_at = db.Column(db.DateTime, default=datetime.utcnow) if db else None


class CollaborationRequest(db.Model if db else object):
    __tablename__ = 'fc_collaborations'
    
    id = db.Column(db.Integer, primary_key=True) if db else None
    sender_id = db.Column(db.Integer, db.ForeignKey('fc_users.id'), nullable=False) if db else None
    receiver_id = db.Column(db.Integer, db.ForeignKey('fc_users.id'), nullable=False) if db else None
    purpose = db.Column(db.String(50), nullable=False) if db else None
    message = db.Column(db.Text, nullable=False) if db else None
    status = db.Column(db.String(30), default="Pending") if db else None
    created_at = db.Column(db.DateTime, default=datetime.utcnow) if db else None


class Inquiry(db.Model if db else object):
    __tablename__ = 'fc_inquiries'
    
    id = db.Column(db.Integer, primary_key=True) if db else None
    listing_id = db.Column(db.Integer, db.ForeignKey('fc_listings.id'), nullable=False) if db else None
    buyer_id = db.Column(db.Integer, db.ForeignKey('fc_users.id'), nullable=False) if db else None
    seller_id = db.Column(db.Integer, db.ForeignKey('fc_users.id'), nullable=False) if db else None
    message = db.Column(db.Text, nullable=False) if db else None
    status = db.Column(db.String(30), default="Pending") if db else None
    created_at = db.Column(db.DateTime, default=datetime.utcnow) if db else None


class Announcement(db.Model if db else object):
    __tablename__ = 'fc_announcements'
    
    id = db.Column(db.Integer, primary_key=True) if db else None
    mandi_id = db.Column(db.Integer, db.ForeignKey('fc_users.id'), nullable=False) if db else None
    title = db.Column(db.String(200), nullable=False) if db else None
    content = db.Column(db.Text, nullable=False) if db else None
    crop_type = db.Column(db.String(100)) if db else None
    procurement_price = db.Column(db.String(50)) if db else None
    status = db.Column(db.String(30), default="Active") if db else None
    created_at = db.Column(db.DateTime, default=datetime.utcnow) if db else None


class Notification(db.Model if db else object):
    __tablename__ = 'fc_notifications'
    
    id = db.Column(db.Integer, primary_key=True) if db else None
    user_id = db.Column(db.Integer, db.ForeignKey('fc_users.id'), nullable=False) if db else None
    title = db.Column(db.String(150), nullable=False) if db else None
    message = db.Column(db.Text, nullable=False) if db else None
    link_url = db.Column(db.String(255)) if db else None
    is_read = db.Column(db.Boolean, default=False) if db else None
    created_at = db.Column(db.DateTime, default=datetime.utcnow) if db else None


class Report(db.Model if db else object):
    __tablename__ = 'fc_reports'
    
    id = db.Column(db.Integer, primary_key=True) if db else None
    reporter_id = db.Column(db.Integer, db.ForeignKey('fc_users.id'), nullable=False) if db else None
    target_type = db.Column(db.String(30), nullable=False) if db else None  # Post, Listing, User, Mandi
    target_id = db.Column(db.Integer, nullable=False) if db else None
    reason = db.Column(db.String(255), nullable=False) if db else None
    status = db.Column(db.String(30), default="Pending Review") if db else None
    created_at = db.Column(db.DateTime, default=datetime.utcnow) if db else None
