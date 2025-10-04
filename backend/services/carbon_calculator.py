"""
Carbon credit calculation service
Based on scientific methodologies and standards
"""
from typing import Dict, Any
import math


# Carbon sequestration rates (tons CO2 per hectare per year)
CARBON_RATES = {
    "Mangrove Restoration": 3.5,  # Mangroves are highly efficient
    "Forest Restoration": 2.5,
    "Wetland Restoration": 2.8,
    "Grassland Restoration": 1.5,
    "Coastal Restoration": 3.0,
    "Agroforestry": 2.0
}


def calculate_carbon_credits(
    area: float,
    vegetation_index: float,
    project_type: str,
    project_duration_years: int = 1
) -> Dict[str, Any]:
    """
    Calculate carbon credits based on project parameters
    
    Args:
        area: Project area in hectares
        vegetation_index: NDVI or vegetation health index (0-1)
        project_type: Type of restoration project
        project_duration_years: Duration of the project
    
    Returns:
        Dictionary with carbon calculation details
    """
    # Get base carbon sequestration rate
    base_rate = CARBON_RATES.get(project_type, 2.0)
    
    # Adjust rate based on vegetation health
    health_multiplier = 0.5 + (vegetation_index * 0.5)  # 0.5 to 1.0
    
    # Calculate annual carbon sequestration
    annual_carbon = area * base_rate * health_multiplier
    
    # Total carbon over project duration
    total_carbon = annual_carbon * project_duration_years
    
    # Calculate additional metrics
    soil_carbon = total_carbon * 0.4  # 40% stored in soil
    biomass_carbon = total_carbon * 0.6  # 60% in biomass
    
    # CO2 equivalent (carbon to CO2 conversion factor: 3.67)
    co2_equivalent = total_carbon * 3.67
    
    # Calculate biodiversity score (0-100)
    biodiversity_score = min(100, int(vegetation_index * 100 + area * 5))
    
    # Calculate water quality impact
    water_quality_impact = calculate_water_quality_impact(area, project_type)
    
    return {
        "total_carbon_tons": round(total_carbon, 2),
        "annual_carbon_tons": round(annual_carbon, 2),
        "co2_equivalent_tons": round(co2_equivalent, 2),
        "soil_carbon_tons": round(soil_carbon, 2),
        "biomass_carbon_tons": round(biomass_carbon, 2),
        "biodiversity_score": biodiversity_score,
        "water_quality_impact": water_quality_impact,
        "calculation_method": "IS 14064-2:2019",
        "confidence_level": round(vegetation_index * 100, 1),
        "project_metrics": {
            "area_hectares": area,
            "vegetation_health_index": vegetation_index,
            "base_sequestration_rate": base_rate,
            "health_multiplier": round(health_multiplier, 2)
        }
    }


def calculate_water_quality_impact(area: float, project_type: str) -> str:
    """
    Calculate water quality impact based on project
    """
    if project_type in ["Mangrove Restoration", "Wetland Restoration", "Coastal Restoration"]:
        if area > 1.0:
            return "Highly Positive"
        else:
            return "Positive"
    elif project_type in ["Forest Restoration", "Agroforestry"]:
        return "Moderate"
    else:
        return "Low"


def calculate_community_benefits(total_value: float) -> Dict[str, float]:
    """
    Calculate community benefit distribution
    """
    return {
        "community_benefit": round(total_value * 0.70, 2),  # 70%
        "verification_cost": round(total_value * 0.10, 2),  # 10%
        "platform_fee": round(total_value * 0.05, 2),       # 5%
        "maintenance_fund": round(total_value * 0.10, 2),   # 10%
        "reserve": round(total_value * 0.05, 2)             # 5%
    }


def estimate_project_impact(area: float, carbon_tons: float) -> Dict[str, Any]:
    """
    Estimate broader environmental and social impact
    """
    # Rough estimates based on research
    families_supported = int(area * 130)  # ~130 families per hectare
    jobs_created = int(area * 10)  # ~10 jobs per hectare
    trees_planted = int(area * 1000)  # ~1000 trees per hectare for mangroves
    
    return {
        "families_supported": families_supported,
        "jobs_created": jobs_created,
        "trees_planted": trees_planted,
        "coastal_protection_km": round(area * 0.5, 2),
        "fish_habitat_improvement": "Significant" if area > 1.0 else "Moderate",
        "carbon_offset_equivalent": {
            "cars_off_road": int(carbon_tons * 0.22),  # ~0.22 cars per ton CO2
            "homes_powered": int(carbon_tons * 0.12)   # ~0.12 homes per ton CO2
        }
    }
