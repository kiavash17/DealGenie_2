# backend/main.py

from fastapi import FastAPI
from pydantic import BaseModel
import json
from prompts import generate_due_diligence_prompt
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

class ApplicationData(BaseModel):
    company_name: str
    founders: list
    problem: str
    solution: str
    market_size: str
    traction: str
    fundraising_ask: str

@app.post("/generate")
async def generate_memo(application: ApplicationData):
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
