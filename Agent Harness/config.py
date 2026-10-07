import os
from dotenv import load_dotenv

load_dotenv()

# Harness configuration
MAX_STEPS = 10
ACTION_TIMEOUT = 1800000  # 30 mins in ms
MAX_RETRIES = 2

# Safety / Policy configuration
ALLOWED_DOMAINS = [
    "example.com",
    "www.example.com",
    "en.wikipedia.org",
    "github.com",
    "accounts.google.com"
]

# Task Configuration
TARGET_URL = os.getenv("TARGET_URL", "https://github.com")
GOOGLE_ACCOUNT = os.getenv("GOOGLE_ACCOUNT", "")
GITHUB_PASSWORD = os.getenv("GITHUB_PASSWORD", "")

# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "mock")
API_KEY = os.getenv("API_KEY", "")
