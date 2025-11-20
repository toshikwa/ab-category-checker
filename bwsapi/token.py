import json
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import requests

from .models import BwsApiCredentials, TokenCache, TokenResponse

_token_cache: Optional[TokenCache] = None
TOKEN_EXPIRY_BUFFER_SECONDS = 300


def get_bws_api_credentials() -> BwsApiCredentials:
    # Lambda
    if os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        response = requests.get(
            url=f"http://localhost:2773/secretsmanager/get?secretId={os.environ['BWS_API_SECRET_ID']}",
            headers={"X-Aws-Parameters-Secrets-Token": os.environ["AWS_SESSION_TOKEN"]},
        )
        secret_string = json.loads(response.text)["SecretString"]
        credentials = json.loads(secret_string)
    # Local
    else:
        credentials = {
            "client_id": os.environ["BWS_API_CLIENT_ID"],
            "client_secret": os.environ["BWS_API_CLIENT_SECRET"],
            "refresh_token": os.environ["BWS_API_REFRESH_TOKEN"],
        }
    return BwsApiCredentials(**credentials)


def generate_access_token(bws_api_credentials: BwsApiCredentials) -> TokenResponse:
    response = requests.post(
        url="https://api.amazon.com/auth/O2/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "refresh_token",
            "refresh_token": bws_api_credentials.refresh_token,
            "client_id": bws_api_credentials.client_id,
            "client_secret": bws_api_credentials.client_secret,
        },
        verify=True,
    )
    response.raise_for_status()
    response_json = response.json()
    return TokenResponse(**response_json)


def get_cached_access_token() -> str:
    global _token_cache
    now = datetime.now(timezone.utc)

    # Check if cached token is valid
    if _token_cache and _token_cache.expires_at > now:
        return _token_cache.access_token

    # Fetch LWA credentials from Secrets Manager or environment variables
    credentials = get_bws_api_credentials()

    # Fetch new token from API
    token_response = generate_access_token(credentials)

    # Cache token with some buffer before expiring
    _token_cache = TokenCache(
        access_token=token_response.access_token,
        expires_at=now + timedelta(seconds=token_response.expires_in - TOKEN_EXPIRY_BUFFER_SECONDS),
        refresh_token=credentials.refresh_token,
    )
    return token_response.access_token
