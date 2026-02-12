from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import User, Item, Match
from app.matching import find_matches_for_item
from app.bati.utils import allowed_file, calculate_haversine_distance
from datetime import datetime
import os
import folium

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Homepage with map and statistics"""
    # Get statistics
    total_items = Item.query.count()
    lost_count = Item.query.filter_by(status='lost').count()
    found_count = Item.query.filter_by(status='found').count()
    verified_matches = Match.query.filter_by(is_verified=True).count()
    
    # Get all items for map
    items = Item.query.all()

    # Build Folium map
    default_lat = current_app.config.get('DEFAULT_LATITUDE', 37.7749)
    default_lng = current_app.config.get('DEFAULT_LONGITUDE', -122.4194)

    fmap = folium.Map(location=[default_lat, default_lng], zoom_start=12)

    for item in items:
        # Ensure item has valid coordinates
        if item.latitude is None or item.longitude is None:
            continue

        # Marker color based on status/verification
        color = 'red'
        if item.status == 'found':
            color = 'green'
        if item.is_verified:
            # Use orange to approximate "verified" yellow
            color = 'orange'

        popup_html = f"""
        <div>
            <h6>{item.title}</h6>
            <p><strong>Status:</strong> {item.status.title()}</p>
            {f'<p><strong>Category:</strong> {item.category}</p>' if item.category else ''}
            <a href="{url_for('main.item_detail', id=item.id)}" class="btn btn-sm btn-primary mt-2">View Details</a>
        </div>
        """

        folium.Marker(
            location=[item.latitude, item.longitude],
            popup=popup_html,
            icon=folium.Icon(color=color, icon="info-sign"),
        ).add_to(fmap)

    map_html = fmap._repr_html_()
    
    return render_template('index.html',
                         items=items,
                         map_html=map_html,
                         total_items=total_items,
                         lost_count=lost_count,
                         found_count=found_count,
                         verified_matches=verified_matches)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Email and password are required.', 'error')
            return render_template('register.html')
        
        # Check if user exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return render_template('register.html')
        
        # Create new user
        user = User(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('main.login'))
    
    return render_template('register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

@bp.route('/report/lost', methods=['GET', 'POST'])
@login_required
def report_lost():
    """Report a lost item"""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        latitude = float(request.form.get('latitude'))
        longitude = float(request.form.get('longitude'))
        
        if not title or not latitude or not longitude:
            flash('Title and location are required.', 'error')
            return render_template('report_lost.html')
        
        # Handle image upload
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                if allowed_file(file.filename, current_app.config['ALLOWED_EXTENSIONS']):
                    filename = secure_filename(file.filename)
                    # Add timestamp to avoid collisions
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                    filename = timestamp + filename
                    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    image_path = f'uploads/{filename}'
        
        # Create item
        item = Item(
            title=title,
            description=description,
            category=category,
            status='lost',
            latitude=latitude,
            longitude=longitude,
            image_path=image_path,
            reported_by=current_user.id
        )
        db.session.add(item)
        db.session.commit()
        
        # Find matches
        matches = find_matches_for_item(item)
        if matches:
            flash(f'Item reported! Found {len(matches)} potential match(es).', 'success')
        else:
            flash('Item reported successfully!', 'success')
        
        return redirect(url_for('main.item_detail', id=item.id))
    
    return render_template('report_lost.html')

@bp.route('/report/found', methods=['GET', 'POST'])
@login_required
def report_found():
    """Report a found item"""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        latitude = float(request.form.get('latitude'))
        longitude = float(request.form.get('longitude'))
        
        if not title or not latitude or not longitude:
            flash('Title and location are required.', 'error')
            return render_template('report_found.html')
        
        # Handle image upload
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                if allowed_file(file.filename, current_app.config['ALLOWED_EXTENSIONS']):
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                    filename = timestamp + filename
                    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    image_path = f'uploads/{filename}'
        
        # Create item
        item = Item(
            title=title,
            description=description,
            category=category,
            status='found',
            latitude=latitude,
            longitude=longitude,
            image_path=image_path,
            reported_by=current_user.id
        )
        db.session.add(item)
        db.session.commit()
        
        # Find matches
        matches = find_matches_for_item(item)
        if matches:
            flash(f'Item reported! Found {len(matches)} potential match(es).', 'success')
        else:
            flash('Item reported successfully!', 'success')
        
        return redirect(url_for('main.item_detail', id=item.id))
    
    return render_template('report_found.html')

@bp.route('/item/<int:id>')
def item_detail(id):
    """Item detail page"""
    item = Item.query.get_or_404(id)
    
    # Get matches for this item
    if item.status == 'lost':
        matches = Match.query.filter_by(lost_item_id=id).order_by(Match.confidence_score.desc()).all()
    else:
        matches = Match.query.filter_by(found_item_id=id).order_by(Match.confidence_score.desc()).all()

    # Build Folium map for this item
    fmap = folium.Map(location=[item.latitude, item.longitude], zoom_start=15)

    color = 'red' if item.status == 'lost' else 'green'

    folium.Marker(
        location=[item.latitude, item.longitude],
        popup=f"<b>{item.title}</b>",
        icon=folium.Icon(color=color, icon="info-sign"),
    ).add_to(fmap)

    map_html = fmap._repr_html_()

    return render_template('item_detail.html', item=item, matches=matches, map_html=map_html)

@bp.route('/matches')
def matches():
    """View all matches"""
    all_matches = Match.query.order_by(Match.confidence_score.desc()).all()
    return render_template('matches.html', matches=all_matches)

@bp.route('/api/items')
def api_items():
    """API endpoint for items (for map)"""
    items = Item.query.all()
    return jsonify([item.to_dict() for item in items])

@bp.route('/admin')
@login_required
def admin():
    """Admin dashboard"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    # Get unverified items
    unverified_items = Item.query.filter_by(is_verified=False).all()
    
    # Get unverified matches
    unverified_matches = Match.query.filter_by(is_verified=False).all()
    
    return render_template('admin.html',
                         unverified_items=unverified_items,
                         unverified_matches=unverified_matches)

@bp.route('/admin/verify/item/<int:id>')
@login_required
def verify_item(id):
    """Verify an item (admin only)"""
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('main.index'))
    
    item = Item.query.get_or_404(id)
    item.is_verified = True
    db.session.commit()
    
    flash(f'Item "{item.title}" has been verified.', 'success')
    return redirect(url_for('main.admin'))

@bp.route('/admin/verify/match/<int:id>')
@login_required
def verify_match(id):
    """Verify a match (admin only)"""
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('main.index'))
    
    match = Match.query.get_or_404(id)
    match.is_verified = True
    db.session.commit()
    
    flash('Match has been verified.', 'success')
    return redirect(url_for('main.admin'))
