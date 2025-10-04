"""
SQLAlchemy database models
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    project_type = Column(String(100), nullable=False)
    location = Column(String(200), nullable=False)
    area = Column(Float, nullable=False)  # in hectares
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    description = Column(Text)
    latitude = Column(Float)
    longitude = Column(Float)
    status = Column(String(50), default="draft")  # draft, verified, blockchain_registered, tokenized
    
    # Image and analysis data
    site_image_path = Column(String(500))
    image_analysis_result = Column(JSON)
    satellite_analysis_result = Column(JSON)
    
    # Carbon data
    estimated_carbon_credits = Column(Float)
    vegetation_health = Column(String(50))
    
    # Blockchain data
    blockchain_address = Column(String(200))
    geonft_id = Column(String(200))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    verifications = relationship("Verification", back_populates="project")
    blockchain_transactions = relationship("BlockchainTransaction", back_populates="project")
    carbon_credits = relationship("CarbonCredit", back_populates="project")


class Verification(Base):
    __tablename__ = "verifications"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    verification_type = Column(String(50), nullable=False)  # internal, third_party, legal
    verifier_name = Column(String(200), nullable=False)
    status = Column(String(50), default="pending")  # pending, approved, rejected
    notes = Column(Text)
    verified_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    project = relationship("Project", back_populates="verifications")


class BlockchainTransaction(Base):
    __tablename__ = "blockchain_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    transaction_hash = Column(String(200), unique=True, nullable=False)
    contract_address = Column(String(200))
    block_number = Column(Integer)
    gas_used = Column(Integer)
    network_fee = Column(Float)
    transaction_type = Column(String(50))  # contract_deployment, geonft_mint, token_creation
    status = Column(String(50), default="pending")  # pending, confirmed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    project = relationship("Project", back_populates="blockchain_transactions")


class CarbonCredit(Base):
    __tablename__ = "carbon_credits"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    total_credits = Column(Float, nullable=False)
    available_credits = Column(Float, nullable=False)
    retired_credits = Column(Float, default=0.0)
    unit_price = Column(Float, nullable=False)
    total_value = Column(Float, nullable=False)
    token_standard = Column(String(50), default="ERC-20")
    vintage_year = Column(Integer)
    registry = Column(String(100))
    status = Column(String(50), default="active")  # active, retired, sold
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="carbon_credits")
    market_listings = relationship("MarketListing", back_populates="carbon_credit")


class MarketListing(Base):
    __tablename__ = "market_listings"
    
    id = Column(Integer, primary_key=True, index=True)
    carbon_credit_id = Column(Integer, ForeignKey("carbon_credits.id"), nullable=False)
    asking_price = Column(Float, nullable=False)
    available_amount = Column(Float, nullable=False)
    status = Column(String(50), default="active")  # active, sold, cancelled
    listed_at = Column(DateTime, default=datetime.utcnow)
    sold_at = Column(DateTime)
    
    # Relationship
    carbon_credit = relationship("CarbonCredit", back_populates="market_listings")
