from fastlogin.config.logging import get_logger
from fastlogin.database.mongo_db import MongoDB

logger = get_logger(__name__)

class FastLogin:
    def __init__(self, database_url: str, database_name: str) -> None:
        self.database_url = database_url
        self.database_name = database_name
        
        self.db = MongoDB(self.database_url, self.database_name)

    async def initialize(self) -> None:
        """Initialize the FastLogin instance by checking the database connection."""

        health_check = await self.db.check_health()

        if not health_check:
            logger.error("Failed to connect to the database.", database_name=self.database_name)
            raise ConnectionError(f"Failed to connect to the database: {self.database_name}")
        logger.info("Successfully connected to the database.", database_name=self.database_name)
