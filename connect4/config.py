import os
import logging
from dotenv import load_dotenv

load_dotenv('.env')

LOG_LEVEL = os.getenv("LOG_LEVEL")
API_PREFIX = os.getenv('API_PREFIX')
SLACK_WEB_CLIENT_TOKEN = os.getenv("SLACK_WEB_CLIENT_TOKEN")
SLACK_APP_TOKEN = os.getenv('SLACK_APP_TOKEN')

logger = logging

logger.basicConfig(level=LOG_LEVEL, format='%(asctime)s -%(levelname)s - %(message)s',
                   datefmt='%d-%b-%y %H:%M:%S')
