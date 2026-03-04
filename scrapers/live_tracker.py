import asyncio
import logging
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from scrapers.bookmakers.onexbet import OneXBetScraper
from worker.notifier.telegram import TelegramNotifier

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DeepTracker")

# Config
TARGET_MATCH = "Qarabag vs Shamakhi"
TEAM_2_NAME = "Shamakhi"
MARKET_LINE = 1.5
CHECK_INTERVAL_MINUTES = 5

# Final verified IDs for this mirror
IT2_OVER_TYPE = 13 
IT2_GROUP_ID = 62

async def track_individual_total():
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    notifier = TelegramNotifier(bot_token, chat_id)
    scraper = OneXBetScraper(headless=True)
    
    last_odd = None
    logger.info(f"🚀 Tracking {TARGET_MATCH} | {TEAM_2_NAME} Over {MARKET_LINE}")

    while True:
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            async with scraper:
                matches = await scraper.fetch_live_odds(sport_id=1)
                match_info = next((m for m in matches if TARGET_MATCH.lower() in f"{m['home_team']} vs {m['away_team']}".lower()), None)
                
                if not match_info:
                    logger.warning(f"Match {TARGET_MATCH} not found.")
                else:
                    game_id = match_info['match_id']
                    details = await scraper.fetch_game_details(game_id)
                    
                    it2_over_odd = None
                    
                    # Search logic for the specific mirror's schema (G=62, T=13)
                    for group in details.get("GE", []):
                        if group.get("G") == IT2_GROUP_ID:
                            for market in group.get("E", []):
                                for event in market:
                                    if event.get("T") == IT2_OVER_TYPE and event.get("P") == MARKET_LINE:
                                        it2_over_odd = event.get("C")
                                        break
                                if it2_over_odd: break
                        if it2_over_odd: break

                    # Broad Fallback if Group 62 fails (scan all events for P=1.5 and likely T)
                    if not it2_over_odd:
                        for event in details.get("E", []):
                             # Some skins put IT2 Over in T=11 or T=13
                             if event.get("P") == MARKET_LINE and event.get("T") in [11, 13]:
                                 it2_over_odd = event.get("C")
                                 break

                    if it2_over_odd:
                        if it2_over_odd != last_odd:
                            icon = "📈" if (last_odd and it2_over_odd > last_odd) else "🎯"
                            direction = "rose to" if (last_odd and it2_over_odd > last_odd) else "is currently"
                            
                            alert = {
                                "home_team": match_info['home_team'],
                                "away_team": match_info['away_team'],
                                "match_minute": timestamp,
                                "score": match_info['score'],
                                "market": f"Over {MARKET_LINE} goals for {TEAM_2_NAME}",
                                "line": f"Odd: {it2_over_odd}",
                                "rule_name": f"Market: Individual Total 2 {icon}"
                            }
                            await notifier.send(alert)
                            last_odd = it2_over_odd
                            logger.info(f"✅ ODD UPDATED: {it2_over_odd}")
                    else:
                        logger.warning(f"Market not found yet. Current Score: {match_info['score']}")
        
        except Exception as e:
            logger.error(f"Tracker Error: {str(e)}")
            
        await asyncio.sleep(CHECK_INTERVAL_MINUTES * 60)

if __name__ == "__main__":
    asyncio.run(track_individual_total())
