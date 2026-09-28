from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from pydantic import BaseModel

from fastlogin.config.logging import get_logger

if TYPE_CHECKING:
    from fastlogin.core.auth import FastLogin
from fastlogin.core.config import OperationType

logger = get_logger(__name__)

async def register_user(payload: BaseModel, auth: FastLogin) -> None:
    """Register a new user in the database."""

    # Check if the register operation is configured
    if OperationType.REGISTER not in auth.configurations:
        logger.error("Register operation is not configured.")
        raise ValueError("Register operation is not configured. Please configure it before calling register.")

    # Get the configuration for the register operation
    config = auth.configurations[OperationType.REGISTER]

    # Validate the payload against the schema
    if not isinstance(payload, config.database_schema):
        logger.error("Payload does not match the configured schema.", payload=payload, schema=config.database_schema.__name__)
        raise TypeError(f"Payload does not match the configured schema: {config.database_schema.__name__}")

    # Check if the user already exists based on the identifier fields
    identifier_query = {field: getattr(payload, field) for field in config.identifier_fields}
    existing_user = await config.collection.find_one(identifier_query)
    if existing_user:
        logger.error("User already exists.", identifier_query=identifier_query)
        raise ValueError("User already exists with the provided identifier(s).")

    # Create a new user document from the payload
    user_document = payload.model_dump() 

    # create database document
    database_data = {}
    for field_name in config.database_schema.model_fields:
        if field_name in user_document:
            database_data[field_name] = getattr(payload, field_name)

    # Add self managed fields to the database document
    now = datetime.now(timezone.utc)
    database_data["created_at"] = now
    database_data["updated_at"] = now

    # Insert the new user document into the collection
    result = await config.collection.insert_one(database_data)
    if not result.acknowledged:
        logger.error("Failed to insert the new user document.", user_document=user_document)
        raise RuntimeError("Failed to register the new user. Please try again.") 

    logger.info("User registered successfully.", user_id=str(result.inserted_id), identifier_query=identifier_query)