# frontend/app.py

import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px

# Load preloaded companies
with open("../data/preloaded_companies.json", "r") as f:
    preloaded_companies = json.load(f)

# Page configuration
st.set_page_config(
    page_title="DealCraft Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        color: #2E4053;
    }
    .dashboard-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: white;
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        text-align: center;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #3498DB;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #7F8C8D;
    }
    .sidebar-header {
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        background-color: #3498DB;
        color: white;
        font-weight: 500;
    }
    .stButton>button:hover {
        background-color: #2980B9;
    }
    .memo-container {
        background-color: white;
        border-radius: 8px;
        padding: 2rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin-top: 1rem;
    }
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
        background-color: #eaf4fb;
        border-color: #3498DB;
    }
    .company-info {
        padding: 1.5rem;
        background-color: white;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
    }
    .company-info h3 {
        color: #2E4053;
        margin-bottom: 1rem;
    }
    .sector-badge {
        display: inline-block;
        padding: 5px 10px;
        background-color: #eaf4fb;
        color: #3498DB;
        border-radius: 20px;
        font-size: 0.8rem;
        margin-bottom: 1rem;
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

# Sidebar
with st.sidebar:
    st.markdown('<div class="sidebar-header">DealCraft VC Dashboard</div>', unsafe_allow_html=True)
    
    # Navigation
    page = st.radio(
        "Navigation",
        ["Company Analysis", "Portfolio Overview"]
    )
    
    # Filters 
    st.markdown("### Filters")
    sector_filter = st.multiselect(
        "Sector",
        list(set([company.get("sector", "Unknown") for company in preloaded_companies])),
        default=[]
    )
    
    # Profile section
    st.markdown("---")
    st.markdown("### User Profile")
    st.markdown("Jane Smith")
    st.markdown("Partner at Acme Ventures")
    st.markdown("---")
    st.markdown("© 2025 DealCraft")

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
            <div class="metric-value">2.5 min</div>
            <div class="metric-label">Avg. Analysis Time</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Company selection section
    st.markdown("""
    <div class="dashboard-card">
        <h3>Select Startup to Analyze</h3>
        <p>Choose a startup from the dropdown below to generate a detailed investment memo and scorecard.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Filter companies by sector if filters are applied
    filtered_companies = preloaded_companies
    if sector_filter:
        filtered_companies = [c for c in preloaded_companies if c.get("sector", "Unknown") in sector_filter]
    
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
            
            # Display company info
            st.markdown(f"""
            <div class="company-info">
                <h3>{selected_company["company_name"]}</h3>
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
            
            # Show tabs for company details and analysis
            tabs = st.tabs(["Company Details", "Investment Memo", "Scorecard"])
            
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
                                 color_continuous_scale=px.colors.sequential.Blues,
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
                        line=dict(color="red", width=2, dash="dash")
                    )
                    fig.add_annotation(
                        x=len(score_df)-1,
                        y=7.9,
                        text="Overall Score: 7.9",
                        showarrow=False,
                        font=dict(color="red")
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Show recommendation
                    st.markdown("""
                    <div style="background-color: #eaf4fb; padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                        <h4 style="color: #3498DB;">Investment Recommendation</h4>
                        <p>We recommend proceeding with the investment. The combination of a strong team, large market opportunity, and compelling product makes this an attractive opportunity with potential for 10x+ returns.</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("Generate the investment memo first to see the scorecard.")

elif page == "Portfolio Overview":
    # Header
    st.markdown('<div class="main-header">💼 Portfolio Overview</div>', unsafe_allow_html=True)
    
    # Sector distribution chart
    st.markdown("""
    <div class="dashboard-card">
        <h3>Sector Distribution</h3>
    </div>
    """, unsafe_allow_html=True)
    
    sector_counts = pd.DataFrame({
        "Sector": [company.get("sector", "Unknown") for company in preloaded_companies]
    }).value_counts("Sector").reset_index()
    sector_counts.columns = ["Sector", "Count"]
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.pie(sector_counts, values='Count', names='Sector', 
                      color_discrete_sequence=px.colors.sequential.Blues,
                      hole=0.4)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(margin=dict(t=30, b=30, l=30, r=30))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(sector_counts, x='Sector', y='Count', 
                     color='Sector', color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_layout(showlegend=False, margin=dict(t=30, b=30, l=30, r=30))
        st.plotly_chart(fig, use_container_width=True)
    
    # Companies table
    st.markdown("""
    <div class="dashboard-card">
        <h3>All Companies</h3>
    </div>
    """, unsafe_allow_html=True)
    
    companies_df = pd.DataFrame([
        {
            "Company": company["company_name"],
            "Sector": company.get("sector", "Unknown"),
            "Deck": company.get("deck_url", "N/A")
        }
        for company in preloaded_companies
    ])
    
    st.dataframe(companies_df, use_container_width=True, hide_index=True)