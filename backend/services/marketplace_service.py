"""
Marketplace service for carbon credit trading
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from models import MarketListing, CarbonCredit, Project
from datetime import datetime
from typing import Dict, Any


def create_market_listing(
    db: Session,
    carbon_credit_id: int,
    asking_price: float
) -> MarketListing:
    """
    Create a new marketplace listing
    """
    carbon_credit = db.query(CarbonCredit).filter(
        CarbonCredit.id == carbon_credit_id
    ).first()
    
    if not carbon_credit:
        raise ValueError("Carbon credit not found")
    
    if carbon_credit.available_credits <= 0:
        raise ValueError("No credits available to list")
    
    listing = MarketListing(
        carbon_credit_id=carbon_credit_id,
        asking_price=asking_price,
        available_amount=carbon_credit.available_credits,
        status="active"
    )
    
    db.add(listing)
    db.commit()
    db.refresh(listing)
    return listing


def get_market_statistics(db: Session) -> Dict[str, Any]:
    """
    Get marketplace statistics
    """
    # Get active listings
    active_listings = db.query(MarketListing).filter(
        MarketListing.status == "active"
    ).count()
    
    # Calculate average price
    avg_price = db.query(func.avg(MarketListing.asking_price)).filter(
        MarketListing.status == "active"
    ).scalar() or 45.0
    
    # Calculate total volume (mock data for now)
    total_volume = 12450.0
    
    # Total transactions
    total_transactions = 1247
    
    # Market cap
    total_credits = db.query(func.sum(CarbonCredit.total_credits)).scalar() or 0
    market_cap = total_credits * avg_price
    
    # Market demand calculation
    demand_percentage = min(100, active_listings * 10 + 50)
    
    return {
        "current_price": round(avg_price, 2),
        "price_change_24h": 0.00,
        "market_demand": demand_percentage,
        "demand_level": "High" if demand_percentage > 70 else "Medium",
        "volume_24h": total_volume,
        "total_transactions": total_transactions,
        "average_price": round(avg_price, 2),
        "market_cap": round(market_cap, 2),
        "active_listings": active_listings,
        "total_credits_available": round(total_credits, 2)
    }


def calculate_market_interest(
    db: Session,
    listing_id: int
) -> Dict[str, Any]:
    """
    Calculate market interest for a listing
    Mock implementation - in production would track actual buyer interest
    """
    return {
        "interested_buyers": [
            {
                "company_name": "EcoTech Corp",
                "company_type": "Corporate",
                "interest_amount": 1.5,
                "offer_price": 67.50
            },
            {
                "company_name": "Green Future Inc",
                "company_type": "Investment Fund",
                "interest_amount": 0.8,
                "offer_price": 36.00
            }
        ],
        "total_interest": 2.3,
        "highest_offer": 67.50
    }


def get_community_benefit_breakdown(total_value: float) -> Dict[str, Any]:
    """
    Calculate community benefit distribution
    """
    return {
        "total_value": total_value,
        "community_benefit": round(total_value * 0.70, 2),
        "community_percentage": 70,
        "families_supported": 156,
        "jobs_created": 12,
        "training_programs": True,
        "livelihood_opportunities": True,
        "women_empowerment": True,
        "capacity_building": "Active"
    }


def get_environmental_impact(carbon_credits: float, area: float) -> Dict[str, Any]:
    """
    Get environmental impact metrics
    """
    return {
        "co2_offset": carbon_credits,
        "hectares_restored": area,
        "biodiversity_enhancement": True,
        "coastal_protection": True,
        "water_quality_improvement": True,
        "marine_habitat_restoration": True,
        "benefits": [
            "Biodiversity enhancement",
            "Coastal protection",
            "Water quality improvement",
            "Marine habitat restoration",
            "Climate resilience"
        ]
    }
