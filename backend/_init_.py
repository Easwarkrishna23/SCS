from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from .database import init_db
from .authentication import AuthManager
from .graph_utils import NetworkGraph
from .message_handler import MessageHandler

db_session = None
auth_manager = None
graph_manager = None
message_handler = None

def create_app(config=None):
    app = Flask(__name__)
    
    # Load configuration
    if config:
        app.config.from_object(config)
    else:
        app.config.from_object('config.Config')

    # Enable CORS
    CORS(app)

    # Initialize database
    global db_session
    db_session = init_db()

    # Initialize managers
    global auth_manager, graph_manager, message_handler
    auth_manager = AuthManager(db_session)
    graph_manager = NetworkGraph(db_session)
    message_handler = MessageHandler(db_session, graph_manager)

    # Create demo data if needed
    if app.config.get('CREATE_DEMO_DATA', False):
        graph_manager.create_demo_graph()

    # Register blueprints
    from frontend.routes import api
    app.register_blueprint(api)

    return app