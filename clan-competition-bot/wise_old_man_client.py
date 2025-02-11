from logging import Logger
import aiohttp
from constants import WOM_BASE_API_URL, WOM_COMPETITION_ENDPOINT

class WiseOldManClient:
    def __init__(self, logger: Logger):
        self.base_url = WOM_BASE_API_URL
        self.competition_endpoint = WOM_COMPETITION_ENDPOINT
        self.logger = logger

    async def fetch_competition(self, competition_id: int):
        if not competition_id:
            self.logger.error(f"Error fetching competition. No competition ID given")
            return
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/{self.competition_endpoint}/{competition_id}"
                self.logger.info(f"Attempting to grab competition with url {url}")
                async with session.get(url) as response:
                    if response.status == 200:
                        self.logger.info("Success!")
                        self.logger.info(f"{response}")
                        return await response.json()
                    else:
                        raise Exception(f"API request failed with status {response.status}")
        except Exception as e:
            self.logger.critical(f"Error fetching competition {competition_id}: {e}")
