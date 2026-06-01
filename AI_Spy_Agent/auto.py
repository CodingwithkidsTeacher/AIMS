import os
import requests

import gradio as gr
from dotenv import load_dotenv
from groq import Groq


# -----------------------------------
# LOAD SECRET KEYS
# -----------------------------------
load_dotenv()

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK", "").strip()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()

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
# SEND DISCORD MESSAGE
# -----------------------------------
def send_to_discord(message):
    if not DISCORD_WEBHOOK:
        return "⚠️ Discord webhook is missing. Check your .env file."

    if not message or not message.strip():
        return "⚠️ Cannot send an empty message."

    if len(message) > 1900:
        message = message[:1900] + "\n\n...Message shortened."

    payload = {
        "content": message
    }

    try:
        response = requests.post(
            DISCORD_WEBHOOK,
            json=payload,
            timeout=10
        )

        if response.status_code in [200, 204]:
            return "✅ Sent to Discord!"

        return f"❌ Discord error: {response.status_code} - {response.text}"

    except requests.RequestException as error:
        return f"❌ Discord request failed: {error}"


# -----------------------------------
# GENERATE AND SEND ONCE
# -----------------------------------
def generate_and_send_to_discord(game):
    report = create_report(game)

    if report.startswith("❌"):
        return report

    discord_result = send_to_discord(report)
    gr.Info(discord_result)

    return report


# -----------------------------------
# AUTO UPDATE FUNCTION
# -----------------------------------
def auto_update_report(game, auto_send_discord):
    report = create_report(game)

    if auto_send_discord:
        discord_result = send_to_discord(report)
        print(discord_result)

    return report


# -----------------------------------
# START AUTO UPDATE
# -----------------------------------
def start_auto_update(minutes):
    try:
        minutes = float(minutes)
    except ValueError:
        gr.Warning("Please enter a number for minutes.")
        return gr.Timer(active=False)

    if minutes <= 0:
        gr.Warning("Minutes must be greater than 0.")
        return gr.Timer(active=False)

    seconds = minutes * 60

    gr.Info(f"Auto update started. The agent will update every {minutes} minute(s).")

    return gr.Timer(value=seconds, active=True)


# -----------------------------------
# STOP AUTO UPDATE
# -----------------------------------
def stop_auto_update():
    gr.Info("Auto update stopped.")
    return gr.Timer(active=False)


# -----------------------------------
# GRADIO APP
# -----------------------------------
with gr.Blocks(title="AI Gaming News Agent") as app:

    gr.Markdown("# 🎮 AI Gaming News Agent")
    gr.Markdown("Choose a game and let AI create a kid-friendly gaming report.")

    # Hidden timer. It only runs when Start Auto Update turns it on.
    auto_timer = gr.Timer(value=600, active=False)

    game_dropdown = gr.Dropdown(
        choices=list(GAMES.keys()),
        value="Minecraft",
        label="Choose a Game"
    )

    with gr.Row():
        generate_button = gr.Button("Generate Report", variant="primary")
        discord_button = gr.Button("Generate & Send to Discord")

    report_output = gr.Textbox(
        label="Gaming Report",
        lines=15
    )

    gr.Markdown("## 🔄 Auto Update")

    update_minutes = gr.Number(
        value=10,
        label="Update every X minutes",
        precision=0
    )

    auto_send_discord = gr.Checkbox(
        label="Automatically send each update to Discord",
        value=False
    )

    with gr.Row():
        start_auto_button = gr.Button("Start Auto Update", variant="primary")
        stop_auto_button = gr.Button("Stop Auto Update", variant="stop")

    generate_button.click(
        fn=create_report,
        inputs=game_dropdown,
        outputs=report_output
    )

    discord_button.click(
        fn=generate_and_send_to_discord,
        inputs=game_dropdown,
        outputs=report_output
    )

    # This runs every X minutes after the timer starts.
    auto_timer.tick(
        fn=auto_update_report,
        inputs=[game_dropdown, auto_send_discord],
        outputs=report_output
    )

    # Start the timer.
    start_auto_button.click(
        fn=start_auto_update,
        inputs=update_minutes,
        outputs=auto_timer
    )

    # Also generate one report immediately when auto update starts.
    start_auto_button.click(
        fn=auto_update_report,
        inputs=[game_dropdown, auto_send_discord],
        outputs=report_output
    )

    # Stop the timer.
    stop_auto_button.click(
        fn=stop_auto_update,
        outputs=auto_timer
    )


# -----------------------------------
# START APP
# -----------------------------------
if __name__ == "__main__":
    app.launch()