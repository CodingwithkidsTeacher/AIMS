import os
import json
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq
from eventregistry import (
    EventRegistry,
    GetTrendingConcepts,
    QueryArticlesIter
)

# -----------------------
# LOAD API KEYS
# -----------------------
load_dotenv()

NEWS_KEY = os.getenv("EVENT_REGISTRY_API_KEY") or os.getenv("NEWS_API_KEY")
GROQ_KEY = os.getenv("GROQ_API_KEY")

if not NEWS_KEY:
    raise ValueError("Missing news API key")

if not GROQ_KEY:
    raise ValueError("Missing GROQ_API_KEY")

news_api = EventRegistry(apiKey=NEWS_KEY)
groq = Groq(api_key=GROQ_KEY)


# -----------------------
# GET TRENDING TOPICS
# -----------------------
def get_topics():
    print("🔥 Getting trending topics...")

    query = GetTrendingConcepts(source="news", count=5)
    results = news_api.execQuery(query)

    topics = []

    for item in results:
        name = item.get("label", {}).get("eng")

        if name:
            topics.append(name)

    return topics


# -----------------------
# GET NEWS ARTICLES
# -----------------------
def get_articles(topic):
    print(f"📰 Getting articles about: {topic}")

    query = QueryArticlesIter(keywords=topic)

    articles = []
    seen_titles = set()

    for article in query.execQuery(news_api, maxItems=15):

        title = article.get("title", "No title")
        clean_title = title.lower().strip()

        # Skip duplicate titles
        if clean_title in seen_titles:
            continue

        seen_titles.add(clean_title)

        articles.append({
            "title": title,
            "url": article.get("url", ""),
            "image": article.get("image") or "https://via.placeholder.com/600x400",
            "source": article.get("source", {}).get("title", "Unknown"),
            "date": article.get("date", "")
        })

        if len(articles) >= 5:
            break

    return articles


# -----------------------
# ASK GROQ TO SUMMARIZE
# -----------------------
def summarize_topic(topic, articles):
    print(f"🤖 Summarizing: {topic}")

    article_text = ""

    for article in articles:
        article_text += "- " + article["title"] + "\n"

    prompt = f"""
You are writing for a modern online news magazine for kids age 8-12.

Write ONLY the summary.

Rules:
- Write 2 short sentences
- Sound exciting and natural
- Do NOT say:
  "Here is a summary"
  "Here’s a summary"
  "In summary"
- Do NOT use bullet points
- Keep it easy for kids to understand

Topic: {topic}

Article titles:
{article_text}
"""

    response = groq.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,
        max_tokens=120
    )

    return response.choices[0].message.content


# -----------------------
# BUILD NEWS JSON
# -----------------------
def build_news(topics):

    magazine = {
        "generatedAt": str(datetime.now()),
        "topics": []
    }

    for topic in topics:

        articles = get_articles(topic)

        if len(articles) == 0:
            continue

        summary = summarize_topic(topic, articles)

        magazine["topics"].append({
            "name": topic,
            "summary": summary,
            "articles": articles
        })

    return magazine


# -----------------------
# SAVE TO FILE
# -----------------------
def save_news(data):

    with open("news.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

    print("✅ Saved news.json")


# -----------------------
# MAIN PROGRAM
# -----------------------
print("\n📡 AI News Magazine Generator\n")

mode = input(
    "Type 't' for trending news or 's' to search your own topic: "
).lower()

topics = []

# -----------------------
# TRENDING MODE
# -----------------------
if mode == "t":

    topics = get_topics()

# -----------------------
# SEARCH MODE
# -----------------------
elif mode == "s":

    custom_topic = input(
        "Enter a topic (AI, sports, Tesla, Minecraft): "
    )

    topics = [custom_topic]

# -----------------------
# FALLBACK
# -----------------------
else:
    print("❌ Invalid choice")
    exit()

print("\n🧠 Topics:")
print(topics)

print("\n📰 Building news magazine...\n")

news_data = build_news(topics)

save_news(news_data)

print("\n🎉 Done! Open index.html")
