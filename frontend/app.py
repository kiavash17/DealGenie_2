# frontend/app.py

import streamlit as st
import requests
import json

with open("../data/preloaded_companies.json", "r") as f:
    preloaded_companies = json.load(f)

st.set_page_config(page_title="DealCraft - VC Memo Generator", layout="centered")

st.title("📄 DealCraft: VC Due Diligence Co-Pilot")

st.write("Upload a structured startup application (JSON) and generate a full Investment Memo + Scorecard.")


st.subheader("Or pick a Preloaded Company")

company_names = [company["company_name"] for company in preloaded_companies]
selected_company = st.selectbox("Choose a company", [""] + company_names)

if selected_company:
    selected_data = next(company for company in preloaded_companies if company["company_name"] == selected_company)
    
    # For preloaded examples, create dummy ApplicationData
    app_data = {
        "company_name": selected_data["company_name"],
        "founders": ["Unknown Founder"],  # Placeholder
        "problem": "Problem description placeholder.",
        "solution": "Solution description placeholder.",
        "market_size": "Market size placeholder.",
        "traction": "Traction placeholder.",
        "fundraising_ask": "$1M seed"
    }
    st.json(app_data)

    if st.button(f"Generate Memo for {selected_data['company_name']}"):
        with st.spinner('Generating memo...'):
            response = requests.post(
                "http://localhost:8000/generate",
                json=app_data
            )

            if response.status_code == 200:
                result = response.json()
                st.subheader("🧾 Investment Memo + Scorecard")
                st.markdown(result["generated_memo"])
            else:
                st.error("Failed to generate memo. Check backend logs.")

# File uploader
uploaded_file = st.file_uploader("Upload Application JSON", type=["json"])

if uploaded_file is not None:
    # Read the uploaded JSON
    app_data = json.load(uploaded_file)

    st.subheader("Parsed Application Data")
    st.json(app_data)

    if st.button("Generate Investment Memo"):
        with st.spinner('Generating memo...'):
            # Send POST request to backend
            response = requests.post(
                "http://localhost:8000/generate",  # If deploying, change this to backend URL
                json=app_data
            )

            if response.status_code == 200:
                result = response.json()
                st.subheader("🧾 Investment Memo + Scorecard")
                st.markdown(result["generated_memo"])
            else:
                st.error("Failed to generate memo. Check backend logs.")
