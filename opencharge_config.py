"""
OpenChargeMap API Configuration

This file contains the API key and configuration settings for OpenChargeMap integration.
"""

# OpenChargeMap API Key - Public for class project use
OPENCHARGE_API_KEY = "b230774d-262e-4207-a003-c8576e82a454"

# API Endpoints
OPENCHARGE_BASE_URL = "https://api.openchargemap.io/v3"
OPENCHARGE_POI_ENDPOINT = f"{OPENCHARGE_BASE_URL}/poi"

# Default query parameters
DEFAULT_PARAMS = {
    "key": OPENCHARGE_API_KEY,
    "maxresults": 500,
    "compact": True,
    "verbose": False,
    "output": "json"
}

# Rate limiting settings
RATE_LIMIT_REQUESTS = 100  # requests per day for free tier
RATE_LIMIT_INTERVAL = 60   # seconds between requests recommended 