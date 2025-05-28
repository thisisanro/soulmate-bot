from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (ApplicationBuilder, CommandHandler, ContextTypes,
                          ConversationHandler, MessageHandler, filters)

from config import TELEGRAM_BOT_TOKEN
from db import Database

BOT_TOKEN = TELEGRAM_BOT_TOKEN

# States
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
    COMPLETE_REG,
    BROWSING,
    MAIN_MENU_STATE,
    INACTIVE_MENU_STATE,
) = range(13)

#Buttons
GENDER_OPTIONS = [["Male", "Female"]]
LOOKING_FOR_OPTIONS = [["Male", "Female", "Doesn't matter"]]
CANCEL_REGISTRATION = [["Cancel"]]
START = [["Start"]]
CONFIRM_REGISTRATION = [["Start searching", "Edit profile"]]
BROWSING_OPTIONS = [["❤️ Like", "❌ Skip", "⚙️ Menu"]]
MAIN_MENU = [["Continue searching", "Edit profile", "Deactivate account"]]
CONTINUE_SEARCHING = [["Continue searching"]]
INACTIVE_MENU = [["Activate account", "Edit profile"]]

db = Database()
user_data = {}
current_profiles = {}

# Registration
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if db.user_exists(user_id):
        user_profile = db.get_user(user_id)
        if user_profile["is_active"]:
            return await show_main_menu(update, context)
        else:
            return await show_inactive_menu(update, context)
        
    reply_markup = ReplyKeyboardMarkup(CANCEL_REGISTRATION, resize_keyboard=True)
    await update.message.reply_text(
        "Hi! Let's find your soulmate! What's your name?", reply_markup=reply_markup
    )
    return ASK_NAME


async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    name = update.message.text

    if name == "Cancel":
        return await cancel(update, context)

    user_data[user_id] = {}
    user_data[user_id]["name"] = update.message.text
    reply_markup = ReplyKeyboardMarkup(CANCEL_REGISTRATION, resize_keyboard=True)
    await update.message.reply_text("How old are you?", reply_markup=reply_markup)
    return ASK_AGE


async def ask_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if update.message.text == "Cancel":
        return await cancel(update, context)

    try:
        age = int(update.message.text)
        if age < 18:
            await update.message.reply_text("You must be at least 18 years old.")
            return ASK_AGE
        if age > 120:
            await update.message.reply_text("Enter your real age.")
            return ASK_AGE
        user_data[user_id]["age"] = age
        reply_markup = ReplyKeyboardMarkup(CANCEL_REGISTRATION, resize_keyboard=True)
        await update.message.reply_text(
            "What city are you in?", reply_markup=reply_markup
        )
        return ASK_CITY

    except ValueError:
        await update.message.reply_text("Please input only numbers.")
        return ASK_AGE


async def ask_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if update.message.text == "Cancel":
        return await cancel(update, context)

    user_data[user_id]["city"] = update.message.text

    gender_with_cancel = GENDER_OPTIONS.copy()
    gender_with_cancel.append(["Cancel"])
    reply_markup = ReplyKeyboardMarkup(
        gender_with_cancel, one_time_keyboard=True, resize_keyboard=True
    )

    await update.message.reply_text(
        "Please, specify your gender:", reply_markup=reply_markup
    )
    return ASK_GENDER


async def ask_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    selected_gender = update.message.text

    if update.message.text == "Cancel":
        return await cancel(update, context)

    if selected_gender not in ["Male", "Female"]:
        gender_with_cancel = GENDER_OPTIONS.copy()
        gender_with_cancel.append(["Cancel"])
        reply_markup = ReplyKeyboardMarkup(
            gender_with_cancel, one_time_keyboard=True, resize_keyboard=True
        )
        await update.message.reply_text(
            "Please select your gender using the buttons provided:",
            reply_markup=reply_markup,
        )
        return ASK_GENDER
    user_data[user_id]["gender"] = selected_gender

    looking_with_cancel = LOOKING_FOR_OPTIONS.copy()
    looking_with_cancel.append(["Cancel"])
    reply_markup = ReplyKeyboardMarkup(
        looking_with_cancel, one_time_keyboard=True, resize_keyboard=True
    )

    await update.message.reply_text(
        "What gender could your soulmate be?", reply_markup=reply_markup
    )
    return ASK_LOOKING_GENDER


async def ask_looking_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    selected_gender = update.message.text

    if update.message.text == "Cancel":
        return await cancel(update, context)

    if selected_gender not in ["Male", "Female", "Doesn't matter"]:
        looking_with_cancel = LOOKING_FOR_OPTIONS.copy()
        looking_with_cancel.append(["Cancel"])
        reply_markup = ReplyKeyboardMarkup(
            looking_with_cancel, one_time_keyboard=True, resize_keyboard=True
        )
        await update.message.reply_text(
            "Please select your preferences using the button:",
            reply_markup=reply_markup,
        )
        return ASK_LOOKING_GENDER
    user_data[user_id]["looking_gender"] = selected_gender

    reply_markup = ReplyKeyboardMarkup(
        CANCEL_REGISTRATION, one_time_keyboard=True, resize_keyboard=True
    )
    await update.message.reply_text(
        "What is the minimum age of your potential soulmate.",
        reply_markup=reply_markup,
    )
    return ASK_LOOKING_AGE_MIN


async def ask_looking_age_min(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if update.message.text == "Cancel":
        return await cancel(update, context)

    try:
        min_age = int(update.message.text)
        if min_age < 18:
            await update.message.reply_text("Minimum age must be at least 18.")
            return ASK_LOOKING_AGE_MIN
        if min_age > 99:
            await update.message.reply_text("Please enter a realistic minimum age.")
            return ASK_LOOKING_AGE_MIN
        user_data[user_id]["looking_age_min"] = min_age

        reply_markup = ReplyKeyboardMarkup(CANCEL_REGISTRATION, resize_keyboard=True)

        await update.message.reply_text(
            "Great! And what is the maximum age you're looking for?",
            reply_markup=reply_markup,
        )
        return ASK_LOOKING_AGE_MAX

    except ValueError:
        await update.message.reply_text("Please input only numbers.")
        return ASK_LOOKING_AGE_MIN


async def ask_looking_age_max(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if update.message.text == "Cancel":
        return await cancel(update, context)

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

        reply_markup = ReplyKeyboardMarkup(CANCEL_REGISTRATION, resize_keyboard=True)
        await update.message.reply_text(
            "We're almost done! Write a few words about yourself and what you're looking for here.",
            reply_markup=reply_markup,
        )
        return ASK_DESCRIPTION

    except ValueError:
        await update.message.reply_text("Please input only numbers.")
        return ASK_LOOKING_AGE_MAX


async def ask_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if update.message.text == "Cancel":
        return await cancel(update, context)

    user_data[user_id]["description"] = update.message.text
    reply_markup = ReplyKeyboardMarkup(CANCEL_REGISTRATION, resize_keyboard=True)
    await update.message.reply_text(
        "Nice! Last step — could you send a photo of yourself?",
        reply_markup=reply_markup,
    )
    return ASK_PHOTO


async def ask_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if update.message.text and update.message.text == "Cancel":
        return await cancel(update, context)

    if update.message.photo:
        user_data[user_id]["photo"] = update.message.photo[-1].file_id
        return await check_profile(update, context)
    else:
        await update.message.reply_text("Please send a photo.")
        return ASK_PHOTO


async def check_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    profile = user_data[user_id]

    if "photo" in profile:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id, photo=profile["photo"]
        )

    looking_age = f"{profile['looking_age_min']} - {profile['looking_age_max']}"
    profile_text = (
        f"Name: {profile['name']}\n"
        f"Age: {profile['age']}\n"
        f"City: {profile['city']}\n"
        f"Gender: {profile['gender']}\n"
        f"Looking for: {profile['looking_gender']}\n"
        f"Age range: {looking_age}\n"
        f"About: {profile['description']}\n\n"
        f"Now you can start your searching or if you want to edit something restart registration"
    )

    reply_markup = ReplyKeyboardMarkup(
        CONFIRM_REGISTRATION, one_time_keyboard=True, resize_keyboard=True
    )
    await update.message.reply_text(profile_text, reply_markup=reply_markup)
    return COMPLETE_REG


async def complete_reg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    choice = update.message.text

    if choice == "Start searching":
        user_data[user_id]["user_id"] = user_id
        db.save_user(user_data[user_id])
        db.activate_user(user_id)
        await update.message.reply_text(
            "Your profile is now active. Good luck finding your soulmate!",
        )
        return await start_browsing(update, context)

    elif choice == "Edit profile":
        return await start(update, context)

    else:
        reply_markup = ReplyKeyboardMarkup(
            CONFIRM_REGISTRATION, one_time_keyboard=True, resize_keyboard=True
        )
        await update.message.reply_text(
            "Please use the buttons provided", reply_markup=reply_markup
        )
        return COMPLETE_REG


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id in user_data:
        user_data[user_id] = {}

    reply_markup = ReplyKeyboardMarkup(START, resize_keyboard=True)

    await update.message.reply_text(
        "Registration cancelled. All information has been discarded.\n"
        "You can start a new registration with the Start button or /start command.",
        reply_markup=reply_markup,
    )

    return ConversationHandler.END


async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await start(update, context)


#Browsing
async def start_browsing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    potential_matches = db.find_potential_matches(user_id, 1)

    if not potential_matches:
        reply_markup = ReplyKeyboardMarkup([["⚙️ Menu", "🔄 Reset search"]], resize_keyboard=True)
        await update.message.reply_text(
            "No more profiles to show! You can reset your search to see profiles again, or go to menu.",
            reply_markup=reply_markup
        )
        return BROWSING
    
    potential_match = potential_matches[0]
    current_profiles[user_id] = potential_match

    await show_profile(update, context, potential_match)
    return BROWSING


async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE, profile, matched=False):
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=profile["photo"]
    )

    profile_text = (
        f"{profile["name"]}, {profile["age"]}\n"
        f"{profile["city"]}\n"
        f"{profile["description"]}"
    )

    reply_markup = ReplyKeyboardMarkup(
        CONTINUE_SEARCHING if matched else BROWSING_OPTIONS,
        resize_keyboard=True
    )
    await update.message.reply_text(profile_text, reply_markup=reply_markup)


async def handle_browsing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    choice = update.message.text

    if choice == "Continue searching":
        return await start_browsing(update, context)
    
    elif choice == "⚙️ Menu":
        return await show_main_menu(update, context)
    
    elif choice == "🔄 Reset search":
        db.reset_viewed_profiles(user_id)
        await update.message.reply_text("Search reset! You'll see all profiles again.")
        return await start_browsing(update, context)
    
    elif choice in ["❤️ Like", "❌ Skip"]:
        if user_id not in current_profiles:
            return await start_browsing(update, context)
        
        viewed_profile = current_profiles[user_id]
        db.add_viewed_profile(user_id, viewed_profile["user_id"])

        if choice == "❤️ Like":
            is_match = db.add_like(user_id, viewed_profile["user_id"])

            if is_match:
                matched_chat = await context.bot.get_chat(viewed_profile["user_id"])
                matched_username = matched_chat.username or "No username"
                matched_user = db.get_user(viewed_profile["user_id"])

                await show_profile(update, context, matched_user, True)
                await update.message.reply_text(
                    f"🎉 It's a match with {viewed_profile['name']} (@{matched_username})!"
                    f"You can now start chatting!"
                )
            else:
                await update.message.reply_text("👍")

        elif choice == "❌ Skip":
            await update.message.reply_text("❌")
        
        return await start_browsing(update, context)
    
    else:
        reply_markup = ReplyKeyboardMarkup(BROWSING_OPTIONS, resize_keyboard=True)
        await update.message.reply_text(
            "Please use the buttons provided.", reply_markup=reply_markup
        )
        return BROWSING


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_profile = db.get_user(user_id)

    if not user_profile:
        return await start(update, context)
    
    reply_markup = ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True)
    await update.message.reply_text(
        "Please use buttons provided.",
        reply_markup=reply_markup
    )
    return MAIN_MENU_STATE


async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    choice = update.message.text

    if choice == "Continue searching":
        return await start_browsing(update, context)
    
    elif choice == "Edit profile":
        db.deactivate_user(user_id)
        if user_id in user_data:
            del user_data[user_id]
        
        user_data[user_id] = {}

        reply_markup = ReplyKeyboardMarkup(CANCEL_REGISTRATION, resize_keyboard=True)
        await update.message.reply_text(
            "Let's update your profile! What's you name?",
            reply_markup=reply_markup
        )

        return ASK_NAME
    
    elif choice == "Deactivate account":
        db.deactivate_user(user_id)
        await update.message.reply_text(
            "Your account has been deactivated. Your profile won't be shown to others."
        )
        return await show_inactive_menu(update, context)
    
    else:
        reply_markup = ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True)
        await update.message.reply_text(
            "Please use buttons provided.", reply_markup=reply_markup
        )
        return MAIN_MENU_STATE


async def show_inactive_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_pofile = db.get_user(user_id)

    if not user_pofile:
        return await start(update, context)
    
    reply_markup = ReplyKeyboardMarkup(INACTIVE_MENU, resize_keyboard=True)
    await update.message.reply_text("Please use buttons provided.", reply_markup=reply_markup)
    return INACTIVE_MENU_STATE
    
    
async def handle_inactive_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    choice = update.message.text

    if choice == "Activate account":
        db.activate_user(user_id)
        await update.message.reply_text(
            "🎉 Welcome back! Your profile is now visible to others again."
        )
        return await show_main_menu(update, context)
    
    elif choice == "Edit profile":
        db.deactivate_user(user_id)
        if user_id in user_data:
            del user_data[user_id]
        
        user_data[user_id] = {}

        reply_markup = ReplyKeyboardMarkup(CANCEL_REGISTRATION, resize_keyboard=True)
        await update.message.reply_text(
            "Let's update your profile! What's you name?",
            reply_markup=reply_markup
        )

        return ASK_NAME
    
    else:
        reply_markup = ReplyKeyboardMarkup(INACTIVE_MENU, resize_keyboard=True)
        await update.message.reply_text(
            "Please use the buttons provided.", reply_markup=reply_markup
        )
        return INACTIVE_MENU_STATE


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            MessageHandler(filters.Regex("^Start$"), register),
        ],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)],
            ASK_AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_age)],
            ASK_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_city)],
            ASK_GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_gender)],
            ASK_LOOKING_GENDER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, ask_looking_gender)
            ],
            ASK_LOOKING_AGE_MIN: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, ask_looking_age_min)
            ],
            ASK_LOOKING_AGE_MAX: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, ask_looking_age_max)
            ],
            ASK_DESCRIPTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, ask_description)
            ],
            ASK_PHOTO: [MessageHandler(filters.ALL & ~filters.COMMAND, ask_photo)],
            COMPLETE_REG: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, complete_reg)
            ],
            BROWSING: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_browsing)],
            MAIN_MENU_STATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_main_menu)
            ],
            INACTIVE_MENU_STATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_inactive_menu)
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            MessageHandler(filters.Regex("^Cancel$"), cancel),
        ],
    )

    app.add_handler(conv_handler)
    app.run_polling()


if __name__ == "__main__":
    main()
