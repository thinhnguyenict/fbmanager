"""
Database models for FB Manager
SQLAlchemy ORM models for fanpages, posts, and messages
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime

Base = declarative_base()

class Fanpage(Base):
    __tablename__ = 'fanpages'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    page_id = Column(String(100), unique=True, nullable=False)
    access_token = Column(Text, nullable=False)
    followers = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    status = Column(String(20), default='active')
    created_at = Column(DateTime, default=datetime.utcnow)
    
    posts = relationship('Post', back_populates='fanpage')
    messages = relationship('Message', back_populates='fanpage')

class Post(Base):
    __tablename__ = 'posts'
    
    id = Column(Integer, primary_key=True)
    fanpage_id = Column(Integer, ForeignKey('fanpages.id'))
    content = Column(Text, nullable=False)
    status = Column(String(20), default='draft')  # draft, scheduled, published
    scheduled_time = Column(DateTime, nullable=True)
    published_time = Column(DateTime, nullable=True)
    fb_post_id = Column(String(100), nullable=True)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    fanpage = relationship('Fanpage', back_populates='posts')

class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    fanpage_id = Column(Integer, ForeignKey('fanpages.id'))
    sender_id = Column(String(100), nullable=False)
    sender_name = Column(String(200))
    message = Column(Text, nullable=False)
    status = Column(String(20), default='unread')  # unread, read, replied
    created_at = Column(DateTime, default=datetime.utcnow)
    
    fanpage = relationship('Fanpage', back_populates='messages')

# Database initialization
def init_db(db_url='sqlite:///fbmanager.db'):
    """Initialize database and create tables"""
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    return engine

def get_session(engine):
    """Get database session"""
    Session = sessionmaker(bind=engine)
    return Session()
