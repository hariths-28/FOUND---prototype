from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    """User model for authentication and item reporting"""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    items = db.relationship('Item', backref='reporter', lazy=True)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.email}>'

@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login"""
    return User.query.get(int(user_id))

class Item(db.Model):
    """Lost or Found item model"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), nullable=False)  # 'lost' or 'found'
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    image_path = db.Column(db.String(500), nullable=True)
    reported_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reported_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    
    # Relationships
    lost_matches = db.relationship('Match', foreign_keys='Match.lost_item_id', 
                                   backref='lost_item', lazy=True, cascade='all, delete-orphan')
    found_matches = db.relationship('Match', foreign_keys='Match.found_item_id', 
                                    backref='found_item', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert item to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'status': self.status,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'image_path': self.image_path,
            'reported_at': self.reported_at.isoformat() if self.reported_at else None,
            'is_verified': self.is_verified
        }
    
    def __repr__(self):
        return f'<Item {self.title} - {self.status}>'

class Match(db.Model):
    """Match between lost and found items"""
    id = db.Column(db.Integer, primary_key=True)
    lost_item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    found_item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    confidence_score = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    
    def to_dict(self):
        """Convert match to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'lost_item': self.lost_item.to_dict() if self.lost_item else None,
            'found_item': self.found_item.to_dict() if self.found_item else None,
            'confidence_score': self.confidence_score,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_verified': self.is_verified
        }
    
    def __repr__(self):
        return f'<Match {self.lost_item_id} <-> {self.found_item_id} ({self.confidence_score:.2f})>'
