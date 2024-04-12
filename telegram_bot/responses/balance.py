
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from db.balances import get_balance_by_t_username
from db.wallets import get_all_wallets_by_t_username
from blockchain.tip_contract import get_tip_balance
from blockchain.wallet import get_balance
from utils.convert import is_int, convert_to_int, human_format
from constants.responses import RESPONSE_BALANCE_MAIN, RESPONSE_BALANCE_MAIN_ONCHAIN, RESPONSE_BALANCE_MAIN_ONCHAIN_WALLET
from utils.convert import human_format


# Define the balance command
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Check the balance of the user."""
    message_text = update.message.text

    # Check if the bot is tagged in the message or the message is in a private chat
    if context.bot.username in message_text or update.message.chat.type == 'private':
        user = update.message.from_user
        balance = get_balance_by_t_username(user.username)
        wallets = get_all_wallets_by_t_username(user.username)
        if wallets == []:
            await update.message.reply_text(RESPONSE_BALANCE_MAIN.format(balance=human_format(balance)))
        else:
            main_balance =  RESPONSE_BALANCE_MAIN.format(balance=human_format(balance)) + RESPONSE_BALANCE_MAIN_ONCHAIN
            for wallet in wallets:
                balance_tip = get_tip_balance(wallet['address'])
                balance_wallet = get_balance(wallet['address'])
                main_balance += RESPONSE_BALANCE_MAIN_ONCHAIN_WALLET.format(wallet=wallet['name'], balance=human_format(balance_wallet), balance_tip=human_format(balance_tip))
            await update.message.reply_text(main_balance)