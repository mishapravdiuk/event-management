from typing import Optional

from ninja import Schema
from pydantic import BaseModel, EmailStr, Field, SecretStr


class PasswordRecoveryRequestSchema(Schema):
    email: EmailStr = Field(
        title="User email",
        description="Validated string",
    )


class AuthSchema(PasswordRecoveryRequestSchema):
    password: SecretStr = Field(title="User password", description="Secret string")


class RegisterUserIn(Schema):
    first_name: str
    last_name: str
    email: str
    phone_number: Optional[str]
    password: str
    confirm_password: str


class AccountSchema(BaseModel):
    id: int = Field(..., description="User ID")
    email: EmailStr = Field(..., description="User email")
    phone: Optional[str] = Field(description="User phone")
    first_name: str = Field(
        ...,
        description="Firstname",
    )
    last_name: str = Field(
        ...,
        description="Lastname",
    )

    def to_dict(self):
        return self.dict()


class AccountResponseSchema(Schema):
    id: int = Field(..., description="")
    username: str = Field("", description="")
    email: EmailStr = Field(..., description="")

    def to_dict(self):
        return self.dict()
