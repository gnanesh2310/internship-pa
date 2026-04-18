"""Together AI — backup AI #3."""
import os
from together import Together
from database.queries import track_api_usage

os.environ["TOGETHER_API_KEY"] = os.environ.get("TOGETHER_API_KEY", "")
_client = Together()

def generate(prompt: str) -> str:
    response = _client.chat.completions.create(
        model="mistralai/Mixtral-8x7B-Instruct-v0.1",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800,
        temperature=0.85,
    )
    text = response.choices[0].message.content.strip()
    track_api_usage("together", requests=1)
    return text