import requests, json, smtplib
from tmdbv3api import TMDb, Movie, TV
from datetime import datetime
from email.mime.text import MIMEText

# --- Config ---
TMDB_API_KEY = "your_tmdb_key"          # Get from TMDB
OPENROUTER_API_KEY = "your_openrouter_key"
EMAIL_FROM = "your_email@gmail.com"      # Gmail (or SMTP server)
EMAIL_TO = "recipient@example.com"
EMAIL_PASSWORD = "your_app_password"     # For Gmail, use an "App Password"  https://myaccount.google.com/apppasswords

# --- OpenRouter Setup ---
OPENROUTER_MODEL = "anthropic/claude-3-haiku"  # $0.25/$0.75 per 1K tokens

def query_openrouter(prompt: str) -> str:
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
        json={"model": OPENROUTER_MODEL, "messages": [{"role": "user", "content": prompt}]}
    )
    return response.json()["choices"][0]["message"]["content"]

# --- TMDB Data Fetch ---
def get_new_sci_fi_entries():
    tmdb = TMDb()
    tmdb.api_key = TMDB_API_KEY
    tmdb.language = "en"

    movies = [m for m in Movie().upcoming() if 878 in m.genre_ids]  # Sci-Fi ID
    tv_shows = [s for s in TV().on_the_air() if 10765 in s.genre_ids]  # Sci-Fi/Fantasy ID

    # Load cached titles to avoid repeats
    try:
        with open("sent_titles.json", "r") as f:
            sent_titles = json.load(f)
    except FileNotFoundError:
        sent_titles = []

    new_entries = []
    for item in movies + tv_shows:
        title = item.title if hasattr(item, "title") else item.name
        if title not in sent_titles:
            date = item.release_date if hasattr(item, "release_date") else item.first_air_date
            prompt = f"Summarize '{title}' in 1 sentence for a sci-fi fan. Focus on premise, not reviews. Example: 'Dune (2021): A young noble leads a rebellion on a desert planet rich with a hallucinogenic spice.' Output:"
            summary = query_openrouter(prompt)
            new_entries.append((title, date, summary))
            sent_titles.append(title)

    # Update cache
    with open("sent_titles.json", "w") as f:
        json.dump(sent_titles, f)

    return new_entries

# --- Email Sending ---
def send_email(content: str):
    msg = MIMEText(content, "html")
    msg["Subject"] = "🚀 Daily Sci-Fi Digest"
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO

    with smtplib.SMTP("smtp.gmail.com", 587) as server:  # For Gmail
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.send_message(msg)

# --- Main ---
if __name__ == "__main__":
    entries = get_new_sci_fi_entries()
    if entries:
        email_content = "<h2>📡 New Sci-Fi Releases</h2><ul>"
        for title, date, summary in entries:
            email_content += f"<li><b>{title} ({date})</b>: {summary}</li>"
        email_content += "</ul>"
        send_email(email_content)
    else:
        print("No new sci-fi titles today.")