from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime

# Create the base class for declarative models
Base = declarative_base()

# Define the Admin model
class Admin(Base):
    __tablename__ = 'admins'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False)  # Will store hashed password
    seniority = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

# Define the User model
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False)  # Will store hashed password
    node_id = Column(Integer, unique=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

# Define the Message model
class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    sender_id = Column(Integer, ForeignKey('users.id'))
    receiver_id = Column(Integer, ForeignKey('users.id'))
    encrypted_content = Column(String(1000))
    sent_at = Column(DateTime, default=datetime.datetime.utcnow)
    read = Column(Boolean, default=False)
    
    # Relationships
    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])

# Define the NetworkEdge model for graph connections
class NetworkEdge(Base):
    __tablename__ = 'network_edges'
    
    id = Column(Integer, primary_key=True)
    node1_id = Column(Integer, ForeignKey('users.id'))
    node2_id = Column(Integer, ForeignKey('users.id'))
    weight = Column(Integer, default=1)  # For shortest path calculations

# Database initialization function
def init_db():
    # Use SQLite for simplicity
    engine = create_engine('sqlite:///secure_comm.db')
    Base.metadata.create_all(engine)
    
    # Create session maker
    Session = sessionmaker(bind=engine)
    return Session()

# Create initial admin and users
def create_initial_data(session):
    from crypto_utils import hash_password
    
    # Create initial admin
    admin = Admin(
        username="admin1",
        password=hash_password("password1"),
        seniority=1
    )
    
    # Create initial users
    user1 = User(
        username="user1",
        password=hash_password("upassword1"),
        node_id=1
    )
    
    user2 = User(
        username="user2",
        password=hash_password("upassword2"),
        node_id=2
    )
    
    session.add_all([admin, user1, user2])
    session.commit()