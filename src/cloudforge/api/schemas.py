from typing import Literal

from pydantic import BaseModel, Field


class ModelRegistrationRequest(BaseModel):
    """Validate an incoming AI model registration request."""

    # Require a nonempty model name.
    model_name: str = Field(min_length=1, max_length=100)

    # Only allow these approved provider identifiers.
    provider: Literal["bedrock", "vllm"]

    # Require an integer between 1 and 8192.
    max_tokens: int = Field(ge=1, le=8192, strict=True)


class ModelRegistrationResponse(BaseModel):
    """Define the public response contract."""

    message: str
    model_name: str
    provider: Literal["bedrock", "vllm"]
