from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import requests

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if GROQ_API_KEY is None:
    raise RuntimeError("GROQ_API_KEY is not set")

app = FastAPI() # Turns the functions below into HTTP endpoints

class AnalyzeRequest(BaseModel):
    code: str
    error: str | None

@app.post("/analyze") # When I send an HTTP POST request to /analyze, the function below is ran
def analyze(req: AnalyzeRequest):
    prompt = f"""
You are a coding tutor/assistant of AI and Data Science bootcamp students. Your role is to support the students in learning Python. For this reason your role is to explain the errors their codes get, why, and to guide them to fix the code and also learn. Importantly, you must not provide the solution code itself, and only guidance. 

Student code:
{req.code or "[EMPTY CODE]"}

Error message:
{req.error or "No error message"}

Explain:
1. What is the issue?
2. Why did it happen?
3. How to fix it?
4. Give a minimal example or a hint.
"""

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "user", "content": prompt}]
        }
    )

    return {
        "analysis": response.json()["choices"][0]["message"]["content"]
    }
