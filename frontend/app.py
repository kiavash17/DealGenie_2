# frontend/app.py

import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Load preloaded companies
with open("../data/preloaded_companies.json", "r") as f:
    preloaded_companies = json.load(f)

# Load Pear VC partners
with open("../data/pear_partners.json", "r") as f:
    pear_partners = json.load(f)

# Page configuration
st.set_page_config(
    page_title="Pear VC Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* Pear VC brand colors */
    :root {
        --pear-green: #56B68B;
        --pear-light-green: #c8e6c9;
        --pear-dark-green: #2E7D32;
        --pear-bg: #f9fcf7;
    }
    
    /* Global background */
    .stApp {
        background-color: var(--pear-bg);
    }
    
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        color: var(--pear-dark-green);
    }
    
    .dashboard-card {
        background-color: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
        border-left: 5px solid var(--pear-green);
    }
    
    .metric-card {
        background-color: white;
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        text-align: center;
        border-bottom: 3px solid var(--pear-green);
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: var(--pear-dark-green);
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #7F8C8D;
    }
    
    .sidebar-header {
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 1rem;
        color: var(--pear-dark-green);
    }
    
    /* Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        background-color: var(--pear-green);
        color: white;
        font-weight: 500;
    }
    
    .stButton>button:hover {
        background-color: var(--pear-dark-green);
    }
    
    .memo-container {
        background-color: white;
        border-radius: 8px;
        padding: 2rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin-top: 1rem;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: white;
        border-radius: 5px;
        padding: 10px 20px;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--pear-light-green);
        border-color: var(--pear-green);
    }
    
    .company-info {
        padding: 1.5rem;
        background-color: white;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
        border-left: 5px solid var(--pear-green);
    }
    
    .company-info h3 {
        color: var(--pear-dark-green);
        margin-bottom: 1rem;
    }
    
    .sector-badge {
        display: inline-block;
        padding: 5px 10px;
        background-color: var(--pear-light-green);
        color: var(--pear-dark-green);
        border-radius: 20px;
        font-size: 0.8rem;
        margin-bottom: 1rem;
    }
    
    .match-badge {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        margin-left: 10px;
    }
    
    .match-high {
        background-color: #d4edda;
        color: #28a745;
    }
    
    .match-medium {
        background-color: #fff3cd;
        color: #ffc107;
    }
    
    .match-low {
        background-color: #f8d7da;
        color: #dc3545;
    }
    
    .score-good {
        color: #27AE60;
    }
    
    .score-medium {
        color: #F39C12;
    }
    
    .score-poor {
        color: #E74C3C;
    }
    
    .partner-card {
        padding: 1.5rem;
        background-color: white;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
        border-left: 5px solid var(--pear-green);
    }
    
    .match-card {
        padding: 1.5rem;
        background-color: white;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin-bottom: 1rem;
        border-left: 5px solid;
    }
    
    .match-explanation {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin-top: 1rem;
        font-size: 0.9rem;
    }
    
    /* Sidebar adjustments */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e6e6e6;
    }
    
    /* Pear logo */
    .pear-logo {
        text-align: center;
        margin-bottom: 20px;
    }
    
    .pear-logo-text {
        font-size: 24px;
        font-weight: 700;
        color: var(--pear-dark-green);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state if not exists
if 'memo_generated' not in st.session_state:
    st.session_state.memo_generated = False
if 'generated_memo' not in st.session_state:
    st.session_state.generated_memo = ""
if 'selected_company' not in st.session_state:
    st.session_state.selected_company = None
if 'show_analysis' not in st.session_state:
    st.session_state.show_analysis = False
if 'selected_partner' not in st.session_state:
    st.session_state.selected_partner = None

# Function to calculate match score between a partner and company
def calculate_match_score(partner, company):
    """Calculate match score between a partner and a company"""
    # Default values for company data
    company_sector = company.get("sector", "")
    company_stage = "Seed"  # Default assumption
    
    # Initialize scores
    sector_match = 0.0
    stage_match = 0.0
    expertise_match = 0.0
    
    # Sector match (0-1)
    if company_sector in partner["investment_preferences"]["sectors"]:
        sector_match = 1.0
    else:
        # Check for partial matches
        for preferred_sector in partner["investment_preferences"]["sectors"]:
            if preferred_sector in company_sector:
                sector_match = 0.8
                break
            # Check if company sector includes partner's expertise areas
            for expertise in partner["expertise"]:
                if expertise in company_sector:
                    sector_match = 0.6
                    break
    
    # Stage match (0-1)
    if company_stage in partner["investment_preferences"]["stage"]:
        stage_match = 1.0
    else:
        stage_match = 0.0
    
    # Expertise match based on partner's expertise areas
    for expertise in partner["expertise"]:
        if expertise in company_sector:
            expertise_match = 1.0
            break
        # Partial match
        elif any(expertise.lower() in sector.lower() for sector in [company_sector]):
            expertise_match = 0.7
            break
    
    # Calculate overall score (weighted average)
    founder_match = 0.5  # Default to medium
    overall_score = (sector_match * 0.4) + (expertise_match * 0.3) + (stage_match * 0.2) + (founder_match * 0.1)
    
    return {
        "overall_score": overall_score,
        "sector_match": sector_match,
        "stage_match": stage_match,
        "expertise_match": expertise_match,
        "founder_match": founder_match
    }

# Function to get top matching partners for a company
def get_matching_partners(company):
    """Get top matching partners for a company"""
    matches = []
    
    for partner in pear_partners:
        score = calculate_match_score(partner, company)
        matches.append({
            "partner": partner,
            "match_score": score
        })
    
    # Sort by overall score, highest first
    matches.sort(key=lambda x: x["match_score"]["overall_score"], reverse=True)
    return matches

# Function to create match explanation
def generate_match_explanation(partner, company, match_score):
    """Generate explanation for match score"""
    explanation = f"Match analysis for {partner['name']} and {company['company_name']}:\n"
    
    # Sector match
    sector_match = match_score["sector_match"]
    explanation += f"- Sector match ({sector_match*10:.1f}/10): "
    
    if sector_match > 0.8:
        explanation += f"{company['sector']} is directly in {partner['name']}'s investment focus.\n"
    elif sector_match > 0.5:
        explanation += f"{company['sector']} is related to {partner['name']}'s investment areas.\n"
    else:
        explanation += f"{company['sector']} is outside {partner['name']}'s typical investment focus.\n"
    
    # Expertise match
    expertise_match = match_score["expertise_match"]
    explanation += f"- Expertise match ({expertise_match*10:.1f}/10): "
    if expertise_match > 0.8:
        explanation += f"{partner['name']} has strong expertise in {company['sector']}.\n"
    elif expertise_match > 0.5:
        explanation += f"{partner['name']} has some relevant expertise for {company['sector']}.\n"
    else:
        explanation += f"{partner['name']}'s expertise doesn't strongly align with {company['sector']}.\n"
    
    # Stage match
    stage_match = match_score["stage_match"]
    company_stage = "Seed"  # Default assumption
    explanation += f"- Stage match ({stage_match*10:.1f}/10): "
    if stage_match > 0.8:
        explanation += f"{company_stage} is a preferred investment stage for {partner['name']}.\n"
    else:
        explanation += f"{company_stage} is not {partner['name']}'s typical investment stage.\n"
    
    return explanation

# Function to get a matrix of all match scores
def get_all_match_scores():
    """Get a matrix of all partner-company matches"""
    all_scores = {}
    
    for company in preloaded_companies:
        company_scores = {}
        for partner in pear_partners:
            score = calculate_match_score(partner, company)
            company_scores[partner["partner_id"]] = score["overall_score"]
        all_scores[company["company_name"]] = company_scores
    
    return all_scores

# Function to get companies that match well with a specific partner
def get_partner_matching_companies(partner_id):
    """Get companies that match well with a specific partner"""
    partner = next((p for p in pear_partners if p["partner_id"] == partner_id), None)
    if not partner:
        return []
    
    matches = []
    for company in preloaded_companies:
        score = calculate_match_score(partner, company)
        matches.append({
            "company": company,
            "match_score": score
        })
    
    # Sort by overall score, highest first
    matches.sort(key=lambda x: x["match_score"]["overall_score"], reverse=True)
    return matches

# Sidebar
with st.sidebar:
    # Pear logo
    st.markdown("""
    <div class="pear-logo">
        <span class="pear-logo-text">🍐 Pear VC</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation
    page = st.radio(
        "Navigation",
        ["Company Analysis", "Partner Profiles", "Application Batch Overview"]
    )
    
    # Filters 
    st.markdown("### Filters")
    sector_filter = st.multiselect(
        "Sector",
        list(set([company.get("sector", "Unknown") for company in preloaded_companies])),
        default=[]
    )
    
    # Partner selection in sidebar
    partner_options = [""] + [partner["name"] for partner in pear_partners]
    selected_partner_name = st.selectbox(
        "Partner View",
        partner_options,
        index=0,
        format_func=lambda x: x if x else "All Partners"
    )
    
    if selected_partner_name:
        st.session_state.selected_partner = next((p for p in pear_partners if p["name"] == selected_partner_name), None)
    else:
        st.session_state.selected_partner = None
    
    # Profile section
    st.markdown("---")
    st.markdown("### User Profile")
    if st.session_state.selected_partner:
        st.markdown(f"**{st.session_state.selected_partner['name']}**")
        st.markdown(f"{st.session_state.selected_partner['title']}")
    else:
        st.markdown("Mar Hershenson")
        st.markdown("Co-Founder at Pear VC")
    st.markdown("---")
    st.markdown("© 2025 Pear VC")

# Main content based on selected page
if page == "Company Analysis":
    # Header
    st.markdown('<div class="main-header">🚀 Startup Application Analysis</div>', unsafe_allow_html=True)
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">{}</div>
            <div class="metric-label">Companies to Evaluate</div>
        </div>
        """.format(len(preloaded_companies)), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">{}</div>
            <div class="metric-label">Sectors Represented</div>
        </div>
        """.format(len(set([company.get("sector", "Unknown") for company in preloaded_companies]))), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">{}</div>
            <div class="metric-label">Pear Partners</div>
        </div>
        """.format(len(pear_partners)), unsafe_allow_html=True)
    
    # Company selection section
    st.markdown("""
    <div class="dashboard-card">
        <h3>Select Startup to Analyze</h3>
        <p>Choose a startup from the dropdown below to generate a detailed investment memo and partner match.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Filter companies by sector if filters are applied
    filtered_companies = preloaded_companies
    if sector_filter:
        filtered_companies = [c for c in preloaded_companies if c.get("sector", "Unknown") in sector_filter]
    
    # Filter companies by partner if a partner is selected
    if st.session_state.selected_partner:
        partner_matches = get_partner_matching_companies(st.session_state.selected_partner["partner_id"])
        # Only keep companies with a match score > 0.5
        good_matches = [match["company"] for match in partner_matches if match["match_score"]["overall_score"] > 0.5]
        filtered_companies = [c for c in filtered_companies if c["company_name"] in [m["company_name"] for m in good_matches]]
        
        st.markdown(f"""
        <div style="background-color: var(--pear-light-green); padding: 10px; border-radius: 5px; margin-bottom: 15px;">
            <strong>Partner Filter Active:</strong> Showing companies that match well with {st.session_state.selected_partner["name"]}'s investment profile.
        </div>
        """, unsafe_allow_html=True)
    
    # Create a list of company names for the dropdown
    company_names = [""] + [company["company_name"] for company in filtered_companies]
    
    # Dropdown for company selection
    selected_company_name = st.selectbox(
        "Select a company to analyze",
        company_names,
        index=0,
        format_func=lambda x: x if x else "Choose a company..."
    )
    
    if selected_company_name:
        # Find the selected company data
        selected_company = next((c for c in filtered_companies if c["company_name"] == selected_company_name), None)
        
        if selected_company:
            # Set session state
            st.session_state.selected_company = selected_company
            st.session_state.show_analysis = True
            
            # Get partner matches for this company
            matches = get_matching_partners(selected_company)
            top_matches = matches[:3]  # Top 3 matches
            
            # Get best matching partner
            best_match = matches[0]
            match_score = best_match["match_score"]["overall_score"] * 10
            match_class = "match-high" if match_score >= 7 else "match-medium" if match_score >= 5 else "match-low"
            match_label = f"Best Partner: {best_match['partner']['name']} ({match_score:.1f}/10)"
            
            # Display company info with partner match
            st.markdown(f"""
            <div class="company-info">
                <h3>{selected_company["company_name"]} 
                    <span class="match-badge {match_class}">{match_label}</span>
                </h3>
                <div class="sector-badge">{selected_company.get("sector", "Technology")}</div>
                <p><strong>Pitch Deck:</strong> <a href="{selected_company.get("deck_url", "#")}" target="_blank">View Deck</a></p>
            </div>
            """, unsafe_allow_html=True)
            
            # Create application data from the selected company
            app_data = {
                "company_name": selected_company["company_name"],
                "founders": ["John Doe", "Jane Smith"],  # Placeholder
                "problem": f"Problem description for {selected_company['company_name']} in the {selected_company.get('sector', 'tech')} sector.",
                "solution": f"{selected_company['company_name']} provides an innovative solution in the {selected_company.get('sector', 'tech')} space.",
                "market_size": f"The {selected_company.get('sector', 'tech')} market is growing rapidly with a projected TAM of $50B by 2026.",
                "traction": f"{selected_company['company_name']} has shown promising early traction with 25% MoM growth.",
                "fundraising_ask": "$5M seed round"
            }
            
            # Show tabs for company details, memo, scorecard, and partner matches
            tabs = st.tabs(["Company Details", "Investment Memo", "Scorecard", "Partner Matches"])
            
            with tabs[0]:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### Company Overview")
                    st.markdown(f"**Company Name:** {app_data['company_name']}")
                    st.markdown(f"**Founders:** {', '.join(app_data['founders'])}")
                    st.markdown(f"**Sector:** {selected_company.get('sector', 'Technology')}")
                    st.markdown(f"**Fundraising Ask:** {app_data['fundraising_ask']}")
                
                with col2:
                    st.markdown("### Key Metrics")
                    st.markdown("**Current Valuation:** $20M")
                    st.markdown("**Previous Round:** $1.5M Pre-seed")
                    st.markdown("**Monthly Revenue:** $100K")
                    st.markdown("**Team Size:** 15")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### Problem")
                    st.write(app_data["problem"])
                    
                    st.markdown("### Market Size")
                    st.write(app_data["market_size"])
                
                with col2:
                    st.markdown("### Solution")
                    st.write(app_data["solution"])
                    
                    st.markdown("### Traction")
                    st.write(app_data["traction"])
            
            with tabs[1]:
                # Helper function to generate memo
                def generate_memo():
                    # Create a mock memo response for demonstration
                    mock_memo = f"""
## Investment Memo: {selected_company['company_name']}

### Executive Summary
{selected_company['company_name']} is a promising startup in the {selected_company.get('sector', 'Technology')} space. The company is raising a {app_data['fundraising_ask']} to accelerate growth and capture market share in the rapidly expanding market. Based on our analysis, we recommend proceeding with the investment.

### Team Assessment
The founding team consists of industry veterans with relevant experience and a proven track record. The CEO previously founded and sold a similar company, while the CTO has deep technical expertise in the domain.

### Market Opportunity
The {selected_company.get('sector', 'Technology')} market is projected to reach $50B by 2026, growing at a CAGR of 35%. The specific segment that {selected_company['company_name']} is targeting represents a $10B opportunity. Key market drivers include:

- Growing adoption of digital solutions
- Increasing demand for efficiency
- Regulatory tailwinds

### Product & Technology
{selected_company['company_name']}'s product addresses a clear pain point in the market with a 10x improvement over existing solutions. The technology stack is modern and scalable, with a strong moat through proprietary algorithms.

### Competitive Landscape
The competitive landscape includes established players and emerging startups:

1. Competitor A - Large incumbent with legacy technology
2. Competitor B - Well-funded startup with similar approach
3. Competitor C - Potential future competitor

{selected_company['company_name']}'s key differentiators include superior technology, better user experience, and stronger go-to-market strategy.

### Business Model & Economics
- Pricing: SaaS model with $50-100 per user per month
- Gross Margins: 85-90%
- CAC: $5,000
- LTV: $50,000
- Payback Period: 10 months

### Go-to-Market Strategy
The company employs a multi-channel approach:
- Direct sales for enterprise customers
- Self-serve for SMBs
- Strategic partnerships for specific verticals

### Risks & Mitigations
1. **Competition Risk**: Potential for increased competition from well-funded startups
   *Mitigation*: Accelerate product development and customer acquisition

2. **Technical Risk**: Challenge in scaling the technology
   *Mitigation*: Experienced CTO and robust engineering team

3. **Market Risk**: Uncertainty about market adoption rate
   *Mitigation*: Strong early traction validates market demand

## Scorecard
Team: 8/10
Market: 9/10
Product: 8/10
Traction: 7/10
Economics: 8/10
Competition: 7/10
Exit Potential: 8/10

**Overall Score: 7.9/10**

## Investment Recommendation
We recommend proceeding with the investment in {selected_company['company_name']}. The combination of a strong team, large market opportunity, and compelling product makes this an attractive opportunity with potential for 10x+ returns.
"""
                    return mock_memo
                
                if not st.session_state.memo_generated:
                    if st.button("Generate Investment Memo", type="primary"):
                        with st.spinner('Generating comprehensive investment memo...'):
                            try:
                                # Set the generated memo in session state
                                st.session_state.generated_memo = generate_memo()
                                st.session_state.memo_generated = True
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
                else:
                    st.markdown('<div class="memo-container">', unsafe_allow_html=True)
                    st.markdown(st.session_state.generated_memo)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    if st.button("Regenerate Memo"):
                        st.session_state.memo_generated = False
                        st.rerun()
            
            with tabs[2]:
                if st.session_state.memo_generated:
                    st.markdown("### Investment Scorecard")
                    
                    # Create a mock scorecard for demonstration
                    scorecard_data = [
                        {"Category": "Team", "Description": "Founders and key executives", "Score": "8/10", "Class": "score-good"},
                        {"Category": "Market", "Description": "Market size and growth potential", "Score": "9/10", "Class": "score-good"},
                        {"Category": "Product", "Description": "Product differentiation and innovation", "Score": "8/10", "Class": "score-good"},
                        {"Category": "Traction", "Description": "Customer and revenue growth", "Score": "7/10", "Class": "score-medium"},
                        {"Category": "Economics", "Description": "Unit economics and business model", "Score": "8/10", "Class": "score-good"},
                        {"Category": "Competition", "Description": "Competitive advantage and moat", "Score": "7/10", "Class": "score-medium"},
                        {"Category": "Exit Potential", "Description": "Potential acquirers and exit paths", "Score": "8/10", "Class": "score-good"}
                    ]
                    
                    # Create a simple table for the scorecard
                    scorecard_df = pd.DataFrame(scorecard_data)
                    st.write("#### Scorecard Results")
                    for _, row in scorecard_df.iterrows():
                        col1, col2, col3 = st.columns([2, 5, 1])
                        with col1:
                            st.markdown(f"**{row['Category']}**")
                        with col2:
                            st.write(row['Description'])
                        with col3:
                            color = "green" if "good" in row['Class'] else "orange" if "medium" in row['Class'] else "red"
                            st.markdown(f"<span style='color:{color};font-weight:bold'>{row['Score']}</span>", unsafe_allow_html=True)
                    
                    st.markdown("""---""")
                    
                    # Create a visual representation of the scores
                    score_df = pd.DataFrame([
                        {"Category": item["Category"], "Score": float(item["Score"].split("/")[0])}
                        for item in scorecard_data
                    ])
                    
                    st.markdown("#### Visual Scorecard")
                    fig = px.bar(score_df, x='Category', y='Score', 
                                 color='Score',
                                 color_continuous_scale=px.colors.sequential.Greens,
                                 height=400)
                    fig.update_layout(
                        title="Investment Scorecard",
                        xaxis_title=None,
                        yaxis_title="Score (out of 10)",
                        coloraxis_showscale=False
                    )
                    fig.add_shape(
                        type="line",
                        x0=-0.5,
                        x1=len(score_df)-0.5,
                        y0=7.9,  # Overall score
                        y1=7.9,
                        line=dict(color="#56B68B", width=2, dash="dash")
                    )
                    fig.add_annotation(
                        x=len(score_df)-1,
                        y=7.9,
                        text="Overall Score: 7.9",
                        showarrow=False,
                        font=dict(color="#56B68B")
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Show recommendation
                    st.markdown("""
                    <div style="background-color: var(--pear-light-green); padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                        <h4 style="color: var(--pear-dark-green);">Investment Recommendation</h4>
                        <p>We recommend proceeding with the investment. The combination of a strong team, large market opportunity, and compelling product makes this an attractive opportunity with potential for 10x+ returns.</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("Generate the investment memo first to see the scorecard.")

            with tabs[3]:
                st.markdown("### Partner Match Analysis")
                st.markdown("Which Pear VC partners would be the best leads for this company?")
                
                # Display all partner matches with scores
                for i, match in enumerate(matches):
                    partner = match["partner"]
                    score = match["match_score"]
                    overall_score = score["overall_score"] * 10
                    
                    # Determine match color based on score
                    if overall_score >= 7:
                        border_color = "#27AE60"  # Green for high match
                        score_color = "green"
                    elif overall_score >= 5:
                        border_color = "#F39C12"  # Orange for medium match
                        score_color = "orange"
                    else:
                        border_color = "#E74C3C"  # Red for low match
                        score_color = "red"
                    
                    # Generate match explanation
                    explanation = generate_match_explanation(partner, selected_company, score)
                    
                    # Display match card
                    st.markdown(f"""
                    <div class="match-card" style="border-left-color: {border_color}">
                        <h4>{partner["name"]} - 
                            <span style="color: {score_color}">{overall_score:.1f}/10 Match</span>
                        </h4>
                        <p><strong>{partner["title"]}</strong></p>
                        <p>Expertise: {", ".join(partner["expertise"])}</p>
                        <p>Investment Philosophy: {partner["investment_philosophy"]}</p>
                        <p>Past Investments: {", ".join(partner["past_investments"][:3])}...</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Score breakdown
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        sector_score = score["sector_match"] * 10
                        st.markdown(f"**Sector Match:** <span style='color:{score_color}'>{sector_score:.1f}/10</span>", unsafe_allow_html=True)
                    with col2:
                        expertise_score = score["expertise_match"] * 10
                        st.markdown(f"**Expertise Match:** <span style='color:{score_color}'>{expertise_score:.1f}/10</span>", unsafe_allow_html=True)
                    with col3:
                        stage_score = score["stage_match"] * 10
                        st.markdown(f"**Stage Match:** <span style='color:{score_color}'>{stage_score:.1f}/10</span>", unsafe_allow_html=True)
                    with col4:
                        founder_score = score["founder_match"] * 10
                        st.markdown(f"**Founder Fit:** <span style='color:{score_color}'>{founder_score:.1f}/10</span>", unsafe_allow_html=True)
                    
                    # Match explanation
                    st.markdown(f"""
                    <div class="match-explanation">
                        {explanation.replace("\n", "<br>")}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("---")

elif page == "Partner Profiles":
    # Header
    st.markdown('<div class="main-header">👥 Pear VC Partner Profiles</div>', unsafe_allow_html=True)
    
    # Partner overview
    st.markdown("""
    <div class="dashboard-card">
        <h3>Pear VC Partners</h3>
        <p>View detailed profiles and investment focus areas for all Pear VC partners.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Filter partners if one is selected
    displayed_partners = [st.session_state.selected_partner] if st.session_state.selected_partner else pear_partners
    
    # Partner profiles
    for partner in displayed_partners:
        with st.expander(f"{partner['name']} - {partner['title']}", expanded=True):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"### {partner['name']}")
                st.markdown(f"**{partner['title']}**")
                st.markdown(partner['bio'])
                
                st.markdown("### Investment Philosophy")
                st.write(partner['investment_philosophy'])
                
                st.markdown("### Areas of Expertise")
                expertise_list = ", ".join(partner['expertise'])
                st.write(expertise_list)
                
                st.markdown("### Notable Investments")
                investment_list = ", ".join(partner['past_investments'])
                st.write(investment_list)
            
            with col2:
                st.markdown("### Investment Preferences")
                st.markdown("**Sectors of Interest:**")
                for sector in partner['investment_preferences']['sectors']:
                    st.markdown(f"- {sector}")
                
                st.markdown("**Preferred Stages:**")
                for stage in partner['investment_preferences']['stage']:
                    st.markdown(f"- {stage}")
                
                st.markdown(f"**Check Size:** {partner['investment_preferences']['check_size']}")
                
                st.markdown("**Founder Attributes Valued:**")
                for attr in partner['investment_preferences']['founder_attributes']:
                    st.markdown(f"- {attr}")
        
        # Best company matches for this partner
        st.markdown("#### Top Company Matches")
        
        # Calculate matches for this partner
        partner_matches = []
        for company in preloaded_companies:
            score = calculate_match_score(partner, company)
            partner_matches.append({
                "company": company,
                "score": score["overall_score"]
            })
        
        # Sort and get top 3
        partner_matches.sort(key=lambda x: x["score"], reverse=True)
        top_matches = partner_matches[:3]
        
        # Display as small cards in a row
        cols = st.columns(3)
        for i, match in enumerate(top_matches):
            with cols[i]:
                company = match["company"]
                score = match["score"] * 10
                score_color = "green" if score >= 7 else "orange" if score >= 5 else "red"
                
                st.markdown(f"""
                <div style="background-color: white; padding: 10px; border-radius: 5px; border-left: 3px solid {score_color};">
                    <h5>{company['company_name']}</h5>
                    <div class="sector-badge">{company.get('sector', 'Technology')}</div>
                    <p><strong>Match Score:</strong> <span style="color: {score_color}">{score:.1f}/10</span></p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")

elif page == "Application Batch Overview":
    # Header
    st.markdown('<div class="main-header">🔍 Application Batch Overview</div>', unsafe_allow_html=True)
    
    # Overview
    st.markdown("""
    <div class="dashboard-card">
        <h3>Partner-Company Match Matrix</h3>
        <p>A comprehensive view of how well each company matches with each Pear VC partner.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Calculate all match scores
    all_scores = get_all_match_scores()
    
    # Create a matrix for heatmap
    partner_ids = [p["partner_id"] for p in pear_partners]
    partner_names = [p["name"] for p in pear_partners]
    companies = [c["company_name"] for c in preloaded_companies]
    
    # Initialize matrix with zeros
    match_matrix = np.zeros((len(companies), len(partner_ids)))
    
    # Fill matrix with match scores
    for i, company in enumerate(companies):
        for j, partner_id in enumerate(partner_ids):
            if company in all_scores and partner_id in all_scores[company]:
                match_matrix[i, j] = all_scores[company][partner_id] * 10  # Scale to 0-10
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=match_matrix,
        x=partner_names,
        y=companies,
        colorscale='Greens',
        colorbar=dict(title="Match Score (0-10)"),
        hoverongaps=False,
        hovertemplate='Company: %{y}<br>Partner: %{x}<br>Match Score: %{z:.1f}/10<extra></extra>'
    ))
    
    fig.update_layout(
        title="Company-Partner Match Matrix",
        xaxis_title="Pear VC Partners",
        yaxis_title="Companies",
        height=600,
        margin=dict(l=50, r=50, t=50, b=50),
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Show best matches for each company
    st.markdown("### Best Partner Match by Company")
    
    # Create a table of best matches
    best_matches_data = []
    for company in preloaded_companies:
        company_name = company["company_name"]
        company_scores = all_scores.get(company_name, {})
        if company_scores:
            best_partner_id = max(company_scores, key=company_scores.get)
            best_partner = next((p for p in pear_partners if p["partner_id"] == best_partner_id), None)
            if best_partner:
                score_value = company_scores[best_partner_id] * 10
                score_class = "score-good" if score_value >= 7 else "score-medium" if score_value >= 5 else "score-poor"
                best_matches_data.append({
                    "Company": company_name,
                    "Sector": company.get("sector", "Unknown"),
                    "Best Match Partner": best_partner["name"],
                    "Match Score": f"{score_value:.1f}/10",
                    "Score Class": score_class
                })
    
    if best_matches_data:
        # Display best matches as cards
        st.markdown("### Best Partner Matches")
        
        # Create a custom grid display
        total_companies = len(best_matches_data)
        cols_per_row = 3
        rows_needed = (total_companies + cols_per_row - 1) // cols_per_row
        
        for row in range(rows_needed):
            cols = st.columns(cols_per_row)
            for col in range(cols_per_row):
                idx = row * cols_per_row + col
                if idx < total_companies:
                    match = best_matches_data[idx]
                    score_color = "green" if "good" in match["Score Class"] else "orange" if "medium" in match["Score Class"] else "red"
                    
                    with cols[col]:
                        st.markdown(f"""
                        <div style="background-color: white; padding: 15px; border-radius: 8px; border-left: 4px solid {score_color}; margin-bottom: 15px; height: 150px;">
                            <h4>{match["Company"]}</h4>
                            <div class="sector-badge">{match["Sector"]}</div>
                            <p><strong>Lead Partner:</strong> {match["Best Match Partner"]}</p>
                            <p><strong>Match Score:</strong> <span style="color: {score_color}">{match["Match Score"]}</span></p>
                        </div>
                        """, unsafe_allow_html=True)
    
    # Filter by selected partner if applicable
    if st.session_state.selected_partner:
        st.markdown(f"### {st.session_state.selected_partner['name']}'s Best Matches")
        
        # Get matches for this specific partner
        partner_id = st.session_state.selected_partner["partner_id"]
        partner_match_data = []
        
        for company in preloaded_companies:
            company_name = company["company_name"]
            if company_name in all_scores and partner_id in all_scores[company_name]:
                score = all_scores[company_name][partner_id] * 10
                score_class = "score-good" if score >= 7 else "score-medium" if score >= 5 else "score-poor"
                partner_match_data.append({
                    "Company": company_name,
                    "Sector": company.get("sector", "Unknown"),
                    "Match Score": f"{score:.1f}/10",
                    "Score Class": score_class,
                    "Score Value": score
                })
        
        # Sort by score
        partner_match_data.sort(key=lambda x: x["Score Value"], reverse=True)
        
        # Display as a table
        if partner_match_data:
            match_df = pd.DataFrame([
                {"Company": item["Company"], 
                 "Sector": item["Sector"], 
                 "Match Score": item["Match Score"]}
                for item in partner_match_data
            ])
            
            st.dataframe(match_df, use_container_width=True, hide_index=True)
    
    # Show sector analysis
    st.markdown("### Sector Analysis")
    
    # Group companies by sector
    sectors = {}
    for company in preloaded_companies:
        sector = company.get("sector", "Unknown")
        if sector not in sectors:
            sectors[sector] = []
        sectors[sector].append(company)
    
    # Create a bar chart of sectors
    sector_counts = pd.DataFrame([
        {"Sector": sector, "Count": len(companies)}
        for sector, companies in sectors.items()
    ])
    
    fig = px.bar(sector_counts, x="Sector", y="Count",
                 title="Companies by Sector",
                 color="Count", 
                 color_continuous_scale=px.colors.sequential.Greens)
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
    
    # Partner coverage by sector
    st.markdown("### Partner Coverage by Sector")
    
    # Calculate average match score by sector for each partner
    sector_partner_scores = {}
    
    for sector, companies in sectors.items():
        sector_partner_scores[sector] = {}
        for partner in pear_partners:
            partner_id = partner["partner_id"]
            sector_scores = []
            
            for company in companies:
                company_name = company["company_name"]
                if company_name in all_scores and partner_id in all_scores[company_name]:
                    sector_scores.append(all_scores[company_name][partner_id])
            
            if sector_scores:
                sector_partner_scores[sector][partner["name"]] = np.mean(sector_scores) * 10
    
    # Create a heatmap of sector-partner matches
    sector_names = list(sector_partner_scores.keys())
    
    if sector_names:
        sector_matrix = np.zeros((len(sector_names), len(partner_names)))
        
        for i, sector in enumerate(sector_names):
            for j, partner_name in enumerate(partner_names):
                if partner_name in sector_partner_scores[sector]:
                    sector_matrix[i, j] = sector_partner_scores[sector][partner_name]
        
        fig = go.Figure(data=go.Heatmap(
            z=sector_matrix,
            x=partner_names,
            y=sector_names,
            colorscale='Greens',
            colorbar=dict(title="Avg. Match Score (0-10)"),
            hoverongaps=False,
            hovertemplate='Sector: %{y}<br>Partner: %{x}<br>Avg. Match: %{z:.1f}/10<extra></extra>'
        ))
        
        fig.update_layout(
            title="Average Partner Match Scores by Sector",
            xaxis_title="Pear VC Partners",
            yaxis_title="Sectors",
            height=500,
            margin=dict(l=50, r=50, t=50, b=50),
        )
        
        st.plotly_chart(fig, use_container_width=True)