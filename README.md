# fastlogin

A small authentication library for Python applications using Pydantic and MongoDB.

## Install

Install `fastlogin` from PyPI:

```bash
pip install fastlogin
```

## Quickstart

Define a Pydantic schema for your user data. Use `json_schema_extra.fastlogin` to tell `fastlogin` which fields are used for authentication.

```python
from pydantic import BaseModel, Field


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
```

Initialize `FastLogin` and configure the authentication operation:

```python
from fastlogin import FastLogin
from fastlogin.core.config import OperationType


async def setup():
    auth = FastLogin(
        database_url="mongodb://localhost:27017",
        database_name="fastlogin",
    )

    await auth.initialize()

    await auth.configure(
        operation=OperationType.REGISTER,
        collection="users",
        schema=UserRegistrationSchema,
    )
```

After configuration, `fastlogin` knows:

* `username` and `email` are identifier fields.
* `email` must be unique.
* `password` is the password field.
* `full_name` is a normal user field.

## Configuration

`OperationType` supports the following operations:

```python
from fastlogin.core.config import OperationType

OperationType.REGISTER
OperationType.LOGIN
OperationType.LOGOUT
OperationType.REFRESH
```

Configure each operation with its corresponding Pydantic schema and MongoDB collection:

```python
await auth.configure(
    operation=OperationType.REGISTER,
    collection="users",
    schema=UserRegistrationSchema,
)
```

## License

MIT
