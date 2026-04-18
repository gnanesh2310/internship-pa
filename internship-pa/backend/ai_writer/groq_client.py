"""Groq Llama3-70B — backup AI #1 (free tier: 14.4k tokens/min)."""
import os
from groq import Groq
from database.queries import track_api_usage

_client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))

def generate(prompt: str) -> str:
    response = _client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800,
        temperature=0.85,
    )
    text = response.choices[0].message.content.strip()
    track_api_usage("groq", tokens=response.usage.total_tokens if response.usage else 0)
    return text
