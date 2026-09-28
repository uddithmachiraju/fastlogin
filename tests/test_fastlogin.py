
import os

import pytest
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from fastlogin import FastLogin  # type: ignore
from fastlogin.core.config import Event, OperationType  # type: ignore

load_dotenv(".env.test")

# Test the configure method with valid inputs
class UserRegistrationDatabaseSchema(BaseModel):
    username: str = Field(
        ..., description="The username of the user.", 
        json_schema_extra={
            "fastlogin": {
                "role": "identifier",
            }
        }
    )
    full_name: str = Field(
        ..., description="The full name of the user.",
    )
    email: str = Field(
        ..., description="The email address of the user.",
        json_schema_extra={
            "fastlogin": {
                "role": "identifier",
                "unique": True,
            }
        }
    )
    hashed_password: str = Field(
        ..., description="The hashed password of the user.",
        json_schema_extra={
            "fastlogin": {
                "role": "password",
            }
        }
    )
    is_active: bool = Field(
        ..., description="Indicates whether the user is active.",
        json_schema_extra={
            "fastlogin": {
                "auto_managed": True
            }
        }
    )
    is_email_verified: bool = Field(
        ..., description="Indicates whether the user's email is verified.",
        json_schema_extra={
            "fastlogin": {
                "auto_managed": True
            }
        }
    )

class UserRegistrationRequestSchema(BaseModel):
    username: str = Field(
        ..., description="The username of the user.",
    )
    full_name: str = Field(
        ..., description="The full name of the user.",
    )
    email: str = Field(
        ..., description="The email address of the user.",
    )
    password: str = Field(
        ..., description="The password of the user.",
    )


@pytest.mark.asyncio
async def test_fastlogin_database_connection():

    database_url=os.getenv("database_url"),
    database_name=os.getenv("database_name"),

    auth = FastLogin(
        database_url=database_url,
        database_name=database_name,
    )

    await auth.initialize()


@pytest.mark.asyncio
async def test_fastlogin_configure_with_valid_inputs():
    database_url=os.getenv("database_url"),
    database_name=os.getenv("database_name"),

    auth = FastLogin(
        database_url=database_url,
        database_name=database_name,
    )

    await auth.configure_collection(operation=OperationType.REGISTER, collection="users", schema=UserRegistrationDatabaseSchema)
    print(auth.configurations)

@pytest.mark.asyncio
async def test_fastlogin_register_user():
    database_url=os.getenv("database_url"),
    database_name=os.getenv("database_name"),

    auth = FastLogin(
        database_url=database_url,
        database_name=database_name,
    )

    await auth.initialize()
    await auth.configure_collection(operation=OperationType.REGISTER, collection="users", schema=UserRegistrationDatabaseSchema)
    await auth.configure_request(operation=OperationType.REGISTER, schema=UserRegistrationRequestSchema)
    await auth.add_update_rule(
        event=Event.EMAIL_VERIFIED,
        collection="users",
        match_fields={"email": "email"},
        set_fields={
            "is_email_verified": True, 
            "is_active": True    
        }
    )