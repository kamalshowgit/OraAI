from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()  # ← THIS LINE IS CRITICAL

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise RuntimeError("GROQ_API_KEY is not set")

client = Groq(api_key=api_key)

MODEL_NAME = "llama-3.3-70b-versatile"

def call_groq(messages):
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        temperature=0,
    )
    return response.choices[0].message.content
