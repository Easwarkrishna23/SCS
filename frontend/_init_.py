from flask import Blueprint

# Create blueprint for frontend routes
frontend = Blueprint('frontend', __name__,
                    template_folder='templates',
                    static_folder='static',
                    static_url_path='/static')

# Import routes at the bottom to avoid circular imports
