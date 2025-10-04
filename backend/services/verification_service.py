"""
Verification service for multi-stage verification process
"""
from sqlalchemy.orm import Session
from datetime import datetime
from models import Verification
from typing import Optional


def create_verification_record(
    db: Session,
    project_id: int,
    verification_type: str,
    verifier_name: str,
    notes: Optional[str] = None
) -> Verification:
    """
    Create a new verification record
    
    Verification types:
    - internal: Initial internal verification
    - third_party: Third-party regulatory verification
    - legal: Legal and statutory compliance
    """
    verification = Verification(
        project_id=project_id,
        verification_type=verification_type,
        verifier_name=verifier_name,
        status="pending",
        notes=notes
    )
    db.add(verification)
    db.commit()
    db.refresh(verification)
    return verification


def update_verification_status(
    db: Session,
    verification_id: int,
    status: str,
    notes: Optional[str] = None
) -> Verification:
    """
    Update verification status
    
    Status options:
    - pending
    - approved
    - rejected
    """
    verification = db.query(Verification).filter(
        Verification.id == verification_id
    ).first()
    
    if not verification:
        raise ValueError("Verification not found")
    
    verification.status = status
    if notes:
        verification.notes = notes
    
    if status == "approved":
        verification.verified_at = datetime.utcnow()
    
    db.commit()
    db.refresh(verification)
    return verification


def get_verification_checklist(verification_type: str) -> dict:
    """
    Get verification checklist based on type
    """
    checklists = {
        "internal": {
            "items": [
                "Photo validation & authenticity",
                "GPS coordinates accuracy",
                "AI analysis review",
                "Overall data quality"
            ],
            "required_confidence": 0.90
        },
        "third_party": {
            "items": [
                "Document authenticity verification",
                "Environmental compliance standards",
                "Regulatory framework adherence",
                "Complete audit trail validation"
            ],
            "standards": ["IS 14064-2:2019"],
            "authority": "Green Compliance Authority India"
        },
        "legal": {
            "items": [
                "Forest Conservation Act, 1980 compliance",
                "Environment Impact Assessment, 2006",
                "National Action Plan on Climate Change",
                "IS 14064-2:2019 - GHG quantification"
            ],
            "risk_assessment": {
                "environmental_impact": "Low Risk",
                "regulatory_compliance": "Medium Risk",
                "data_quality": "Low Risk"
            }
        }
    }
    
    return checklists.get(verification_type, {})


def validate_verification_requirements(
    db: Session,
    project_id: int,
    verification_type: str
) -> dict:
    """
    Validate if project meets requirements for verification type
    """
    verifications = db.query(Verification).filter(
        Verification.project_id == project_id,
        Verification.status == "approved"
    ).all()
    
    approved_types = [v.verification_type for v in verifications]
    
    requirements = {
        "internal": [],
        "third_party": ["internal"],
        "legal": ["internal", "third_party"]
    }
    
    required = requirements.get(verification_type, [])
    missing = [r for r in required if r not in approved_types]
    
    return {
        "can_proceed": len(missing) == 0,
        "missing_verifications": missing,
        "completed_verifications": approved_types
    }
