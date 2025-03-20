import os
from flask_sqlalchemy import SQLAlchemy
from config import DATABASE_NAME, DATABASE_TYPE, DATABASE_DIR  # Import your configuration values

# Initialize Flask-SQLAlchemy instance
db = SQLAlchemy()

# Build the database path
DATABASE_PATH = os.path.join(DATABASE_DIR, DATABASE_NAME)

# Ensure the directory exists for the database file
os.makedirs(DATABASE_DIR, exist_ok=True)

# Log the database path to check if it's correct
print(f"Database path: {DATABASE_PATH}")

# SQLite Database URL with absolute path
DATABASE_URL = f"{DATABASE_TYPE}:///{os.path.abspath(DATABASE_PATH)}"

# Function to initialize the database and connect it to the Flask app
def init_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable modification tracking
    db.init_app(app)  # Initialize Flask-SQLAlchemy with the app
    
    # Create the database if it doesn't exist
    with app.app_context():
        if not os.path.exists(DATABASE_PATH):
            print(f"Database not found. Creating a new database at {DATABASE_PATH}...")
            db.create_all()  # Create the database and tables
        else:
            print(f"Database already exists at {DATABASE_PATH}.")
