
import os

import pytest
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from fastlogin import FastLogin  # type: ignore
from fastlogin.core.config import OperationType  # type: ignore

load_dotenv(".env.test")

# Test the configure method with valid inputs
class UserRegistrationSchema(BaseModel):
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
    password: str = Field(
        ..., description="The password of the user.",
        json_schema_extra={
            "fastlogin": {
                "role": "password",
            }
        }
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

    await auth.configure(operation=OperationType.REGISTER, collection="users", schema=UserRegistrationSchema)
    print(auth.configurations)