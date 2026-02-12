import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///lost_found.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload configuration
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # Default map center (Vellore Institute of Technology, Vellore)
    DEFAULT_LATITUDE = 12.9692
    DEFAULT_LONGITUDE = 79.1559
    
    # Matching thresholds
    MATCH_CONFIDENCE_THRESHOLD = 0.6
    LOCATION_PROXIMITY_THRESHOLD = 5000  # meters
