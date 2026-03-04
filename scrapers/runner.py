import asyncio
import logging
from scrapers.bookmakers.onexbet import OneXBetScraper
from scrapers.bookmakers.parimatch import ParimatchScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ScraperRunner")

async def run_scrapers():
    """
    Example runner that executes multiple bookmaker scrapers.
    """
    scrapers = [
        OneXBetScraper(headless=True),
        ParimatchScraper(headless=True)
    ]
    
    logger.info(f"Initialized {len(scrapers)} scrapers for the Indian market.")
    
    for scraper in scrapers:
        async with scraper:
            try:
                odds = await scraper.fetch_live_odds()
                logger.info(f"Successfully fetched {len(odds)} matches from {scraper.bookmaker_name}")
                for match in odds:
                    logger.info(f" - {match.get('home_team')} vs {match.get('away_team')} | Odds: {match.get('odds')}")
            except Exception as e:
                logger.error(f"Error running scraper {scraper.bookmaker_name}: {str(e)}")

if __name__ == "__main__":
    try:
        asyncio.run(run_scrapers())
    except KeyboardInterrupt:
        logger.info("Scraper runner stopped by user.")
