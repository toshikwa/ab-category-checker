from datetime import datetime, timezone
from typing import Optional

import requests

from .models import RefinementResult
from .token import get_cached_access_token


def get_refinements(user_email: str, category: Optional[str] = None) -> RefinementResult:
    api_host = "jp.business-api.amazon.com"
    params = {
        "productRegion": "JP",
        "locale": "ja_JP",
        "keywords": "",
        "pageSize": 24,
        "category": category,
    }
    res = requests.get(
        url=f"https://{api_host}/products/2020-08-26/products",
        params=params,
        headers={
            "host": api_host,
            "x-amz-user-email": user_email,
            "x-amz-access-token": get_cached_access_token(),
            "x-amz-date": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        },
    )
    res.raise_for_status()
    response_data = res.json()
    return RefinementResult(**response_data.get("refinements", {}))
