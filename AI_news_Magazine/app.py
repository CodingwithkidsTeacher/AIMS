import requests
from openai import OpenAI
from dotenv import load_dotenv
import os

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
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    summary = response.choices[0].message.content

    return summary

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

    for article in articles:

        title = article.get("title", "No Title")

        description = article.get("description", "")

        image_url = article.get(
            "urlToImage",
            "https://via.placeholder.com/600x300"
        )

        article_url = article.get("url", "#")

        print(f"Generating summary for: {title}")

        summary = summarize_article(description)

        article_html = create_article_html(
            title,
            summary,
            image_url,
            article_url
        )

        all_articles_html += article_html

    return all_articles_html

# -----------------------------------
# STEP 5 — UPDATE WEBSITE
# -----------------------------------

def update_website(topic="technology"):

    with open("template.html", "r", encoding="utf-8") as file:
        template = file.read()

    articles_html = build_magazine(topic)

    final_html = template.replace(
        "{{ARTICLES}}",
        articles_html
    )

    with open("index.html", "w", encoding="utf-8") as file:
        file.write(final_html)

    print("✅ Website updated successfully!")

# -----------------------------------
# RUN PROJECT
# -----------------------------------

update_website("space")