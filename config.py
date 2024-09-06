import os

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ.get("TOKEN")
API_URL = os.environ.get("API_URL")
REDIS_URI = os.environ.get("REDIS_URI")
