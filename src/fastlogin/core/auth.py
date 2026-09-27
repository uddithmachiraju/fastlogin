from __future__ import annotations

from pydantic import BaseModel

from fastlogin.config.logging import get_logger
from fastlogin.core.config import OperationConfig, OperationType
from fastlogin.database.mongo_db import MongoDB

logger = get_logger(__name__)

class FastLogin:
    """A class to handle user authentication and registration using a MongoDB database."""

    def __init__(self, database_url: str, database_name: str) -> None:
        self.database_url = database_url
        self.database_name = database_name
        
        self.db = MongoDB(self.database_url, self.database_name)

        self.configurations: dict[OperationType, OperationConfig] = {}

    async def configure(self, operation: OperationType, collection: str, schema: type[BaseModel]) -> None:
        """Configure the database collection and schema with user data."""

        if not isinstance(operation, OperationType):
            logger.error("Invalid operation type provided.", operation=operation)
            raise TypeError(f"Invalid operation type: {operation}. Must be one of {list(OperationType)}.")

        if operation in self.configurations:
            logger.error("Operation already configured.", operation=operation.value)
            raise ValueError(f"Operation {operation.value} is already configured.")

        if not collection or not collection.strip():
            logger.error("Collection name cannot be empty.", collection=collection)
            raise ValueError("Collection name cannot be empty.")

        if not isinstance(schema, type) or not issubclass(schema, BaseModel):
            logger.error("Schema must be a subclass of pydantic.BaseModel.", schema=schema)
            raise TypeError("Schema must be a subclass of pydantic.BaseModel.")

        # Get the database instance
        database = await self.db.get_database()

        if database is None:
            logger.error("Failed to get the database instance.", database_name=self.database_name)
            raise ConnectionError(f"Failed to get the database instance: {self.database_name}")  

        # check if the collection exists, if not create it
        if collection not in await self.db.list_collections():
            await database.create_collection(collection)
            logger.info("Collection created.", collection=collection, database_name=self.database_name)
        else:
            logger.info("Collection already exists.", collection=collection, database_name=self.database_name)      

        # Set the collection and schema
        self.collection = database[collection]

        # Inspect the schema
        identifier_fields: list[str] = []
        password_field: str | None = None
        indexed_fields: list[str] = []
        unique_fields: list[str] = []

        for field_name, field in schema.model_fields.items():

            extra = field.json_schema_extra

            if not isinstance(extra, dict):
                continue

            fastlogin_config = extra.get("fastlogin", {})

            if not isinstance(fastlogin_config, dict):
                continue

            role = fastlogin_config.get("role")

            if role == "identifier":
                identifier_fields.append(field_name)
            elif role == "password":
                if password_field is not None:
                    logger.error("Multiple password fields defined in schema.", schema=schema.__name__)
                    raise ValueError(f"Multiple password fields defined in schema: {schema.__name__}")
                password_field = field_name

            if fastlogin_config.get("index") is True:
                indexed_fields.append(field_name)

            if fastlogin_config.get("unique") is True:
                unique_fields.append(field_name)

        if operation in {OperationType.REGISTER, OperationType.LOGIN} and not identifier_fields:
            logger.error("At least one identifier field must be defined in the schema to perform registration or login.", schema=schema.__name__, operation=operation.value)
            raise ValueError(f"At least one identifier field must be defined in the schema to perform registration or login: {schema.__name__}")

        if operation in {OperationType.REGISTER, OperationType.LOGIN} and password_field is None:
            logger.error("A password field must be defined in the schema to perform registration or login.", schema=schema.__name__, operation=operation.value)
            raise ValueError(f"A password field must be defined in the schema to perform registration or login: {schema.__name__}")

        # Index the unique fields in the collection
        for field_name in unique_fields:
            if field_name not in indexed_fields:
                indexed_fields.append(field_name)

        # create indexes for the indexed fields
        for field_name in indexed_fields:
            await self.collection.create_index(field_name)
            logger.info("Index created for field.", field=field_name, collection=collection, database_name=self.database_name)

        # store the configuration
        self.configurations[operation] = OperationConfig(
            operation=operation,
            schema=schema,
            collection=self.collection,
            identifier_fields=identifier_fields,
            password_field=password_field,
            indexed_fields=indexed_fields,
            unique_fields=unique_fields,
        )
        
        logger.info("Collection and schema configured.", collection=collection, schema=schema.__name__, database_name=self.database_name)

    async def initialize(self) -> None:
        """Initialize the FastLogin instance by checking the database connection."""

        health_check = await self.db.check_health()

        if not health_check:
            logger.error("Failed to connect to the database.", database_name=self.database_name)
            raise ConnectionError(f"Failed to connect to the database: {self.database_name}")
        logger.info("Successfully connected to the database.", database_name=self.database_name)

    async def register(self) -> None:
        """Register a new user in the database."""
