import asyncio
import logging
from scrapers.bookmakers.onexbet import OneXBetScraper

# Configure logging to show exact details
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("1xBetTest")

async def test_live_odds():
    """
    Directly tests 1xBet scraper to fetch live football match odds.
    """
    scraper = OneXBetScraper(headless=True)
    
    print("\n--- 1xBet Live Odds Test ---")
    print(f"Targeting Soccer (Sport ID: 1)")
    
    async with scraper:
        try:
            # You can change sport_id to verify other sports (e.g., Cricket: 5, Tennis: 4)
            logger.info("Starting live odds fetch...")
            matches = await scraper.fetch_live_odds(sport_id=1) 
            
            if not matches:
                print("\n❌ No live football matches found or all mirrors are blocked.")
                print("Try running the script again in a few minutes or double-check the mirrors.")
            else:
                print(f"\n✅ Found {len(matches)} live matches on 1xBet:\n")
                for m in matches[:10]: # Show first 10
                    print(f"Match: {m['home_team']} vs {m['away_team']}")
                    print(f"League: {m['league']}")
                    print(f"Score: {m['score']}")
                    print(f"Odds (1/X/2): {m['odds']['1']} / {m['odds']['X']} / {m['odds']['2']}")
                    print("-" * 30)
                    
        except Exception as e:
            logger.error(f"Test failed with error: {str(e)}")

if __name__ == "__main__":
    try:
        asyncio.run(test_live_odds())
    except KeyboardInterrupt:
        pass
