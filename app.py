from config import botToken, userId
from scheduler import startScheduler
from handlers import button, textHandler, sendCountdownMessage
from telegram.ext import Updater, CallbackQueryHandler, MessageHandler, Filters, CommandHandler

_sharedUserData = {}

def main():
    try:
        print("Initializing bot...")
        updater = Updater(token=botToken, use_context=True)
        dp = updater.dispatcher
        updater.dispatcher.user_data[userId] = _sharedUserData
        def startCmd(update, context):
            if update.effective_user.id == userId:
                sendCountdownMessage(context.bot)
        dp.add_handler(CommandHandler("start", startCmd))
        dp.add_handler(CallbackQueryHandler(button))
        dp.add_handler(MessageHandler(Filters.text & Filters.user(user_id=userId), textHandler))
        print("Starting scheduler...")
        startScheduler(updater.bot, _sharedUserData)
        print("Starting polling...")
        updater.start_polling()
        print("Bot is running...")
        updater.idle()
    except Exception as e:
        print(f"Error: {e}")
        raise

if __name__ == "__main__":
    main()