import os

import gradio as gr
from dotenv import load_dotenv
from groq import Groq


# -----------------------------------
# LOAD SECRET KEY
# -----------------------------------
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if GROQ_API_KEY:
    groq_client = Groq(api_key=GROQ_API_KEY)
else:
    groq_client = None


# -----------------------------------
# GAME UPDATES
# -----------------------------------
GAMES = {
    "Minecraft": [
        "New cave biome added",
        "Minecraft snapshot released",
        "New mob announced",
    ],
    "Fortnite": [
        "Star Wars crossover event",
        "New ranked mode update",
        "Limited-time skins added",
    ],
    "Roblox": [
        "Roblox event announced",
        "New creator tools added",
        "Trending simulator released",
    ],
    "Nintendo": [
        "Nintendo Direct announced",
        "New Mario game teased",
        "Switch update released",
    ],
    "Steam": [
        "Big indie game sale",
        "Top trending games updated",
        "New survival game released",
    ],
}


# -----------------------------------
# BACKUP SUMMARY
# -----------------------------------
def make_backup_summary(game, updates):
    update_text = ", ".join(updates)

    return (
        f"{game} has some exciting updates! "
        f"Players can check out: {update_text}."
    )


# -----------------------------------
# ASK GROQ TO WRITE REPORT
# -----------------------------------
def ask_groq(game, updates):
    if groq_client is None:
        return make_backup_summary(game, updates)

    update_text = ""

    for update in updates:
        update_text += "- " + update + "\n"

    prompt = f"""
You are writing a short gaming news report for kids age 8-12.

Write ONLY the report.

Rules:
- Write 2 short sentences.
- Use simple words.
- Make it fun and exciting.
- Do not say "Here is a summary."
- Do not use bullet points.
- Do not invent extra facts.
- Only use the updates below.

Game:
{game}

Updates:
{update_text}
"""

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.5,
            max_tokens=100
        )

        return response.choices[0].message.content.strip()

    except Exception:
        return make_backup_summary(game, updates)


# -----------------------------------
# CREATE REPORT
# -----------------------------------
def create_report(game):
    updates = GAMES.get(game)

    if not updates:
        return "❌ Game not found."

    summary = ask_groq(game, updates)

    update_list = ""

    for update in updates:
        update_list += f"• {update}\n"

    report = f"""🎮 {game} Gaming Report

🕹️ Game Updates:
{update_list}

🤖 AI Report:
{summary}
"""

    return report


# -----------------------------------
# GRADIO APP
# -----------------------------------
with gr.Blocks(title="AI Gaming News Agent") as app:

    gr.Markdown("# 🎮 AI Gaming News Agent")
    gr.Markdown("Choose a game and let AI create a kid-friendly gaming report.")

    game_dropdown = gr.Dropdown(
        choices=list(GAMES.keys()),
        value="Minecraft",
        label="Choose a Game"
    )

    generate_button = gr.Button("Generate Report", variant="primary")

    report_output = gr.Textbox(
        label="Gaming Report",
        lines=15
    )

    generate_button.click(
        fn=create_report,
        inputs=game_dropdown,
        outputs=report_output
    )


# -----------------------------------
# START APP
# -----------------------------------
if __name__ == "__main__":
    app.launch()