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

class Event(str, Enum):
    EMAIL_VERIFIED = "email_verified"
    USER_REGISTERED = "user_registered"


@dataclass
class OperationConfig:
    operation: OperationType
    collection: AsyncIOMotorCollection
    database_schema: type[BaseModel]
    request_schema: type[BaseModel]
    identifier_fields: list[str] = field(default_factory=list)
    password_field: str | None = None

    indexed_fields: list[str] = field(default_factory=list)
    unique_fields: list[str] = field(default_factory=list)

@dataclass
class UpdateRule:
    event: Event
    collection: str
    match_fields: dict[str, str]
    set_fields: dict[str, any] | None = None
    unset_fields: list[str] | None = None