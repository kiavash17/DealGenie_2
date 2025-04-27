from typing import List, Dict, Optional, Any
from pydantic import BaseModel


class FounderProfile(BaseModel):
    name: str
    background: Optional[str] = None
    linkedin: Optional[str] = None
    attributes: Optional[List[str]] = None


class CompanyProfile(BaseModel):
    company_name: str
    founders: Optional[List[FounderProfile]] = None
    deck_url: Optional[str] = None
    sector: str
    stage: Optional[str] = None
    problem: Optional[str] = None
    solution: Optional[str] = None
    market_size: Optional[str] = None
    traction: Optional[str] = None
    fundraising_ask: Optional[str] = None


class InvestmentPreferences(BaseModel):
    sectors: List[str]
    stage: List[str]
    check_size: str
    founder_attributes: List[str]


class PartnerProfile(BaseModel):
    partner_id: str
    name: str
    title: str
    bio: str
    expertise: List[str]
    investment_philosophy: str
    investment_preferences: InvestmentPreferences
    past_investments: List[str]


class MatchScore(BaseModel):
    overall_score: float
    sector_match: float
    stage_match: float
    founder_match: float
    expertise_match: float
    explanation: str


class PartnerCompanyMatch(BaseModel):
    partner: PartnerProfile
    company: CompanyProfile
    match_score: MatchScore


class MatchResult(BaseModel):
    top_matches: List[PartnerCompanyMatch]
    all_scores: Dict[str, Dict[str, float]]