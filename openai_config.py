"""
OpenAI API Configuration
This file loads environment variables from .env or provides defaults
"""

import os
from dotenv import load_dotenv

# Try to load .env file if it exists
load_dotenv()

# OpenAI/Azure OpenAI Configuration
OPENAI_API_TYPE = os.getenv("OPENAI_API_TYPE", "azure")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "24046116ca6b413e8c8ba19e25c7f44d")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://mx250220204441as.openai.azure.com/")
OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION", "2025-01-01-preview")
OPENAI_DEPLOYMENT_NAME = os.getenv("OPENAI_DEPLOYMENT_NAME", "gpt-4o-mlops-hpc")

# Full URL for the deployment endpoint
OPENAI_API_ENDPOINT = f"{OPENAI_API_BASE}openai/deployments/{OPENAI_DEPLOYMENT_NAME}/chat/completions?api-version={OPENAI_API_VERSION}"

def get_openai_api_key():
    """Get the OpenAI API key, checking environment variables first"""
    return OPENAI_API_KEY 