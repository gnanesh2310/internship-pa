"""OpenRouter — backup AI #2."""
import os
from openai import OpenAI
from database.queries import track_api_usage

_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY", ""),
)

def generate(prompt: str) -> str:
    response = _client.chat.completions.create(
        model="mistralai/mistral-7b-instruct:free",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800,
    )
    text = response.choices[0].message.content.strip()
    track_api_usage("openrouter", requests=1)
    return text
