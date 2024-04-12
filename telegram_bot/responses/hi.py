
import random

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes



# Define the start function
async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message_text = update.message.text

    if context.bot.username in message_text or update.message.chat.type == 'private':
        # Check if the bot is tagged in the message or the message is in a private chat
        """Send a message when the command /start is issued."""
        good_morning_messages = [
            "Greetings!",
            "Howdy!",
            "Good day to you!"
        ]
        
        # List of good night GIF URLs (replace with your own URLs)
        gif_urls = [
            "assets/gif/hi.gif",
            "assets/gif/hi2.gif",
            "assets/gif/hi3.gif",
        ]
        
        # Randomly select a good night message
        selected_message = random.choice(good_morning_messages)

        # Randomly select a GIF URL
        selected_gif_path = random.choice(gif_urls)

        file = open(selected_gif_path, 'rb')

        user = update.effective_user

        if len(context.args) == 1 and context.args[0][0] == '@':
            await update.message.reply_animation(
                animation=file,
                caption=f"{selected_message} @{user.username} says to @{context.args[0][1:]}",
            )
        else:
            await update.message.reply_animation(
                animation=file,
                caption=f"{selected_message} @{user.username}",
            )


# Define the start function
async def good_morning(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message_text = update.message.text
    # Check if the bot is tagged in the message or the message is in a private chat
    if context.bot.username in message_text or update.message.chat.type == 'private':
        """Send a message when the command /start is issued."""
        good_morning_messages = [
            "Top of the morning to you!",
            "Good morning, sunshine!",
            "Rise and shine, world!"
        ]
        
        # List of good night GIF URLs (replace with your own URLs)
        gif_urls = [
            "assets/gif/gm.gif",
            "assets/gif/gm2.gif",
            "assets/gif/gm3.gif",
        ]
        
        # Randomly select a good night message
        selected_message = random.choice(good_morning_messages)

        # Randomly select a GIF URL
        selected_gif_path = random.choice(gif_urls)

        file = open(selected_gif_path, 'rb')

        user = update.effective_user
        if len(context.args) == 1 and context.args[0][0] == '@':
            await update.message.reply_animation(
                animation=file,
                caption=f"{selected_message} @{user.username} gm to @{context.args[0][1:]}",
            )
        else:
            await update.message.reply_animation(
                animation=file,
                caption=f"{selected_message} @{user.username}",
            )

# Define the start function
async def good_night(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message_text = update.message.text
    # Check if the bot is tagged in the message or the message is in a private chat
    if context.bot.username in message_text or update.message.chat.type == 'private':
        """Send a message when the command /start is issued."""
        good_night_messages = [
            "Sweet dreams!",
            "Sleep tight!",
            "Good night!"
        ]
        
        # List of good night GIF URLs (replace with your own URLs)
        gif_urls = [
            "assets/gif/gm.gif",
            "assets/gif/gm2.gif",
            "assets/gif/gm3.gif",
        ]
        
        # Randomly select a good night message
        selected_message = random.choice(good_night_messages)

        # Randomly select a GIF URL
        selected_gif_path = random.choice(gif_urls)

        file = open(selected_gif_path, 'rb')

        user = update.effective_user
        if len(context.args) == 1 and context.args[0][0] == '@':
            await update.message.reply_animation(
                animation=file,
                caption=f"{selected_message} @{user.username} gn to @{context.args[0][1:]}",
            )
        else:
            await update.message.reply_animation(
                animation=file,
                caption=f"{selected_message} @{user.username}",
            )