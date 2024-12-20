import os
from flask import Flask
from flask_socketio import SocketIO
from config import config
from frontend._init_ import frontend
from backend._init_ import create_app
from .backend.database import init_db

def create_main_app(config_name=None):
    # Determine configuration to use
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')
    
    # Create Flask application
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize database
    init_db()
    
    # Initialize SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    # Register blueprints
    app.register_blueprint(frontend)
    
    # Initialize backend
    backend_app = create_app(app.config)
    app.register_blueprint(backend_app)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return frontend.send_static_file('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return frontend.send_static_file('errors/500.html'), 500
    
    return app, socketio

if __name__ == '__main__':
    app, socketio = create_main_app()
    
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 5000))
    
    # Run the application
    socketio.run(app, 
                host='0.0.0.0',  # Makes the server externally visible
                port=port,
                debug=(os.environ.get('FLASK_ENV') == 'development'))
    