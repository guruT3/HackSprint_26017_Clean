from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, current_app
from .config import CollaborationConfig
from .utils import sanitize_text, secure_save_image
from .services import CollaborationService
from .seed import DEMO_FARMERS, DEMO_MANDIS, DEMO_LISTINGS, DEMO_REQUIREMENTS, DEMO_POSTS, DEMO_ANNOUNCEMENTS

farmer_collaboration_bp = Blueprint(
    'farmer_collaboration',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/farmer-connect-static'
)

def init_farmer_collaboration(app):
    """Host application registration helper."""
    app.register_blueprint(farmer_collaboration_bp)
    print("[+] Farmer Collaboration & Mandi Marketplace (Farmer Connect) module initialized.")


@farmer_collaboration_bp.route('/farmer-connect')
def dashboard():
    """Farmer Connect Central Dashboard."""
    return render_template(
        'farmer_collaboration/dashboard.html',
        farmers=DEMO_FARMERS[:6],
        mandis=DEMO_MANDIS,
        listings=DEMO_LISTINGS[:6],
        requirements=DEMO_REQUIREMENTS[:4],
        posts=DEMO_POSTS[:3],
        categories=CollaborationConfig.MARKETPLACE_CATEGORIES
    )


@farmer_collaboration_bp.route('/farmer-connect/community')
def community():
    """Farmer Community & Discussion Forum."""
    cat_filter = request.args.get('category')
    posts = DEMO_POSTS
    if cat_filter:
        posts = [p for p in DEMO_POSTS if p.get('category') == cat_filter]
        
    return render_template(
        'farmer_collaboration/community.html',
        posts=posts,
        categories=CollaborationConfig.COMMUNITY_CATEGORIES,
        selected_category=cat_filter
    )


@farmer_collaboration_bp.route('/farmer-connect/community/post', methods=['POST'])
def create_post():
    """Create a new community discussion post."""
    title = sanitize_text(request.form.get('title'))
    content = sanitize_text(request.form.get('content'))
    category = sanitize_text(request.form.get('category', 'General Farming'))
    crop_name = sanitize_text(request.form.get('crop_name'))
    
    if title and content:
        new_post = {
            "id": len(DEMO_POSTS) + 1,
            "author": "Ramesh Kumar",
            "author_id": 1,
            "location": "Bargarh, Odisha",
            "category": category,
            "title": title,
            "content": content,
            "likes": 0,
            "comments_count": 0,
            "best_answer": None,
            "created_at": "Just now"
        }
        DEMO_POSTS.insert(0, new_post)
        flash("Discussion post published successfully!", "success")
        
    return redirect(url_for('farmer_collaboration.community'))


@farmer_collaboration_bp.route('/farmer-connect/community/post/<int:post_id>')
def post_detail(post_id):
    """View post details and discussion replies."""
    post = next((p for p in DEMO_POSTS if p["id"] == post_id), None)
    if not post:
        flash("Post not found", "error")
        return redirect(url_for('farmer_collaboration.community'))
        
    return render_template('farmer_collaboration/post_detail.html', post=post)


@farmer_collaboration_bp.route('/farmer-connect/marketplace')
def marketplace():
    """Agricultural Marketplace."""
    cat_filter = request.args.get('category')
    search_q = request.args.get('q')
    listings = DEMO_LISTINGS
    
    if cat_filter:
        listings = [l for l in listings if l.get('category') == cat_filter]
    if search_q:
        q = search_q.lower()
        listings = [l for l in listings if q in l['title'].lower() or q in l['category'].lower() or q in l['location'].lower()]
        
    return render_template(
        'farmer_collaboration/marketplace.html',
        listings=listings,
        categories=CollaborationConfig.MARKETPLACE_CATEGORIES,
        selected_category=cat_filter,
        search_query=search_q
    )


@farmer_collaboration_bp.route('/farmer-connect/marketplace/create', methods=['GET', 'POST'])
def create_listing():
    """Create a new marketplace listing."""
    if request.method == 'POST':
        title = sanitize_text(request.form.get('title'))
        category = sanitize_text(request.form.get('category'))
        description = sanitize_text(request.form.get('description'))
        quantity = float(request.form.get('quantity', 1))
        unit = sanitize_text(request.form.get('unit', 'kg'))
        price = float(request.form.get('price', 0))
        price_type = sanitize_text(request.form.get('price_type', 'Fixed Price'))
        location = sanitize_text(request.form.get('location', 'Bargarh, Odisha'))
        
        new_item = {
            "id": len(DEMO_LISTINGS) + 1,
            "title": title,
            "seller": "Ramesh Kumar",
            "seller_id": 1,
            "category": category,
            "quantity": quantity,
            "unit": unit,
            "price": price,
            "price_type": price_type,
            "location": location,
            "rating": 4.9,
            "verified": True,
            "status": "Available"
        }
        DEMO_LISTINGS.insert(0, new_item)
        flash("Marketplace product listing created successfully!", "success")
        return redirect(url_for('farmer_collaboration.marketplace'))
        
    return render_template(
        'farmer_collaboration/create_listing.html',
        categories=CollaborationConfig.MARKETPLACE_CATEGORIES,
        price_types=CollaborationConfig.PRICE_TYPES,
        units=CollaborationConfig.UNITS
    )


@farmer_collaboration_bp.route('/farmer-connect/marketplace/listing/<int:listing_id>')
def listing_detail(listing_id):
    """View details of a marketplace item."""
    item = next((l for l in DEMO_LISTINGS if l["id"] == listing_id), None)
    if not item:
        flash("Listing not found", "error")
        return redirect(url_for('farmer_collaboration.marketplace'))
        
    return render_template('farmer_collaboration/listing_detail.html', item=item)


@farmer_collaboration_bp.route('/farmer-connect/requirements')
def requirements():
    """Farmer Requirements Board."""
    reqs = DEMO_REQUIREMENTS
    matches = CollaborationService.match_requirement_with_sellers(reqs[0]) if reqs else []
    return render_template('farmer_collaboration/requirements.html', requirements=reqs, matches=matches)


@farmer_collaboration_bp.route('/farmer-connect/requirements/create', methods=['GET', 'POST'])
def create_requirement():
    """Post a new farmer requirement."""
    if request.method == 'POST':
        title = sanitize_text(request.form.get('title'))
        category = sanitize_text(request.form.get('category'))
        description = sanitize_text(request.form.get('description'))
        quantity = float(request.form.get('quantity', 1))
        unit = sanitize_text(request.form.get('unit', 'kg'))
        budget = float(request.form.get('budget', 0))
        location = sanitize_text(request.form.get('location', 'Bargarh, Odisha'))
        by_date = sanitize_text(request.form.get('by_date', '2026-09-30'))
        
        new_req = {
            "id": len(DEMO_REQUIREMENTS) + 1,
            "title": title,
            "farmer": "Ramesh Kumar",
            "category": category,
            "quantity": quantity,
            "unit": unit,
            "budget": budget,
            "location": location,
            "by_date": by_date,
            "status": "Open"
        }
        DEMO_REQUIREMENTS.insert(0, new_req)
        flash("Requirement posted successfully! Nearby sellers have been notified.", "success")
        return redirect(url_for('farmer_collaboration.requirements'))
        
    return render_template(
        'farmer_collaboration/create_requirement.html',
        categories=CollaborationConfig.REQUIREMENT_CATEGORIES,
        units=CollaborationConfig.UNITS
    )


@farmer_collaboration_bp.route('/farmer-connect/mandi')
def mandi_hub():
    """Mandi Hub & Announcements."""
    return render_template(
        'farmer_collaboration/mandi_hub.html',
        mandis=DEMO_MANDIS,
        announcements=DEMO_ANNOUNCEMENTS
    )


@farmer_collaboration_bp.route('/farmer-connect/search')
def global_search():
    """Global search route across products, farmers, posts, mandis, and requirements."""
    q = request.args.get('q', '')
    results = CollaborationService.global_search(q)
    return render_template('farmer_collaboration/search.html', results=results, query=q)


@farmer_collaboration_bp.route('/farmer-connect/profile/<int:farmer_id>')
def farmer_profile(farmer_id):
    """View public farmer profile."""
    farmer = next((f for f in DEMO_FARMERS if f["id"] == farmer_id), DEMO_FARMERS[0])
    farmer_listings = [l for l in DEMO_LISTINGS if l.get("seller_id") == farmer_id]
    farmer_posts = [p for p in DEMO_POSTS if p.get("author_id") == farmer_id]
    
    return render_template(
        'farmer_collaboration/profile.html',
        farmer=farmer,
        listings=farmer_listings,
        posts=farmer_posts
    )


@farmer_collaboration_bp.route('/farmer-connect/messages')
def messages():
    """In-app Messaging & Chat."""
    return render_template('farmer_collaboration/messages.html', farmers=DEMO_FARMERS)


@farmer_collaboration_bp.route('/farmer-connect/notifications')
def notifications():
    """Notification Center."""
    notifications_list = [
        {"title": "New Purchase Inquiry", "message": "Subhashree Naik sent an inquiry for '500 kg Swarna Paddy Seeds'.", "time": "10 mins ago", "link": "/farmer-connect/messages"},
        {"title": "Collaboration Request Accepted", "message": "Suresh Kumar accepted your tractor sharing request.", "time": "1 hour ago", "link": "/farmer-connect/profile/2"},
        {"title": "New Mandi Announcement", "message": "Bargarh Mandi published Kharif Paddy MSP Procurement notice.", "time": "3 hours ago", "link": "/farmer-connect/mandi"}
    ]
    return render_template('farmer_collaboration/notifications.html', notifications=notifications_list)


@farmer_collaboration_bp.route('/farmer-connect/admin')
def admin_dashboard():
    """Admin Dashboard for Verification, Reports, and Suspensions."""
    return render_template(
        'farmer_collaboration/admin.html',
        total_farmers=len(DEMO_FARMERS),
        total_mandis=len(DEMO_MANDIS),
        total_listings=len(DEMO_LISTINGS),
        total_posts=len(DEMO_POSTS),
        farmers=DEMO_FARMERS,
        mandis=DEMO_MANDIS
    )
