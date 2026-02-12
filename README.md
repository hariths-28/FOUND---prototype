# Lost & Found System

A Smart Map-Based Lost & Found System that uses real-time map pins and intelligent matching to help recover items.

## Features

- **Report Lost Items**: Report items you've lost with location, description, and images
- **Report Found Items**: Report items you've found to help reunite them with owners
- **Interactive Map (Folium/Leaflet + OpenStreetMap)**: Visual map interface showing all lost and found items
- **Intelligent Matching**: AI-powered matching algorithm combining text similarity, location proximity, and time analysis
- **Admin Verification**: Admin system to verify items and matches
- **Image Upload**: Support for uploading item images
- **Real-time Statistics**: Dashboard showing total items, recovered items, and active matches

## Tech Stack

- **Backend**: Python 3.10+, Flask, Flask-SQLAlchemy, Flask-Login
- **Database**: SQLite
- **Frontend**: HTML5, Bootstrap 5, Vanilla JavaScript
- **Maps**: Folium (Python) + Leaflet + OpenStreetMap
- **Storage**: Local filesystem for images

## Setup Instructions

### 1. Create Virtual Environment

```bash
python -m venv venv
```

### 2. Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
python run.py
```

The application will be available at `http://localhost:5000`

### Notes on Maps

- This project uses **Folium** on the backend to render item maps and **Leaflet + OpenStreetMap** on the frontend for interactive item reporting.
- **No API key is required**; maps are powered by free OpenStreetMap tiles.

## Creating an Admin User

To create an admin user, you can use Python's interactive shell:

```bash
python
```

Then run:

```python
from app import create_app, db
from app.models import User
from config import Config

app = create_app(Config)
with app.app_context():
    # Create admin user
    admin = User(email='admin@example.com')
    admin.set_password('admin123')
    admin.is_admin = True
    db.session.add(admin)
    db.session.commit()
    print('Admin user created!')
```

Replace `admin@example.com` and `admin123` with your desired email and password.

## Project Structure

```
lost_found_app/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models.py            # Database models
│   ├── routes.py            # Flask routes
│   ├── matching.py          # Matching algorithm
│   ├── bati/                # Business logic
│   │   ├── __init__.py
│   │   └── utils.py         # Utility functions
│   ├── static/
│   │   ├── css/             # CSS files
│   │   ├── js/              # JavaScript files
│   │   └── uploads/         # Uploaded images
│   └── templates/           # HTML templates
│       ├── base.html
│       ├── index.html
│       ├── report_lost.html
│       ├── report_found.html
│       ├── item_detail.html
│       ├── matches.html
│       ├── admin.html
│       ├── login.html
│       └── register.html
├── config.py                # Configuration
├── run.py                   # Application entry point
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Database Schema

- **User**: Stores user accounts and admin status
- **Item**: Stores lost and found items with location, description, and images
- **Match**: Stores matches between lost and found items with confidence scores

## Matching Algorithm

The matching system uses three factors:

1. **Text Similarity (50% weight)**: Compares item titles and descriptions using TF-IDF
2. **Location Proximity (30% weight)**: Calculates distance using Haversine formula
3. **Time Difference (20% weight)**: Considers when items were reported

Matches are created when the combined score exceeds 0.6 (60% confidence).

## Usage

1. **Register/Login**: Create an account or login
2. **Report Items**: Click "Report Lost" or "Report Found" to add items
3. **View Map**: See all items on the interactive map
4. **View Matches**: Check suggested matches on the Matches page
5. **Admin**: Admin users can verify items and matches

## Notes

- This is a hackathon demonstration project
- For production use, consider:
  - Using a production database (PostgreSQL)
  - Implementing proper file storage (AWS S3, etc.)
  - Adding rate limiting
  - Implementing email notifications
  - Adding more sophisticated matching algorithms
  - Using environment variables for all secrets

## License

Hackathon Demo Project
