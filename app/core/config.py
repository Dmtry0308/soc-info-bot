import os
from dotenv import load_dotenv

load_dotenv()

MATTERMOST_URL = os.getenv("MATTERMOST_URL")
MATTERMOST_TOKEN = os.getenv("MATTERMOST_TOKEN")
MATTERMOST_BOT_USERNAME = os.getenv("MATTERMOST_BOT_USERNAME")
VT_API_KEY = os.getenv("VT_API_KEY")
VT_PROXY = os.getenv("VT_PROXY")
