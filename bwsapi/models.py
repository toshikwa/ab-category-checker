from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class BwsApiCredentials(BaseModel):
    client_id: str = Field(...)
    client_secret: str = Field(...)
    refresh_token: str = Field(...)


class TokenResponse(BaseModel):
    access_token: str = Field(...)
    token_type: str = Field(...)
    expires_in: int = Field(...)
    refresh_token: str = Field(...)


class TokenCache(BaseModel):
    access_token: str = Field(...)
    expires_at: datetime = Field(...)
    refresh_token: str = Field(...)


class RefinementItem(BaseModel):
    display_name: str = Field(..., alias="displayName")
    id: str = Field(...)


class RefinementResult(BaseModel):
    categories: List[RefinementItem] = Field(default_factory=list)
    sub_categories: List[RefinementItem] = Field(default_factory=list, alias="subCategories")
