from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Startup info
    startup_name = Column(String)
    startup_segment = Column(String)
    startup_trl = Column(Integer)
    startup_area = Column(String)
    startup_description = Column(Text)
    
    # Preferences
    preferred_regions = Column(JSON)
    preferred_categories = Column(JSON)
    min_amount = Column(String)
    alert_frequency = Column(String, default="weekly")
    
    # Relationships
    favorites = relationship("UserFavorite", back_populates="user")
    alerts = relationship("Alert", back_populates="user")

class Opportunity(Base):
    __tablename__ = "opportunities"
    
    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String)
    type = Column(String)  # edital, bolsa, investimento
    region = Column(String)
    deadline = Column(DateTime)
    amount = Column(String)
    source = Column(String)
    source_url = Column(String)
    relevance_score = Column(Float, default=0.0)
    tags = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Vector embeddings metadata
    pinecone_id = Column(String)
    
    # Relationships
    favorites = relationship("UserFavorite", back_populates="opportunity")

class UserFavorite(Base):
    __tablename__ = "user_favorites"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    opportunity_id = Column(Integer, ForeignKey("opportunities.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="favorites")
    opportunity = relationship("Opportunity", back_populates="favorites")

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    opportunity_id = Column(Integer, ForeignKey("opportunities.id"))
    type = Column(String)  # email, dashboard
    sent_at = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="alerts")

class AgentLog(Base):
    __tablename__ = "agent_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_name = Column(String, nullable=False)
    action = Column(String, nullable=False)
    status = Column(String, nullable=False)  # success, error, running
    details = Column(JSON)
    execution_time = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)