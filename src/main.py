from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters
from dotenv import load_dotenv
import os

load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

ASK_NAME = 0
ASK_AGE = 1
ASK_SEX = 2
ASK_LOOKING_FOR = 3
ASK_CITY = 4
ASK_DESCRIPTION = 5
ASK_PHOTO = 6

GENDER_OPTIONS = [["Male", "Female"]]
LOOKING_FOR_OPTIONS = [["Male", "Female", "Doesn't matter"]]

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! I'm Soulmate Bot. Let's create your profile.")
    return ASK_NAME

async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id] = {}
    user_data[user_id]['name'] = update.message.text
    await update.message.reply_text("How old are you?")
    return ASK_AGE

async def ask_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id]['age'] = update.message.text

    reply_markup = ReplyKeyboardMarkup(
        GENDER_OPTIONS,
        one_time_keyboard=True,
        resize_keyboard=True
    )

    await update.message.reply_text(
        "Please, specify your gender:",
        reply_markup=reply_markup
    )
    return ASK_SEX

async def ask_sex(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id]['sex'] = update.message.text

    reply_markup = ReplyKeyboardMarkup(
        LOOKING_FOR_OPTIONS,
        one_time_keyboard=True,
        resize_keyboard=True
    )

    await update.message.reply_text(
        "Who are you looking for?",
        reply_markup=reply_markup
    )
    return ASK_LOOKING_FOR

async def ask_looking_for(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id]['looking_for'] = update.message.text
    await update.message.reply_text("What city are you in?")
    return ASK_CITY

async def ask_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id]['city'] = update.message.text
    await update.message.reply_text("Tell something about yourself and what you're looking for:")
    return ASK_DESCRIPTION

async def ask_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id]['description'] = update.message.text
    await update.message.reply_text("Now, please send a photo of yourself.")
    return ASK_PHOTO

async def ask_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if update.message.photo:
        user_data[user_id]['photo'] = update.message.photo[-1].file_id
        await update.message.reply_text("Thanks! Your profile is complete.")
    else:
        await update.message.reply_text("Please send a photo.")
        return ASK_PHOTO

    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)],
            ASK_AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_age)],
            ASK_SEX: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_sex)],
            ASK_LOOKING_FOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_looking_for)],
            ASK_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_city)],
            ASK_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_description)],
            ASK_PHOTO: [MessageHandler(filters.PHOTO, ask_photo)],
        },
        fallbacks=[],
    )

    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()