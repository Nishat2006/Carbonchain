"""
Blue Carbon Registry - FastAPI Backend
Main application entry point
"""
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn
from datetime import datetime

from database import engine, get_db, Base
from models import Project, Verification, BlockchainTransaction, CarbonCredit, MarketListing
from schemas import (
    ProjectCreate, ProjectResponse, VerificationCreate, VerificationResponse,
    BlockchainTransactionResponse, CarbonCreditResponse, MarketListingResponse,
    AnalysisResult, DashboardMetrics
)
from services.image_analysis import analyze_satellite_image, analyze_site_image
from services.carbon_calculator import calculate_carbon_credits
from services.blockchain_service import deploy_contract, mint_geonft, create_carbon_tokens
from services.verification_service import create_verification_record, update_verification_status
from services.marketplace_service import create_market_listing, get_market_statistics
from services.aptos_integration import get_aptos_service
from services.binance_price_service import get_price_service, start_price_updater
import os
import asyncio

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Blue Carbon Registry API",
    description="Backend API for Mangrove Carbon Registration and Trading",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # React app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event - Start price updater
@app.on_event("startup")
async def startup_event():
    """Start background tasks on startup"""
    # Start Binance price updater (updates every 1 second)
    asyncio.create_task(start_price_updater(interval=1))
    print("✅ Binance price updater started (1 second intervals)")

# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "Blue Carbon Registry API",
        "version": "1.0.0",
        "status": "operational",
        "features": ["Real-time Binance pricing", "Blockchain integration", "AI Analysis"]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}


# ==================== PROJECT ENDPOINTS ====================

@app.post("/api/projects", response_model=ProjectResponse)
async def create_project(
    project_type: str = Form(...),
    location: str = Form(...),
    area: float = Form(...),
    start_date: str = Form(...),
    end_date: str = Form(...),
    description: str = Form(...),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    db: Session = Depends(get_db)
):
    """Create a new carbon credit project"""
    try:
        project = Project(
            project_type=project_type,
            location=location,
            area=area,
            start_date=datetime.fromisoformat(start_date),
            end_date=datetime.fromisoformat(end_date),
            description=description,
            latitude=latitude or 28.6139,  # Default to New Delhi
            longitude=longitude or 77.2090,
            status="draft"
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        
        return project
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: int, db: Session = Depends(get_db)):
    """Get project details by ID"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@app.get("/api/projects", response_model=List[ProjectResponse])
async def list_projects(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all projects with optional filtering"""
    query = db.query(Project)
    if status:
        query = query.filter(Project.status == status)
    projects = query.offset(skip).limit(limit).all()
    return projects


# ==================== IMAGE ANALYSIS ENDPOINTS ====================

@app.post("/api/analysis/site-image/{project_id}")
async def upload_and_analyze_site_image(
    project_id: int,
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload site image and perform AI analysis"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    try:
        # Save uploaded image
        upload_dir = "uploads/site_images"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = f"{upload_dir}/{project_id}_{image.filename}"
        
        with open(file_path, "wb") as f:
            content = await image.read()
            f.write(content)
        
        # Analyze image
        analysis_result = await analyze_site_image(file_path)
        
        # Update project with image path
        project.site_image_path = file_path
        project.image_analysis_result = analysis_result
        db.commit()
        
        return {
            "success": True,
            "image_path": file_path,
            "analysis": analysis_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/api/analysis/satellite/{project_id}")
async def analyze_satellite_data(
    project_id: int,
    db: Session = Depends(get_db)
):
    """Analyze satellite data for the project location"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    try:
        # Perform satellite analysis
        satellite_result = await analyze_satellite_image(
            latitude=project.latitude,
            longitude=project.longitude,
            area=project.area
        )
        
        # Calculate carbon credits
        carbon_data = calculate_carbon_credits(
            area=project.area,
            vegetation_index=satellite_result.get("vegetation_index", 0.78),
            project_type=project.project_type
        )
        
        # Update project
        project.satellite_analysis_result = satellite_result
        project.estimated_carbon_credits = carbon_data["total_carbon_tons"]
        project.vegetation_health = satellite_result.get("vegetation_health", "Excellent")
        db.commit()
        
        return {
            "success": True,
            "satellite_analysis": satellite_result,
            "carbon_calculation": carbon_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Satellite analysis failed: {str(e)}")


# ==================== VERIFICATION ENDPOINTS ====================

@app.post("/api/verification/{project_id}", response_model=VerificationResponse)
async def create_verification(
    project_id: int,
    verification_type: str = Form(...),  # 'internal', 'third_party', 'legal'
    verifier_name: str = Form(...),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Create a verification record"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    verification = create_verification_record(
        db=db,
        project_id=project_id,
        verification_type=verification_type,
        verifier_name=verifier_name,
        notes=notes
    )
    
    return verification


@app.put("/api/verification/{verification_id}/approve")
async def approve_verification(
    verification_id: int,
    notes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Approve a verification"""
    verification = update_verification_status(
        db=db,
        verification_id=verification_id,
        status="approved",
        notes=notes
    )
    
    # Update project status based on verification type
    project = db.query(Project).filter(Project.id == verification.project_id).first()
    if verification.verification_type == "legal":
        project.status = "verified"
        db.commit()
    
    return {"success": True, "verification": verification}


@app.get("/api/verification/project/{project_id}", response_model=List[VerificationResponse])
async def get_project_verifications(project_id: int, db: Session = Depends(get_db)):
    """Get all verifications for a project"""
    verifications = db.query(Verification).filter(
        Verification.project_id == project_id
    ).all()
    return verifications


# ==================== BLOCKCHAIN ENDPOINTS ====================

@app.post("/api/blockchain/deploy/{project_id}")
async def deploy_blockchain_contract(
    project_id: int,
    db: Session = Depends(get_db)
):
    """Deploy smart contract to blockchain"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.status != "verified":
        raise HTTPException(status_code=400, detail="Project must be verified first")
    
    try:
        # Deploy contract
        contract_result = await deploy_contract(
            project_id=f"MANGROVE-{project.id:03d}",
            carbon_amount=project.estimated_carbon_credits,
            location=project.location,
            latitude=project.latitude,
            longitude=project.longitude
        )
        
        # Create blockchain transaction record
        transaction = BlockchainTransaction(
            project_id=project_id,
            transaction_hash=contract_result["transaction_hash"],
            contract_address=contract_result["contract_address"],
            block_number=contract_result["block_number"],
            gas_used=contract_result["gas_used"],
            network_fee=contract_result["network_fee"],
            transaction_type="contract_deployment",
            status="confirmed"
        )
        db.add(transaction)
        
        # Update project
        project.blockchain_address = contract_result["contract_address"]
        project.status = "blockchain_registered"
        db.commit()
        db.refresh(transaction)
        
        return {
            "success": True,
            "transaction": transaction,
            "contract_address": contract_result["contract_address"]
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Blockchain deployment failed: {str(e)}")


@app.post("/api/blockchain/mint-geonft/{project_id}")
async def mint_project_geonft(
    project_id: int,
    db: Session = Depends(get_db)
):
    """Mint GeoNFT for the project"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if not project.blockchain_address:
        raise HTTPException(status_code=400, detail="Contract must be deployed first")
    
    try:
        # Mint GeoNFT
        nft_result = await mint_geonft(
            contract_address=project.blockchain_address,
            latitude=project.latitude,
            longitude=project.longitude,
            metadata={
                "project_id": f"MANGROVE-{project.id:03d}",
                "location": project.location,
                "area": project.area,
                "carbon_credits": project.estimated_carbon_credits
            }
        )
        
        # Create transaction record
        transaction = BlockchainTransaction(
            project_id=project_id,
            transaction_hash=nft_result["transaction_hash"],
            contract_address=project.blockchain_address,
            block_number=nft_result["block_number"],
            gas_used=nft_result["gas_used"],
            network_fee=nft_result["network_fee"],
            transaction_type="geonft_mint",
            status="confirmed"
        )
        db.add(transaction)
        
        # Update project
        project.geonft_id = nft_result["nft_id"]
        db.commit()
        db.refresh(transaction)
        
        return {
            "success": True,
            "nft_id": nft_result["nft_id"],
            "transaction": transaction
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"GeoNFT minting failed: {str(e)}")


# ==================== TOKENIZATION ENDPOINTS ====================

@app.post("/api/tokenization/create/{project_id}")
async def tokenize_carbon_credits(
    project_id: int,
    unit_price: float = Form(45.0),
    db: Session = Depends(get_db)
):
    """Tokenize carbon credits as ERC-20 tokens"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if not project.blockchain_address:
        raise HTTPException(status_code=400, detail="Contract must be deployed first")
    
    try:
        # Create carbon tokens
        token_result = await create_carbon_tokens(
            contract_address=project.blockchain_address,
            amount=project.estimated_carbon_credits,
            unit_price=unit_price
        )
        
        # Create carbon credit record
        carbon_credit = CarbonCredit(
            project_id=project_id,
            total_credits=project.estimated_carbon_credits,
            available_credits=project.estimated_carbon_credits,
            retired_credits=0.0,
            unit_price=unit_price,
            total_value=project.estimated_carbon_credits * unit_price,
            token_standard="ERC-20",
            vintage_year=project.start_date.year,
            registry="Blue Carbon Network",
            status="active"
        )
        db.add(carbon_credit)
        
        # Create transaction record
        transaction = BlockchainTransaction(
            project_id=project_id,
            transaction_hash=token_result["transaction_hash"],
            contract_address=project.blockchain_address,
            block_number=token_result["block_number"],
            gas_used=token_result["gas_used"],
            network_fee=token_result["network_fee"],
            transaction_type="token_creation",
            status="confirmed"
        )
        db.add(transaction)
        
        # Update project
        project.status = "tokenized"
        db.commit()
        db.refresh(carbon_credit)
        
        return {
            "success": True,
            "carbon_credit": carbon_credit,
            "transaction": transaction,
            "revenue_distribution": {
                "community_benefit": round(carbon_credit.total_value * 0.70, 2),
                "verification_cost": round(carbon_credit.total_value * 0.10, 2),
                "platform_fee": round(carbon_credit.total_value * 0.05, 2)
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Tokenization failed: {str(e)}")


@app.get("/api/tokenization/{project_id}", response_model=CarbonCreditResponse)
async def get_carbon_credits(project_id: int, db: Session = Depends(get_db)):
    """Get carbon credit details for a project"""
    carbon_credit = db.query(CarbonCredit).filter(
        CarbonCredit.project_id == project_id
    ).first()
    if not carbon_credit:
        raise HTTPException(status_code=404, detail="Carbon credits not found")
    return carbon_credit


# ==================== MARKETPLACE ENDPOINTS ====================

@app.post("/api/marketplace/list/{project_id}")
async def list_on_marketplace(
    project_id: int,
    asking_price: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """List carbon credits on marketplace"""
    carbon_credit = db.query(CarbonCredit).filter(
        CarbonCredit.project_id == project_id
    ).first()
    if not carbon_credit:
        raise HTTPException(status_code=404, detail="Carbon credits not found")
    
    try:
        listing = create_market_listing(
            db=db,
            carbon_credit_id=carbon_credit.id,
            asking_price=asking_price or carbon_credit.unit_price
        )
        
        return {
            "success": True,
            "listing": listing
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/marketplace/listings")
async def get_marketplace_listings(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all marketplace listings"""
    listings = db.query(MarketListing).filter(
        MarketListing.status == "active"
    ).offset(skip).limit(limit).all()
    
    return listings


@app.get("/api/marketplace/statistics")
async def get_marketplace_stats(db: Session = Depends(get_db)):
    """Get marketplace statistics with real-time Binance pricing"""
    stats = get_market_statistics(db)
    
    # Get real-time market data from Binance
    try:
        price_service = get_price_service()
        market_data = await price_service.get_carbon_market_data()
        
        # Update stats with real-time data
        stats.update({
            "current_price": market_data["current_price"],
            "price_change_24h": market_data["price_change_24h"],
            "price_change_percent": market_data["price_change_percent"],
            "high_24h": market_data["high_24h"],
            "low_24h": market_data["low_24h"],
            "market_sentiment": market_data["market_sentiment"],
            "demand_level": market_data["demand_level"],
            "crypto_influence": market_data["crypto_influence"],
            "last_updated": market_data["last_updated"],
        })
    except Exception as e:
        print(f"⚠️  Binance API error: {e}")
    
    return stats

@app.get("/api/marketplace/live-prices")
async def get_live_prices():
    """Get real-time prices from Binance"""
    try:
        price_service = get_price_service()
        market_data = await price_service.get_carbon_market_data()
        return {
            "success": True,
            "data": market_data
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/marketplace/portfolio-value/{carbon_credits}")
async def get_portfolio_value(carbon_credits: float):
    """Calculate portfolio value with real-time pricing"""
    try:
        price_service = get_price_service()
        portfolio = await price_service.calculate_portfolio_value(carbon_credits)
        return {
            "success": True,
            "portfolio": portfolio
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# ==================== DASHBOARD ENDPOINTS ====================

@app.get("/api/dashboard/{project_id}")
async def get_project_dashboard(project_id: int, db: Session = Depends(get_db)):
    """Get comprehensive dashboard metrics for a project"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    carbon_credit = db.query(CarbonCredit).filter(
        CarbonCredit.project_id == project_id
    ).first()
    
    # Calculate metrics
    metrics = {
        "project_overview": {
            "credits_generated": carbon_credit.total_credits if carbon_credit else 0,
            "market_value": carbon_credit.total_value if carbon_credit else 0,
            "project_status": project.status,
            "monitoring_since": project.created_at.isoformat()
        },
        "key_metrics": {
            "hectares_restored": project.area,
            "co2_sequestered": project.estimated_carbon_credits * 1000,  # in kg
            "community_income": carbon_credit.total_value * 0.70 if carbon_credit else 0,
            "biodiversity_index": 85
        },
        "progress": {
            "restoration_progress": 78,
            "carbon_sequestration": 65,
            "community_impact": 92,
            "biodiversity_recovery": 71
        },
        "environmental_health": {
            "water_quality": "Improved",
            "vegetation_health": project.vegetation_health or "Excellent",
            "marine_life": "Recovering"
        },
        "community_benefits": {
            "families_supported": 156,
            "jobs_created": 12,
            "training_programs": True,
            "livelihood_opportunities": True,
            "women_empowerment": True
        }
    }
    
    return metrics


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
