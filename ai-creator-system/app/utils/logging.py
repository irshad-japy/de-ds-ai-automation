from loguru import logger
import os


os.makedirs("logs", exist_ok=True)
logger.add("logs/app.log", rotation="1 MB", retention="7 days")