"""Gemini 1.5 Flash — primary AI provider (free tier: 1M tokens/day)."""
import os
import google.generativeai as genai
from database.queries import track_api_usage

genai.configure(api_key=os.environ.get("GEMINI_API_KEY", ""))

_model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=genai.GenerationConfig(
        temperature=0.85,
        max_output_tokens=800,
    )
)

def generate(prompt: str) -> str:
    """Call Gemini and return the text response. Raises on failure."""
    response = _model.generate_content(prompt)
    text = response.text.strip()
    # Rough token estimate for tracking
    tokens_est = len(prompt.split()) + len(text.split())
    track_api_usage("gemini", tokens=tokens_est * 2)
    return text
