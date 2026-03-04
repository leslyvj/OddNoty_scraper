import asyncio
import logging
import json
from scrapers.bookmakers.onexbet import OneXBetScraper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MarketDebugger")

async def debug_markets():
    scraper = OneXBetScraper(headless=True)
    game_id = 700693088 # Qarabag vs Shamakhi
    
    async with scraper:
        print(f"Fetching deep data for Game ID: {game_id}")
        details = await scraper.fetch_game_details(game_id)
        
        if not details:
            print("Could not fetch details. Check mirror/connection.")
            return

        # Save to a temp file for inspection
        with open("match_data_debug.json", "w") as f:
            json.dump(details, f, indent=2)
        print("Raw data saved to match_data_debug.json")

        # Scan Grouped Events (GE)
        found = False
        for group in details.get("GE", []):
            group_name = group.get("GN", "Unknown")
            # print(f"Checking Group: {group_name} (G={group.get('G')})")
            
            for market in group.get("E", []):
                for event in market:
                    # Let's look for Shamakhi's Over 1.5. 
                    # If odds are around 3.79 (as in user screenshot)
                    odd_val = event.get("C")
                    point = event.get("P")
                    if point == 1.5:
                         print(f"Potential Match: G={group.get('G')}, T={event.get('T')}, Point={point}, Odd={odd_val}, GroupName={group_name}")
                         found = True

        if not found:
            print("No market with Point=1.5 found in GE.")
            # Search in top-level 'E' as well
            for event in details.get("E", []):
                if event.get("P") == 1.5:
                    print(f"Top-level Match: T={event.get('T')}, Point={event.get('P')}, Odd={event.get('C')}")

if __name__ == "__main__":
    asyncio.run(debug_markets())
