# backend/main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import os
from typing import List, Dict, Optional
from dotenv import load_dotenv
from openai import OpenAI
from prompts import generate_due_diligence_prompt
from models import (
    CompanyProfile, 
    PartnerProfile, 
    MatchScore, 
    PartnerCompanyMatch, 
    MatchResult
)

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

# Path to data files
PARTNERS_DATA_PATH = "../data/pear_partners.json"
COMPANIES_DATA_PATH = "../data/preloaded_companies.json"

class ApplicationData(BaseModel):
    company_name: str
    founders: list
    problem: str
    solution: str
    market_size: str
    traction: str
    fundraising_ask: str

def load_partners():
    """Load partner data from JSON file"""
    try:
        with open(PARTNERS_DATA_PATH, "r") as f:
            partners_data = json.load(f)
        
        # Convert raw data to PartnerProfile objects
        partners = [PartnerProfile(**partner) for partner in partners_data]
        return partners
    except Exception as e:
        print(f"Error loading partner data: {e}")
        return []

def load_companies():
    """Load company data from JSON file"""
    try:
        with open(COMPANIES_DATA_PATH, "r") as f:
            companies_data = json.load(f)
            
        # Convert to CompanyProfile objects
        # Note: This is a simplified version as our preloaded_companies.json has minimal data
        companies = []
        for company in companies_data:
            # Add default values for required fields
            if "stage" not in company:
                if "sector" in company and "AI" in company["sector"]:
                    company["stage"] = "Seed"
                else:
                    company["stage"] = "Series A"
                    
            companies.append(CompanyProfile(**company))
        return companies
    except Exception as e:
        print(f"Error loading company data: {e}")
        return []

def calculate_match_score(partner: PartnerProfile, company: CompanyProfile) -> MatchScore:
    """
    Calculate match score between a partner and a company
    Returns a MatchScore object with scores and explanation
    """
    # Initialize scores
    sector_match = 0.0
    stage_match = 0.0
    expertise_match = 0.0
    founder_match = 0.5  # Default to medium since we don't have much founder data
    
    # Sector match (0-1)
    if company.sector in partner.investment_preferences.sectors:
        sector_match = 1.0
    else:
        # Check for partial matches
        for preferred_sector in partner.investment_preferences.sectors:
            if preferred_sector in company.sector:
                sector_match = 0.8
                break
            # Check if company sector includes partner's expertise areas
            for expertise in partner.expertise:
                if expertise in company.sector:
                    sector_match = 0.6
                    break
    
    # Stage match (0-1)
    if company.stage in partner.investment_preferences.stage:
        stage_match = 1.0
    else:
        stage_match = 0.0
    
    # Expertise match based on partner's expertise areas
    for expertise in partner.expertise:
        if expertise in company.sector:
            expertise_match = 1.0
            break
        # Partial match
        elif any(expertise.lower() in sector.lower() for sector in [company.sector]):
            expertise_match = 0.7
            break
    
    # Calculate overall score (weighted average)
    # Sector match is most important, followed by expertise and stage
    overall_score = (sector_match * 0.4) + (expertise_match * 0.3) + (stage_match * 0.2) + (founder_match * 0.1)
    
    # Generate explanation
    explanation = f"Match analysis for {partner.name} and {company.company_name}:\n"
    explanation += f"- Sector match ({sector_match*10}/10): "
    
    if sector_match > 0.8:
        explanation += f"{company.sector} is directly in {partner.name}'s investment focus.\n"
    elif sector_match > 0.5:
        explanation += f"{company.sector} is related to {partner.name}'s investment areas.\n"
    else:
        explanation += f"{company.sector} is outside {partner.name}'s typical investment focus.\n"
    
    explanation += f"- Expertise match ({expertise_match*10}/10): "
    if expertise_match > 0.8:
        explanation += f"{partner.name} has strong expertise in {company.sector}.\n"
    elif expertise_match > 0.5:
        explanation += f"{partner.name} has some relevant expertise for {company.sector}.\n"
    else:
        explanation += f"{partner.name}'s expertise doesn't strongly align with {company.sector}.\n"
    
    explanation += f"- Stage match ({stage_match*10}/10): "
    if stage_match > 0.8:
        explanation += f"{company.stage} is a preferred investment stage for {partner.name}.\n"
    else:
        explanation += f"{company.stage} is not {partner.name}'s typical investment stage.\n"
    
    return MatchScore(
        overall_score=overall_score,
        sector_match=sector_match,
        stage_match=stage_match,
        founder_match=founder_match,
        expertise_match=expertise_match,
        explanation=explanation
    )

def match_partners_to_company(company: CompanyProfile) -> List[PartnerCompanyMatch]:
    """
    Match a company to all partners and return sorted results
    """
    partners = load_partners()
    matches = []
    
    for partner in partners:
        score = calculate_match_score(partner, company)
        match = PartnerCompanyMatch(
            partner=partner,
            company=company,
            match_score=score
        )
        matches.append(match)
    
    # Sort by overall score, highest first
    matches.sort(key=lambda x: x.match_score.overall_score, reverse=True)
    return matches

def get_all_matches() -> Dict[str, Dict[str, float]]:
    """
    Generate a matrix of all partner-company match scores
    Used for visualization on the dashboard
    """
    partners = load_partners()
    companies = load_companies()
    
    all_scores = {}
    
    for company in companies:
        company_scores = {}
        for partner in partners:
            score = calculate_match_score(partner, company)
            company_scores[partner.partner_id] = score.overall_score
        all_scores[company.company_name] = company_scores
    
    return all_scores

@app.post("/generate")
async def generate_memo(application: ApplicationData):
    """Generate investment memo for a company"""
    # Build the prompt
    prompt = generate_due_diligence_prompt(application)

    # Call the LLM
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a professional VC due diligence expert."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5,
        max_tokens=3000,
    )

    output_text = response.choices[0].message.content

    return {"generated_memo": output_text}

@app.get("/partners")
async def get_partners():
    """Get all partner profiles"""
    partners = load_partners()
    return {"partners": partners}

@app.get("/companies")
async def get_companies():
    """Get all company profiles"""
    companies = load_companies()
    return {"companies": companies}

@app.get("/match/company/{company_name}")
async def match_company(company_name: str):
    """Match a specific company with partners"""
    companies = load_companies()
    company = next((c for c in companies if c.company_name == company_name), None)
    
    if not company:
        raise HTTPException(status_code=404, detail=f"Company {company_name} not found")
    
    matches = match_partners_to_company(company)
    top_matches = matches[:3]  # Get top 3 matches
    
    all_scores = get_all_matches()
    
    return MatchResult(
        top_matches=top_matches,
        all_scores=all_scores
    )

@app.get("/match/all")
async def match_all():
    """Get all company-partner matches"""
    all_scores = get_all_matches()
    
    # Also get company objects for detailed info
    companies = load_companies()
    partners = load_partners()
    
    top_matches_by_company = {}
    for company in companies:
        matches = match_partners_to_company(company)
        top_matches_by_company[company.company_name] = matches[0]  # Best match
    
    return {
        "all_scores": all_scores,
        "top_matches_by_company": top_matches_by_company
    }