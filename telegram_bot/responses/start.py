
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from db.transactions import record_welcome_bonus_by_t_username

from db.users import setup_user, set_command_by_t_username
from constants.globals import (
    WALLET_BUTTON,
    WITHDRAW_BUTTON,
    USER_HELP_BUTTON,
    USER_BALANCE_BUTTON,
    USER_HISTORY_BUTTON,
    USER_NEW_USER_ADDED,
    DEFAULT_WELCOME_BACK_MESSAGE,
    DEFAULT_WELCOME_MESSAGE
)



# Define the start function 
# If the user is new, add the user to the database and send a welcome message
# If the user is not new, send a welcome back message
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    message_text = update.message.text
    
    if context.bot.username in message_text or update.message.chat.type == 'private':
        result = setup_user(t_first_name=user.first_name, 
                            t_last_name=user.last_name, 
                            t_username=user.username, 
                            t_id_telegram=user.id, 
                            t_is_bot=user.is_bot, 
                            d_username='')
        if result == USER_NEW_USER_ADDED:
            message_text = DEFAULT_WELCOME_MESSAGE.format(user=user.username)
            record_welcome_bonus_by_t_username(user.username)
        else:
            message_text = DEFAULT_WELCOME_BACK_MESSAGE.format(user=user.username)

        # Create a simple keyboard
        if update.message.chat.type == 'private':
            keyboard = [[WALLET_BUTTON, WITHDRAW_BUTTON ], [USER_HELP_BUTTON, USER_BALANCE_BUTTON, USER_HISTORY_BUTTON]]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        else:
            reply_markup = None

        # Update the command state
        previous_state = '/start'
        set_command_by_t_username(user.username, previous_state)

        # Send the message with the keyboard
        await update.message.reply_html(message_text, reply_markup=reply_markup)

