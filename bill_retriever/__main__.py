import requests
from settings import settings

# Earliest Congress that works is 82 (1952)

session = requests.Session()
session.params = {
    "format": settings.url_param_format,
    "offset": settings.url_param_offset,
    "limit": settings.url_param_limit,
}
session.headers.update({"x-api-key": settings.api_key})

data = session.get(f"https://api.congress.gov/v3/bill/{settings.url_param_congress}")
print(data.json())
