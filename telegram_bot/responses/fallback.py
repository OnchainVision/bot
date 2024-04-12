
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from db.users import get_command_by_t_username, set_command_by_t_username
from .wallet import (
    wallet_options,
    wallet_deposit,
    wallet_topup,
    wallet_withdraw,
    wallet_onchain_transfer,
)
from .wallet_new import (
    wallet_generate_address_response,
    wallet_import_address_response_pk,
    wallet_import_address_response_name

)
from .start import start
from .withdraw import withdraw_btt, withdraw_btt_in_address, withdraw_btt_in_wallet
from constants.globals import (
    USER_MAIN_MENU_BUTTON,
    WALLET_BUTTON,
    WALLET_SELECT_BUTTON,
    WALLET_NEW_BUTTON,
    WALLET_DEPOSIT_BUTTON,
    WALLET_TOPUP_BUTTON,
    WALLET_WITHDRAW_BUTTON,
    WALLET_ONCHAIN_TRANSFER_BUTTON,
    WALLET_GENERATE_BUTTON,
    WALLET_IMPORT_BUTTON,
    WALLET_IMPORT_BUTTON,
    WALLET_PK_PROVIDED,
    DEFAULT_NO_FALLBACK_MESSAGE,
    WITHDRAW_BUTTON_ON_ADDRESS,
    WITHDRAW_BUTTON_ON_ACCOUNT
    
    
)

def extract_message_from_previous_state(previous_state: str, cmd: str) -> str:
    return previous_state.replace(cmd, "")


# Define the fallback handler
async def fallback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle unmatched commands."""
    user = update.effective_user
    command = get_command_by_t_username(user.username)

    # Call the method based on the previous state

    '''
        If the previous state was WALLET_BUTTON it means that the selected text will be the wallet name
        If the previous state was WALLET_SELECT_BUTTON it means that along the way/in the code it was decided to select a wallet
    '''
    
    if update.message.chat.type == 'private':
        print(f"fallback_handler: command: {command}")

        if command.startswith(USER_MAIN_MENU_BUTTON):
            await start(update, context)
        elif command.startswith(WALLET_BUTTON):
            await wallet_options(update, context)
        elif command.startswith(WALLET_SELECT_BUTTON):
            await wallet_options(update, context)
        elif command.startswith(WITHDRAW_BUTTON_ON_ADDRESS):
            await withdraw_btt_in_address(update, context)
        elif command.startswith(WITHDRAW_BUTTON_ON_ACCOUNT):
            await withdraw_btt_in_wallet(update, context)
        elif command.startswith(WALLET_DEPOSIT_BUTTON):
            await wallet_deposit(update, context)
        elif command.startswith(WALLET_TOPUP_BUTTON):
            await wallet_topup(update, context)
        elif command.startswith(WALLET_WITHDRAW_BUTTON):
            await wallet_withdraw(update, context)
        elif command.startswith(WALLET_ONCHAIN_TRANSFER_BUTTON):
            await wallet_onchain_transfer(update, context)
        elif command.startswith(WALLET_GENERATE_BUTTON):
            await wallet_generate_address_response(update, context)
        elif command.startswith(WALLET_IMPORT_BUTTON):
            await wallet_import_address_response_pk(update, context)
        elif command.startswith(WALLET_PK_PROVIDED):
            pk = '0x' + extract_message_from_previous_state(command, WALLET_PK_PROVIDED)
            await wallet_import_address_response_name(update, context, pk)
        else:
            print(f"fallback_handler: command: {command}")
            print(f"fallback_handler: message: {update.message.text}")
            
            set_command_by_t_username(user.username, '/start')
            
            
            reply_markup = ReplyKeyboardMarkup([[USER_MAIN_MENU_BUTTON, WALLET_BUTTON]], resize_keyboard=True)

            await update.message.reply_text("Sorry, I didn't understand that command.", reply_markup=reply_markup)