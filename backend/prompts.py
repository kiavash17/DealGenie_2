# backend/prompts.py

def generate_due_diligence_prompt(application):
    return f"""
You are a professional VC due diligence expert.

Given the following startup application:

Company Name: {application.company_name}
Founders: {', '.join(application.founders)}
Problem: {application.problem}
Solution: {application.solution}
Market Size: {application.market_size}
Traction: {application.traction}
Fundraising Ask: {application.fundraising_ask}

Please generate:

1. A clean, professional Investment Memo with the following sections:
   - Problem
   - Solution
   - Market
   - Traction
   - Team
   - Risks

2. A Scorecard in this exact Markdown table format:

| Category | Score (1–5) | Notes (Short Justification) |
|:---------|:------------|:----------------------------|
| Team | ⭐⭐⭐⭐ | Founders have strong technical backgrounds, ex-Stripe. |
| Problem | ⭐⭐⭐⭐ | Pain point is clear in B2B SaaS automation. |
| Solution | ⭐⭐⭐⭐ | Product offers real-time integrations, unique edge. |
| Market | ⭐⭐⭐ | $500M TAM, but niche in early stage. |
| Traction | ⭐⭐ | Early pilot customers, no revenue yet. |
| Business Model | ⭐⭐⭐⭐ | SaaS model, strong margins projected. |
| Competition | ⭐⭐⭐ | Several competitors, some differentiation. |
| Technology/IP | ⭐⭐ | No patents yet, working on proprietary algorithms. |
| Fundraising Ask | ⭐⭐⭐⭐ | $1M seed ask, focused on hitting clear milestones. |
| Risks | ⭐⭐⭐ | Market adoption timing uncertain. |

3. A short Investment Thesis (3–5 sentences) explaining why an investor should consider investing and any major risks.

Please output everything cleanly formatted in Markdown.
"""
