
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

from steps.command_steps import is_in_steps, get_step, get_arguments, add_step
from utils.convert import is_int, convert_to_int, human_format
from utils.wallet import get_wallet_full_name, get_url_by_tx, get_my_wallet_t, is_address
from utils.qr_image import qrcode_create
from blockchain.wallet import create_wallet, get_address_and_private_key, get_balance, transfer_eth
from blockchain.tip_contract import withdraw_tip_top_up
from blockchain.tx import check_tx_status
from db.transactions import top_up_balance_by_t_username, withdraw_balance_by_t_username
from utils.wallet import get_my_wallet_t
from db.users import set_command_by_t_username, get_command_by_t_username
from db.wallets import get_all_wallets_by_t_username
from db.balances import get_balance_by_t_username
from db.parameters import get_param
from constants.globals import (
    USER_MAIN_MENU_BUTTON,
    WITHDRAW_BUTTON_ON_ADDRESS,
    WITHDRAW_BUTTON_ON_ACCOUNT,
    WALLET_SELECT_BUTTON,
    
)

from constants.responses import (
    RESPONSE_WITHDRAW_SUCCESS,
    RESPONSE_WITHDRAW_FAILED,
    TEXT_INVALID_AMOUNT,
    EXAMPLE_AMOUNT,
    TEXT_INVALID_AMOUNT_ADDRESS,
    EXAMPLE_ADDRESS_AMOUNT,
    WALLET_NOT_FOUND,
    RESPONSE_WITHDRAW_INPUT_AMOUNT_ADDRESS,
    RESPONSE_WITHDRAW_INPUT_AMOUNT,
    RESPONSE_WITHDRAW_MINIMUM,
    RESPONSE_WITHDRAW_OPTIONS,
)


from constants.parameters import PARAMETER_MINIMUM_WITHDRAW_BTT

# Wallet goes to
async def withdraw_btt(update, context):
    user = update.effective_user
    # Check if the command was sent in a private chat
    if update.message.chat.type == 'private':
        balance = get_balance_by_t_username(user.username)
        min_balance = int(get_param(PARAMETER_MINIMUM_WITHDRAW_BTT))

        if balance < min_balance:
            await context.bot.send_message(user.id, RESPONSE_WITHDRAW_MINIMUM.format(amount=human_format(min_balance), balance=human_format(balance)))
        else:
            wallets = get_all_wallets_by_t_username(user.username)
            if wallets == []:
                keyboard = [[WITHDRAW_BUTTON_ON_ADDRESS]]
            else:
                keyboard = [ [WITHDRAW_BUTTON_ON_ADDRESS] ]
                for wallet in wallets:
                    keyboard.append([ WITHDRAW_BUTTON_ON_ACCOUNT + get_wallet_full_name(wallet) ])
            keyboard.append([USER_MAIN_MENU_BUTTON])

            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await context.bot.send_message(user.id, RESPONSE_WITHDRAW_OPTIONS, reply_markup=reply_markup)


async def withdraw_btt_in_wallet(update, context):
    user = update.effective_user
    # Check if the command was sent in a private chat
    if update.message.chat.type == 'private':
        command = get_command_by_t_username(user.username)
        if is_in_steps(command):
            step = get_step(command)
            arguments = get_arguments(command)
            if step == 1:
                withdraw_amount = update.message.text

                if is_int(withdraw_amount) == False:
                    await update.message.reply_text(TEXT_INVALID_AMOUNT.format(text=withdraw_amount) + EXAMPLE_AMOUNT)
                else:
                    wallet_name = arguments[1]
                    my_wallet = get_my_wallet_t(user.username, wallet_name)
                    if my_wallet is not None:
                        withdraw_amount_int = convert_to_int(withdraw_amount)
                        balance = get_balance_by_t_username(user.username)
                        min_balance = int(get_param(PARAMETER_MINIMUM_WITHDRAW_BTT))
                        if balance < min_balance or withdraw_amount_int > balance or withdraw_amount_int < min_balance:
                            reply_markup = ReplyKeyboardMarkup([[USER_MAIN_MENU_BUTTON]], resize_keyboard=True)
                            await context.bot.send_message(user.id, RESPONSE_WITHDRAW_MINIMUM.format(amount=human_format(min_balance), balance=human_format(balance)), reply_markup=reply_markup)
                        else:
                            # Withdraw the amount
                            set_command_by_t_username(user.username, WALLET_SELECT_BUTTON + my_wallet['name'])
                            tx = withdraw_tip_top_up(my_wallet['address'], withdraw_amount_int)
                            url = get_url_by_tx(tx)
                            
                            if check_tx_status(tx) == True:
                                withdraw_balance_by_t_username(tx, user.username, withdraw_amount_int)
                                reply_markup = ReplyKeyboardMarkup([[USER_MAIN_MENU_BUTTON]], resize_keyboard=True)
                                await update.message.reply_html(RESPONSE_WITHDRAW_SUCCESS.format(amount=human_format(withdraw_amount_int), url=url), reply_markup=reply_markup)
                            else:
                                reply_markup = ReplyKeyboardMarkup([[USER_MAIN_MENU_BUTTON]], resize_keyboard=True)
                                await update.message.reply_text(RESPONSE_WITHDRAW_FAILED.format(amount=human_format(withdraw_amount_int), url=url), reply_markup=reply_markup)

        else:
            wallet_name = update.message.text.replace(WITHDRAW_BUTTON_ON_ACCOUNT, "")
            my_wallet = get_my_wallet_t(user.username, wallet_name)
            command = add_step(update.message.text, my_wallet['name'])
            set_command_by_t_username(user.username, command)

            if my_wallet is not None:
                await context.bot.send_message(user.id, RESPONSE_WITHDRAW_INPUT_AMOUNT)
            else:
                await context.bot.send_message(user.id, WALLET_NOT_FOUND.format(wallet=wallet_name))


async def withdraw_btt_in_address(update, context):
    user = update.effective_user
    # Check if the command was sent in a private chat
    if update.message.chat.type == 'private':
        command = get_command_by_t_username(user.username)
        print(f"wallet_deposit: command: {command}")
        if command == WITHDRAW_BUTTON_ON_ADDRESS:
            address = update.message.text.split(" ")[0]
            withdraw_amount = update.message.text.split(" ")[1]

            if is_int(withdraw_amount) == False or is_address(address) == False:
                await update.message.reply_text(TEXT_INVALID_AMOUNT_ADDRESS.format(text=update.message.text) + EXAMPLE_ADDRESS_AMOUNT)
            else:
                withdraw_amount_int = convert_to_int(withdraw_amount)
                balance = get_balance_by_t_username(user.username)
                min_balance = int(get_param(PARAMETER_MINIMUM_WITHDRAW_BTT))
                if balance < min_balance or withdraw_amount_int > balance or withdraw_amount_int < min_balance:
                    reply_markup = ReplyKeyboardMarkup([[USER_MAIN_MENU_BUTTON]], resize_keyboard=True)
                    await context.bot.send_message(user.id, RESPONSE_WITHDRAW_MINIMUM.format(amount=human_format(min_balance), balance=human_format(balance)), reply_markup=reply_markup)
                else:
                    # Withdraw the amount
                    set_command_by_t_username(user.username, USER_MAIN_MENU_BUTTON)
                    tx = withdraw_tip_top_up(address, withdraw_amount_int)
                    url = get_url_by_tx(tx)
   
                    if check_tx_status(tx) == True:
                        withdraw_balance_by_t_username(tx, user.username, withdraw_amount_int)
                        reply_markup = ReplyKeyboardMarkup([[USER_MAIN_MENU_BUTTON]], resize_keyboard=True)
                        await update.message.reply_html(RESPONSE_WITHDRAW_SUCCESS.format(amount=human_format(withdraw_amount_int), url=url), reply_markup=reply_markup)
                    else:
                        reply_markup = ReplyKeyboardMarkup([[USER_MAIN_MENU_BUTTON]], resize_keyboard=True)
                        await update.message.reply_text(RESPONSE_WITHDRAW_FAILED.format(amount=human_format(withdraw_amount_int), url=url), reply_markup=reply_markup)

        else:
            set_command_by_t_username(user.username, WITHDRAW_BUTTON_ON_ADDRESS)
            await context.bot.send_message(user.id, RESPONSE_WITHDRAW_INPUT_AMOUNT_ADDRESS)