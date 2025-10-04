"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


# Project Schemas
class ProjectCreate(BaseModel):
    project_type: str
    location: str
    area: float
    start_date: str
    end_date: str
    description: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class ProjectResponse(BaseModel):
    id: int
    project_type: str
    location: str
    area: float
    start_date: datetime
    end_date: datetime
    description: str
    latitude: Optional[float]
    longitude: Optional[float]
    status: str
    site_image_path: Optional[str]
    estimated_carbon_credits: Optional[float]
    vegetation_health: Optional[str]
    blockchain_address: Optional[str]
    geonft_id: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Verification Schemas
class VerificationCreate(BaseModel):
    verification_type: str
    verifier_name: str
    notes: Optional[str] = None


class VerificationResponse(BaseModel):
    id: int
    project_id: int
    verification_type: str
    verifier_name: str
    status: str
    notes: Optional[str]
    verified_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Blockchain Schemas
class BlockchainTransactionResponse(BaseModel):
    id: int
    project_id: int
    transaction_hash: str
    contract_address: Optional[str]
    block_number: Optional[int]
    gas_used: Optional[int]
    network_fee: Optional[float]
    transaction_type: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Carbon Credit Schemas
class CarbonCreditResponse(BaseModel):
    id: int
    project_id: int
    total_credits: float
    available_credits: float
    retired_credits: float
    unit_price: float
    total_value: float
    token_standard: str
    vintage_year: Optional[int]
    registry: Optional[str]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Market Listing Schemas
class MarketListingResponse(BaseModel):
    id: int
    carbon_credit_id: int
    asking_price: float
    available_amount: float
    status: str
    listed_at: datetime
    sold_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Analysis Schemas
class AnalysisResult(BaseModel):
    vegetation_index: float
    vegetation_health: str
    confidence: float
    analysis_timestamp: datetime


class DashboardMetrics(BaseModel):
    project_overview: Dict[str, Any]
    key_metrics: Dict[str, Any]
    progress: Dict[str, Any]
    environmental_health: Dict[str, Any]
    community_benefits: Dict[str, Any]
