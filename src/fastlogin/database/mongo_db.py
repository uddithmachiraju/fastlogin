from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from fastlogin.config.logging import get_logger
from fastlogin.database.base_db import Database

logger = get_logger(__name__) 

class MongoDB(Database):
    def __init__(self, database_url: str, database_name: str):
        self.database_url = database_url
        self.database_name = database_name

        self.client: AsyncIOMotorClient = AsyncIOMotorClient(
            self.database_url, 
            appname="FastLogin",
        )

    async def get_database(self) -> AsyncIOMotorDatabase:
        """Get the default database from the MongoDB client."""

        return self.client.get_default_database()

    async def list_collections(self) -> list[str]:
        """List all collections in the database."""

        database = await self.get_database()
        return await database.list_collection_names()

    async def close_db(self) -> None:
        """Close the MongoDB client connection."""

        self.client.close()
        logger.info("MongoDB connection closed.", database_name=self.database_name)

    async def check_health(self) -> bool:
        """Check the health of the MongoDB connection."""

        try:
            await self.client.admin.command("ping")
            logger.info("MongoDB connection is healthy.", database_name=self.database_name)
            return True
        except Exception as e:
            logger.error("MongoDB connection health check failed.", error=str(e), database_name=self.database_name)
            return False