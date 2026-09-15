from typing import List, Optional
from pydantic import BaseModel


class CompanyProfile(BaseModel):

    company_name: Optional[str] = None
    ticker: Optional[str] = None
    industry: Optional[str] = None
    sector: Optional[str] = None

    description: Optional[str] = None

    headquarters: Optional[str] = None

    founded_year: Optional[int] = None

    employees: Optional[int] = None

    website: Optional[str] = None



class BusinessModel(BaseModel):

    revenue_model: Optional[str] = None

    products_services: List[str] = []

    customer_segments: List[str] = []

    suppliers: List[str] = []

    competitive_advantages: List[str] = []

    risks: List[str] = []



class ManagementProfile(BaseModel):

    ceo: Optional[str] = None

    executives: List[str] = []

    board_members: List[str] = []

    leadership_quality: Optional[str] = None

    governance_rating: Optional[str] = None



class OwnershipProfile(BaseModel):

    major_shareholders: List[str] = []

    institutional_ownership: Optional[str] = None

    insider_ownership: Optional[str] = None

    ownership_structure: Optional[str] = None



class ProductProfile(BaseModel):

    products: List[str] = []

    services: List[str] = []

    platforms: List[str] = []

    key_products: List[str] = []



class GeographyProfile(BaseModel):

    headquarters: Optional[str] = None

    operating_regions: List[str] = []

    manufacturing_locations: List[str] = []

    sales_regions: List[str] = []



class BusinessSegment(BaseModel):

    name: str

    description: Optional[str] = None

    revenue_share: Optional[str] = None

    growth_rate: Optional[str] = None



class CompanyResearchResult(BaseModel):

    profile: CompanyProfile

    business_model: BusinessModel

    management: ManagementProfile

    ownership: OwnershipProfile

    products: ProductProfile

    geography: GeographyProfile

    segments: List[BusinessSegment] = []

    confidence_score: Optional[float] = None