import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(PROJECT_ROOT / ".env.name", override=True)

MODEL_NAME = "llama-3.3-70b-versatile"


def get_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Add it to your environment or .env before using AI query mode."
        )
    lowered = api_key.strip().lower()
    if lowered in {"dummy", "drop your groq api key here", "your_groq_api_key"}:
        raise RuntimeError(
            "GROQ_API_KEY is a placeholder value. Set a real Groq API key in .env or environment."
        )
    return Groq(api_key=api_key)


def call_groq(messages):
    client = get_client()
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        temperature=0,
    )
    return response.choices[0].message.content
