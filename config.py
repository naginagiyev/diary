import os
from dotenv import load_dotenv

load_dotenv()

userId = int(os.getenv("AUTHENTICATED_USER"))
connectionString = os.getenv("CONNECTION_STRING")
botToken = os.getenv("BOT_TOKEN")

stateIdle, stateWaitingProductivity, stateWaitingNotes = 0, 1, 2