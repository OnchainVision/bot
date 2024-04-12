import os

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from constants.responses import RESPONSE_HELP_MAIN

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    
    message_text = update.message.text

    # Check if the bot is tagged in the message
    if context.bot.username in message_text or update.message.chat.type == 'private':
        TIP_BOT_URL = os.getenv('TIP_BOT_URL')
        SUPPORT_DISCORD_URL = os.getenv('SUPPORT_DISCORD_URL')
        SUPPORT_TELEGRAM_URL = os.getenv('SUPPORT_TELEGRAM_URL')
        DEPOSIT_WITHOUT_WALLET_URL = os.getenv('DEPOSIT_WITHOUT_WALLET_URL')
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Support Discord", url=SUPPORT_DISCORD_URL)], 
                                             [InlineKeyboardButton("Support Telegram", url=SUPPORT_TELEGRAM_URL)], 
                                             [InlineKeyboardButton("Deposit Website", url=DEPOSIT_WITHOUT_WALLET_URL)]])
        await update.message.reply_html(RESPONSE_HELP_MAIN.format(urlbot=TIP_BOT_URL), reply_markup=reply_markup)
    