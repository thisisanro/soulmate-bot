# Soulmate

A Telegram bot to help people find each other for hanging out, hobbies and collaboration.

## Features

- Registration form
- Matchmaking based on user preferences
- Like/Skip browsing interface
- Mutual match detection
- Main menu with options to edit or deactivate account
- SQLite database for storing user profiles and likes

## How it works

1. User starts with `/start` and completes the registration
2. After confirmation, the bot shows matching profiles
3. If both users like each other, it's a match 🎉 (Users get each other’s contact info to start a conversation)
4. Users can edit their profile or deactivate their account anytime

## Tech Stack

- Python
- python-telegram-bot library
- SQLite for local database

## Setup

```bash
# Clone the repo
git clone https://github.com/thisisanro/soulmate-bot.git

# Install dependencies
pip install -r requirements.txt

# Run the bot
python main.py