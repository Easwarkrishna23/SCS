from .crypto_utils import hash_password, verify_password
from .database import Admin, User
from functools import wraps
from flask import session, redirect, url_for
import jwt
import datetime

SECRET_KEY = 'your-secret-key'  # In production, use environment variable

def generate_token(user_id, is_admin=False):
    """Generate JWT token for authenticated users"""
    payload = {
        'user_id': user_id,
        'is_admin': is_admin,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def login_required(f):
    """Decorator for routes that require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = session.get('token')
        if not token:
            return redirect(url_for('login'))
        
        payload = verify_token(token)
        if not payload:
            return redirect(url_for('login'))
            
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator for routes that require admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = session.get('token')
        if not token:
            return redirect(url_for('login'))
        
        payload = verify_token(token)
        if not payload or not payload.get('is_admin'):
            return redirect(url_for('login'))
            
        return f(*args, **kwargs)
    return decorated_function

class AuthManager:
    def __init__(self, db_session):
        self.db_session = db_session

    def authenticate_admin(self, username, password):
        """Authenticate admin users"""
        admin = self.db_session.query(Admin).filter_by(username=username).first()
        if admin and verify_password(password, admin.password):
            return generate_token(admin.id, is_admin=True)
        return None

    def authenticate_user(self, username, password):
        """Authenticate regular users"""
        user = self.db_session.query(User).filter_by(username=username).first()
        if user and verify_password(password, user.password):
            return generate_token(user.id, is_admin=False)
        return None

    def create_admin(self, username, password, seniority):
        """Create a new admin account"""
        if self.db_session.query(Admin).filter_by(username=username).first():
            return False, "Username already exists"
        
        new_admin = Admin(
            username=username,
            password=hash_password(password),
            seniority=seniority
        )
        self.db_session.add(new_admin)
        self.db_session.commit()
        return True, "Admin created successfully"

    def create_user(self, username, password, node_id):
        """Create a new user account"""
        if self.db_session.query(User).filter_by(username=username).first():
            return False, "Username already exists"
        
        new_user = User(
            username=username,
            password=hash_password(password),
            node_id=node_id
        )
        self.db_session.add(new_user)
        self.db_session.commit()
        return True, "User created successfully"