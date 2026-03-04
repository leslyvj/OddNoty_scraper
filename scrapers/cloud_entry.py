import asyncio
import logging
import os
import re
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI
from uvicorn import Config, Server
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv

from scrapers.bookmakers.onexbet import OneXBetScraper
from worker.notifier.telegram import TelegramNotifier

# Load environment
load_dotenv()

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()] # No file logging needed for Cloud (use stdout)
)
logger = logging.getLogger("CloudOddBot")

# --- 1. Health-Check API ---
app = FastAPI()

@app.get("/")
async def health_check():
    """Endpoint for Render's health-check system."""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

# --- 2. Tracking Engine ---
active_tracks = {}

class OddTrackerEngine:
    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.notifier = TelegramNotifier(bot_token, chat_id)
        self.scraper = OneXBetScraper(headless=True)

    async def monitor(self, match_name, team_num, line):
        last_odd = None
        key = (match_name.lower(), team_num, line)
        logger.info(f"Started monitoring: {match_name} | Team {team_num} Over {line}")
        
        while key in active_tracks:
            try:
                timestamp = datetime.now().strftime("%H:%M:%S")
                async with self.scraper:
                    matches = await self.scraper.fetch_live_odds(sport_id=1)
                    match_info = next((m for m in matches if match_name.lower() in f"{m['home_team']} vs {m['away_team']}".lower()), None)
                    
                    if match_info:
                        game_id = match_info['match_id']
                        details = await self.scraper.fetch_game_details(game_id)
                        target_group = 2 if team_num == 1 else 62
                        current_odd = None
                        
                        for group in details.get("GE", []):
                            if group.get("G") == target_group:
                                for market in group.get("E", []):
                                    for event in market:
                                        if event.get("T") in [11, 13] and event.get("P") == line:
                                            current_odd = event.get("C")
                                            break
                                    if current_odd: break
                            if current_odd: break
                        
                        if current_odd and current_odd != last_odd:
                            icon = "🚀" if (last_odd and current_odd > last_odd) else "🎯"
                            await self.notifier.send({
                                "home_team": match_info['home_team'],
                                "away_team": match_info['away_team'],
                                "match_minute": timestamp,
                                "score": match_info['score'],
                                "market": f"Team {team_num} Over {line}",
                                "line": f"Odd: {current_odd}",
                                "rule_name": f"Cloud Tracker {icon}"
                            })
                            last_odd = current_odd
            except Exception as e:
                logger.error(f"Engine Error: {str(e)}")
            await asyncio.sleep(60)

# --- 3. Telegram Bot Handlers ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    pattern = r"(.+?)\s?:\s?track team_([12]) total ([\d\.]+)"
    match = re.search(pattern, text, re.IGNORECASE)
    
    if match:
        match_name = match.group(1).strip()
        team_num = int(match.group(2))
        line = float(match.group(3))
        key = (match_name.lower(), team_num, line)
        
        if key in active_tracks:
            await update.message.reply_text("⚠️ Already tracking.")
            return

        await update.message.reply_text(f"✅ Cloud Monitor Active: {match_name} (Team {team_num} Over {line}).")
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        engine = OddTrackerEngine(bot_token, chat_id)
        active_tracks[key] = asyncio.create_task(engine.monitor(match_name, team_num, line))
    else:
        await update.message.reply_text("Format: Match : track team_2 total 1.5")


# --- 4. Main Entry Point (Parallel FastAPI & Bot) ---
async def main():
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    port = int(os.getenv("PORT", 10000)) # Render default port
    
    # Start Bot
    bot_app = ApplicationBuilder().token(bot_token).build()
    bot_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    # Start FastAPI
    config = Config(app=app, host="0.0.0.0", port=port, log_level="info")
    server = Server(config)

    logger.info(f"🤖 Starting Cloud OddBot on port {port}...")
    
    # Run both simultaneously
    await asyncio.gather(
        bot_app.initialize(),
        bot_app.start_polling(),
        server.serve()
    )

if __name__ == "__main__":
    asyncio.run(main())
