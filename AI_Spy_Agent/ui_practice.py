import gradio as gr


GAMES = ["Minecraft", "Fortnite", "Roblox", "Nintendo", "Steam"]


def create_report(game):
   return f"""🎮 {game} Gaming Report


🕹️ Game Updates:
• Example update 1
• Example update 2
• Example update 3


🤖 AI Report:
This is where the AI-generated report will appear.
"""


def generate_and_send_to_discord(game):
   report = create_report(game)
   return report


def auto_update_report(game, auto_send_discord):
   report = create_report(game)


   if auto_send_discord:
       print("This would send the report to Discord.")


   return report


with gr.Blocks(title="AI Gaming News Agent") as app:


   gr.Markdown("# 🎮 AI Gaming News Agent")
   gr.Markdown("Choose a game and let AI create a kid-friendly gaming report.")


   game_dropdown = gr.Dropdown(
       choices=GAMES,
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


if __name__ == "__main__":
   app.launch()
