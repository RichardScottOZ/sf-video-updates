import requests

OPENROUTER_API_KEY = "your_openrouter_key"
OPENROUTER_MODEL = "mistralai/mixtral-8x7b-instruct"  # Or "mistral-7b-instruct"

def query_mixtral(title: str, date: str) -> str:
    prompt = f"""<s>[INST] Summarize the sci-fi title '{title}' ({date}) in 1 sentence for a fan. 
    Focus on premise and tone. Example: "Dune (2021): A visually stunning epic of desert warfare and prophecy." 
    Keep it under 15 words. [/INST]</s>"""
    
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "https://yourdomain.com",  # OpenRouter requires this
        },
        json={
            "model": OPENROUTER_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 50,
        }
    )
    return response.json()["choices"][0]["message"]["content"]

# Usage in your existing TMDB loop:
summary = query_mixtral(movie.title, movie.release_date)