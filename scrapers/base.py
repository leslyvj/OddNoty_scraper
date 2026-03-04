import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    """
    Base class for all bookmaker scrapers.
    Defines the interface and common utilities.
    """
    
    def __init__(self, bookmaker_name: str, headless: bool = True):
        self.bookmaker_name = bookmaker_name
        self.headless = headless
        self.browser = None
        self.context = None

    @abstractmethod
    async def start(self):
        """Initialize browser and context."""
        pass

    @abstractmethod
    async def fetch_live_odds(self, league_id: str = None) -> List[Dict[str, Any]]:
        """Fetch live odds for the given league or all available matches."""
        pass

    @abstractmethod
    async def stop(self):
        """Close browser and cleanup."""
        pass

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()
