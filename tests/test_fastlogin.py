
import os

import pytest
from dotenv import load_dotenv

from fastlogin import FastLogin  # type: ignore

load_dotenv(".env.test")

@pytest.mark.asyncio
async def test_fastlogin_database_connection():

    database_url=os.getenv("database_url"),
    database_name=os.getenv("database_name"),

    auth = FastLogin(
        database_url=database_url,
        database_name=database_name,
    )

    await auth.initialize()