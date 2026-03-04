import asyncio
import logging
import httpx
from typing import List, Dict, Any
from scrapers.base import BaseScraper
from scrapers.utils.mirrors import MirrorManager

logger = logging.getLogger(__name__)

class OneXBetScraper(BaseScraper):
    """
    Scraper for 1xBet India.
    Focuses on deep market data using the verified mirror.
    """
    
    def __init__(self, headless: bool = True):
        super().__init__("1xBet", headless)
        self.mirrors = [
            "https://indi-1xbet.com",
            "https://1xbet-sport.in",
            "https://1xbetindia.info",
            "https://1x-india.in",
        ]
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "X-Requested-With": "XMLHttpRequest",
            "x-svc-source": "__BETTING_APP__",
            "Connection": "keep-alive"
        }

    async def start(self):
        logger.info(f"Initialized {self.bookmaker_name} Deep Market Scraper.")
        pass

    async def fetch_live_odds(self, sport_id: int = 1) -> List[Dict[str, Any]]:
        """Fetch general live matches."""
        for mirror in self.mirrors:
            url = f"{mirror}/service-api/LiveFeed/Get1x2_VZip"
            params = {
                "sports": sport_id, "count": 100, "lng": "en", "gr": 413,
                "mode": 4, "country": 71, "partner": 71
            }
            async with httpx.AsyncClient(headers=self.headers, timeout=15.0) as client:
                try:
                    response = await client.get(url, params=params)
                    if response.status_code == 200:
                        data = response.json()
                        return self._parse_general_response(data.get("Value", []))
                except Exception as e:
                    logger.error(f"Mirror {mirror} general fetch failed: {str(e)}")
        return []

    async def fetch_game_details(self, game_id: int) -> Dict[str, Any]:
        """
        Fetches ALL markets for a specific game (GetGameZip).
        This includes Individual Totals, Corners, Cards etc.
        """
        for mirror in self.mirrors:
            url = f"{mirror}/service-api/LiveFeed/GetGameZip"
            params = {
                "id": game_id,
                "lng": "en",
                "isSubGames": "true",
                "GroupEvents": "true",
                "countevents": 500,
                "grMode": 4,
                "partner": 71,
                "country": 71
            }
            async with httpx.AsyncClient(headers=self.headers, timeout=15.0) as client:
                try:
                    response = await client.get(url, params=params)
                    if response.status_code == 200:
                        return response.json().get("Value", {})
                except Exception as e:
                    logger.error(f"Mirror {mirror} game detail fetch failed: {str(e)}")
        return {}

    def _parse_general_response(self, raw_matches: List[Dict]) -> List[Dict[str, Any]]:
        parsed = []
        for item in raw_matches:
            parsed.append({
                "match_id": item.get("I"),
                "home_team": item.get("O1"),
                "away_team": item.get("O2"),
                "league": item.get("LE"),
                "score": f"{item.get('SC', {}).get('FS', {}).get('S1', 0)}-{item.get('SC', {}).get('FS', {}).get('S2', 0)}",
                "odds": {"1": self._find_coef(item.get("E", []), 1)} # Just 1x2 for quick find
            })
        return parsed

    def _find_coef(self, events: List[Dict], event_id: int) -> float:
        for e in events:
            if e.get("T") == event_id:
                return e.get("C")
        return 0.0

    async def stop(self):
        pass
