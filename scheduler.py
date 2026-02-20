import time
import schedule
import threading
from datetime import datetime
from handlers import dailyCheck

def runScheduler():
    while True:
        schedule.run_pending()
        time.sleep(10)

def startScheduler(bot, userData):
    def scheduledJob():
        now = datetime.utcnow()
        print(f"Running daily check at {now.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        dailyCheck(bot, userData)

    schedule.every().day.at("21:00").do(scheduledJob)

    schedulerThread = threading.Thread(target=runScheduler, daemon=True)
    schedulerThread.start()