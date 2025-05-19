from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (ApplicationBuilder, CommandHandler, ContextTypes,
                          ConversationHandler, MessageHandler, filters)

from config import TELEGRAM_BOT_TOKEN

BOT_TOKEN = TELEGRAM_BOT_TOKEN

(
    ASK_NAME,
    ASK_AGE,
    ASK_CITY,
    ASK_GENDER,
    ASK_LOOKING_GENDER,
    ASK_LOOKING_AGE_MIN,
    ASK_LOOKING_AGE_MAX,
    ASK_DESCRIPTION,
    ASK_PHOTO,
) = range(9)


GENDER_OPTIONS = [["Male", "Female"]]
LOOKING_FOR_OPTIONS = [["Male", "Female", "Doesn't matter"]]

user_data = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! Let's find your soulmate! What's your name?")
    return ASK_NAME


async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id] = {}
    user_data[user_id]["name"] = update.message.text
    await update.message.reply_text("How old are you?")
    return ASK_AGE


async def ask_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        age = int(update.message.text)
        if age < 18:
            await update.message.reply_text("You must be at least 18 years old.")
            return ASK_AGE
        if age > 120:
            await update.message.reply_text("Enter your real age.")
            return ASK_AGE
        user_data[user_id]["age"] = age
        await update.message.reply_text("What city are you in?")
        return ASK_CITY

    except ValueError:
        await update.message.reply_text("Please input only numbers.")


async def ask_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id]["city"] = update.message.text

    reply_markup = ReplyKeyboardMarkup(
        GENDER_OPTIONS, one_time_keyboard=True, resize_keyboard=True
    )

    await update.message.reply_text(
        "Please, specify your gender:", reply_markup=reply_markup
    )
    return ASK_GENDER


async def ask_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    selected_gender = update.message.text

    if selected_gender not in ["Male", "Female"]:
        reply_markup = ReplyKeyboardMarkup(
            GENDER_OPTIONS, one_time_keyboard=True, resize_keyboard=True
        )
        await update.message.reply_text(
            "Please select your gender using the buttons provided:",
            reply_markup=reply_markup
        )
        return ASK_GENDER
    user_data[user_id]["gender"] = selected_gender

    reply_markup = ReplyKeyboardMarkup(
        LOOKING_FOR_OPTIONS, one_time_keyboard=True, resize_keyboard=True
    )

    await update.message.reply_text(
        "What gender could your soulmate be?", reply_markup=reply_markup
    )
    return ASK_LOOKING_GENDER


async def ask_looking_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    selected_gender = update.message.text

    if selected_gender not in ["Male", "Female", "Doesn't matter"]:
        reply_markup = ReplyKeyboardMarkup(
            LOOKING_FOR_OPTIONS, one_time_keyboard=True, resize_keyboard=True
        )
        await update.message.reply_text(
            "Please select your preferences using the button:",
            reply_markup=reply_markup,
        )
        return ASK_LOOKING_GENDER
    user_data[user_id]["looking_gender"] = selected_gender

    await update.message.reply_text(
        "What is the minimum age of your potential soulmate.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ASK_LOOKING_AGE_MIN


async def ask_looking_age_min(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        min_age = int(update.message.text)
        if min_age < 18:
            await update.message.reply_text("Minimum age must be at least 18.")
            return ASK_LOOKING_AGE_MIN
        if min_age > 99:
            await update.message.reply_text("Please enter a realistic minimum age.")
            return ASK_LOOKING_AGE_MIN
        user_data[user_id]["looking_age_min"] = min_age
        await update.message.reply_text(
            "Great! And what is the maximum age you're looking for?"
        )
        return ASK_LOOKING_AGE_MAX

    except ValueError:
        await update.message.reply_text("Please input only numbers.")
        return ASK_LOOKING_AGE_MIN


async def ask_looking_age_max(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    min_age = user_data[user_id]["looking_age_min"]
    try:
        max_age = int(update.message.text)
        if max_age <= min_age:
            await update.message.reply_text(
                f"Maximum age must be greater than your minimum of {min_age}."
            )
            return ASK_LOOKING_AGE_MAX
        if max_age > 120:
            await update.message.reply_text("Please enter a realistic maximum age.")
            return ASK_LOOKING_AGE_MAX
        user_data[user_id]["looking_age_max"] = max_age
        await update.message.reply_text(
            "We're almost done! Write a few words about yourself and what you're looking for here."
        )
        return ASK_DESCRIPTION

    except ValueError:
        await update.message.reply_text("Please input only numbers.")
        return ASK_LOOKING_AGE_MAX


async def ask_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id]["description"] = update.message.text
    await update.message.reply_text("Nice! Last step — could you send a photo of yourself?")
    return ASK_PHOTO


async def ask_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if update.message.photo:
        user_data[user_id]["photo"] = update.message.photo[-1].file_id
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
            ASK_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_city)],
            ASK_GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_gender)],
            ASK_LOOKING_GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_looking_gender)],
            ASK_LOOKING_AGE_MIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_looking_age_min)],
            ASK_LOOKING_AGE_MAX: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_looking_age_max)],
            ASK_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_description)],
            ASK_PHOTO: [MessageHandler(filters.ALL & ~filters.COMMAND, ask_photo)],
        },
        fallbacks=[],
    )

    app.add_handler(conv_handler)
    app.run_polling()


if __name__ == "__main__":
    main()
