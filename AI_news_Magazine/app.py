import requests
from openai import OpenAI
from dotenv import load_dotenv
import os
import json  # ✅ ADDED for JSON saving

# Load API keys
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# -----------------------------------
# STEP 1 — GET NEWS ARTICLES
# -----------------------------------

def get_news(topic="technology"):
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "q": topic,
        "language": "en",
        "pageSize": 5,
        "apiKey": NEWS_API_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data["articles"]

# -----------------------------------
# STEP 2 — SUMMARIZE ARTICLE
# -----------------------------------

def summarize_article(article_text):
    prompt = f"""
    Summarize this news article in 2 short sentences.
    Make it exciting and easy for students to understand.

    Article:
    {article_text}
    """
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    summary = response.choices[0].message.content
    return summary

def generate_headline(original_title, summary):
    response = client.chat.completions.create(  # Fixed: changed openai_client to client
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Rewrite this news headline to be more engaging for a young audience."},
            {"role": "user", "content": f"Original: {original_title}\nSummary: {summary}"}
        ]
    )
    return response.choices[0].message.content

# -----------------------------------
# STEP 3 — CREATE HTML ARTICLE
# -----------------------------------

def create_article_html(title, summary, image_url, article_url):
    html = f"""
    <div class="article">
        <h2>{title}</h2>
        <img src="{image_url}" width="100%">
        <p>{summary}</p>
        <a href="{article_url}" target="_blank">
            Read Full Article
        </a>
    </div>
    """
    return html

# -----------------------------------
# STEP 4 — BUILD MAGAZINE
# -----------------------------------

def build_magazine(topic="technology"):
    articles = get_news(topic)
    all_articles_html = ""
    processed_articles = []  # ✅ ADDED for JSON storage

    for article in articles:
        title = article.get("title", "No Title")
        description = article.get("description", "")
        image_url = article.get("urlToImage", "https://via.placeholder.com/600x300")
        article_url = article.get("url", "#")

        print(f"Generating summary for: {title}")
        summary = summarize_article(description)

        # ✅ ADDED: Save to list for JSON
        processed_articles.append({
            "title": title,
            "summary": summary,
            "image_url": image_url,
            "article_url": article_url
        })

        article_html = create_article_html(title, summary, image_url, article_url)
        all_articles_html += article_html

    # ✅ ADDED: Save to JSON file
    with open("articles.json", "w", encoding="utf-8") as f:
        json.dump(processed_articles, f, indent=2)
    print(f"💾 Saved {len(processed_articles)} articles to articles.json")

    return all_articles_html

# -----------------------------------
# STEP 5 — UPDATE WEBSITE
# -----------------------------------

def update_website(topic="technology"):
    with open("template.html", "r", encoding="utf-8") as file:
        template = file.read()

    articles_html = build_magazine(topic)

    final_html = template.replace("{{ARTICLES}}", articles_html)

    with open("index.html", "w", encoding="utf-8") as file:
        file.write(final_html)

    print("✅ Website updated successfully!")

# -----------------------------------
# RUN PROJECT
# -----------------------------------

if __name__ == "__main__":
    # ✅ ADDED: Topic selection
    user_topic = input("Enter news topic (technology, sports, science, space): ") or "space"
    print(f"\n📰 Creating magazine about: {user_topic}\n")
    update_website(user_topic)
