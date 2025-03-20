from database import db

# Define the User model
class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    mobile = db.Column(db.String(15), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    pages = db.relationship('Pages', backref='user', lazy=True, cascade="all, delete-orphan")

# Define the Pages model
class Pages(db.Model):
    __tablename__ = 'pages'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    page_uuid = db.Column(db.String, nullable=True)
    page_type=db.Column(db.String, nullable=True)
    file_extension = db.Column(db.String, nullable=True)
