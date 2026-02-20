from db import saveRecord
from utils import parseProductivity
from datetime import datetime, timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import userId, stateIdle, stateWaitingProductivity, stateWaitingNotes

state = stateIdle

def getNextCheckDelta():
    now = datetime.utcnow()
    nextRun = now.replace(hour=21, minute=0, second=0, microsecond=0)
    if now >= nextRun:
        nextRun += timedelta(days=1)
    delta = nextRun - now
    totalSeconds = int(delta.total_seconds())
    hours = totalSeconds // 3600
    minutes = (totalSeconds % 3600) // 60
    seconds = totalSeconds % 60
    return hours, minutes, seconds

def sendCountdownMessage(bot):
    h, m, s = getNextCheckDelta()
    text = f"⏳ _Növbəti yoxlamaya {h:02d} saat {m:02d} dəqiqə {s:02d} saniyə qalıb!_"
    bot.send_message(chat_id=userId, parse_mode="Markdown", text=text)

def dailyCheck(bot, contextUserData):
    contextUserData["created_at"] = datetime.utcnow()
    keyboard = [
        [
            InlineKeyboardButton(" 😭 ", callback_data="0"),
            InlineKeyboardButton(" 😢 ", callback_data="15"),
            InlineKeyboardButton(" 😞 ", callback_data="30"),
            InlineKeyboardButton(" 😐 ", callback_data="50"),
            InlineKeyboardButton(" 🙂 ", callback_data="70"),
            InlineKeyboardButton(" 😊 ", callback_data="85"),
            InlineKeyboardButton(" 😁 ", callback_data="100"),
        ]
    ]
    bot.send_message(
        chat_id=userId,
        text="_☀️ How was your day today?_",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

def button(update, context):
    global state
    query = update.callback_query
    query.answer()
    context.user_data["pending_mood"] = int(query.data)
    state = stateWaitingProductivity
    query.message.delete()
    msg = context.bot.send_message(
        chat_id=userId,
        text="_⚡ How productive was your day?_",
        parse_mode="Markdown",
    )
    context.user_data["productivity_question_msg_id"] = msg.message_id

def productivityHandler(update, context):
    global state
    if state != stateWaitingProductivity:
        return
    state = stateWaitingNotes
    productivity = parseProductivity(update.message.text)
    context.user_data["pending_productivity"] = productivity
    productivityQId = context.user_data.pop("productivity_question_msg_id", None)
    if productivityQId:
        context.bot.delete_message(chat_id=userId, message_id=productivityQId)
    update.message.delete()
    msg = context.bot.send_message(
        chat_id=userId,
        text="_🗒️ Any notes?_",
        parse_mode="Markdown",
    )
    context.user_data["notes_question_msg_id"] = msg.message_id

def notesHandler(update, context):
    global state
    if state != stateWaitingNotes:
        return
    state = stateIdle
    mood = context.user_data.pop("pending_mood", None)
    productivity = context.user_data.pop("pending_productivity", None)
    createdAt = context.user_data.pop("created_at", None)
    if mood is None or createdAt is None:
        update.message.reply_text(
            "_Something went wrong. Please wait for the next daily check._",
            parse_mode="Markdown",
        )
        return
    text = update.message.text.strip()
    note = None if len(text) <= 1 else text
    respondedAt = datetime.utcnow()
    saveRecord(
        createdAt=createdAt,
        respondedAt=respondedAt,
        happinessScore=mood,
        productivityScore=productivity,
        notes=note,
    )
    notesQId = context.user_data.pop("notes_question_msg_id", None)
    if notesQId:
        context.bot.delete_message(chat_id=userId, message_id=notesQId)
    update.message.delete()
    bakuTime = respondedAt + timedelta(hours=1)
    formattedDate = bakuTime.strftime("%d.%m.%Y in %H:%M")
    escapedDate = formattedDate.replace(".", r"\.").replace(":", r"\:")
    context.bot.send_message(
        chat_id=userId,
        text=f"_💾 Record saved for ***{escapedDate}***_",
        parse_mode="MarkdownV2",
    )

def textHandler(update, context):
    global state
    if state == stateWaitingProductivity:
        productivityHandler(update, context)
    elif state == stateWaitingNotes:
        notesHandler(update, context)