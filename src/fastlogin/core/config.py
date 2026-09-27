from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from motor.motor_asyncio import AsyncIOMotorCollection
from pydantic import BaseModel


class OperationType(str, Enum):
    REGISTER = "register"
    LOGIN = "login"
    LOGOUT = "logout"
    REFRESH = "refresh"


@dataclass
class OperationConfig:
    operation: OperationType
    schema: type[BaseModel]
    collection: AsyncIOMotorCollection
    identifier_fields: list[str] = field(default_factory=list)
    password_field: str | None = None

    indexed_fields: list[str] = field(default_factory=list)
    unique_fields: list[str] = field(default_factory=list)