
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

from steps.command_steps import is_in_steps, get_step, get_arguments, add_step
from utils.convert import is_int, convert_to_int, human_format
from utils.qr_image import qrcode_create
from utils.wallet import get_wallet_full_name, get_url_by_tx
from blockchain.wallet import get_balance, transfer_eth
from blockchain.tip_contract import get_tip_balance, deposit_tip, withdraw_tip, top_up_tip
from blockchain.tx import check_tx_status
from db.transactions import top_up_balance_by_t_username
from db.wallets import get_all_wallets_by_t_username, add_wallet_by_t_username
from db.users import set_command_by_t_username, get_command_by_t_username
from db.wallets import delete_wallet_name_by_t_username
from db.parameters import get_param
from constants.globals import (
    WALLET_BUTTON,
    WALLET_NEW_BUTTON,
    WALLET_SELECT_BUTTON,
    WALLET_DEPOSIT_BUTTON,
    WALLET_WITHDRAW_BUTTON,
    WALLET_TOPUP_BUTTON,
    WALLET_DELETE_BUTTON,
    WALLET_ONCHAIN_TRANSFER_BUTTON,
    MESSAGE_WALLET_TRANSFER_ON_CHAIN,
    MESSAGE_WALLET_TOP_UP,
    MESSAGE_CHOSE_WALLET,
    MESSAGE_WALLET_NOT_FOUND,
    MESSAGE_WALLET_MENU,
    MESSAGE_WALLET_INSUFFICIENT_FEE,
    MESSAGE_WALLET_INSUFFICIENT_BALANCE,
    MESSAGE_WALLET_DEPOSIT,
    MESSAGE_WALLET_WITHDRAW,
    MESSAGE_WALLET_INSUFFICIENT_TIP,
    USER_MAIN_MENU_BUTTON
)
from constants.responses import (
    TEXT_INVALID_AMOUNT,
    EXAMPLE_AMOUNT,
    RESPONSE_WALLET_TOPUP_SUCCESS,
    RESPONSE_WALLET_DEPOSIT_SUCCESS,
    RESPONSE_WALLET_WITHDRAW_SUCCESS,
    RESPONSE_WALLET_TRANSFER_SUCCESS,
    RESPONSE_WALLET_TOPUP_FAILED,
    RESPONSE_WALLET_DEPOSIT_FAILED,
    RESPONSE_WALLET_WITHDRAW_FAILED,
    RESPONSE_WALLET_TRANSFER_FAILED,
    RESPONSE_WALLET_DELETE_SUCCESS
)

from constants.parameters import PARAMETER_MINIMUM_FEES



#   1.2. Your wallet options (wallet_options) -  Checks on previous command - fallback - WALLET_BUTTON
#     1.2.1. Deposit (wallet_deposit)
#     1.2.2. Withdraw (wallet_withdraw)
#     1.2.3. Delete (wallet_delete)
#     1.2.4. Topup (wallet_topup)
#     1.2.5. Transfer (wallet_onchain_transfer)
#   1.3. Main Menu (wallet_main_menu)

# _response goes to the response of the previous command and usually comes from a fallback command
# The fallback command is used to handle unmatched commands based on the previous state

# Wallet goes to
async def wallet_private(update, context):
    user = update.effective_user
    set_command_by_t_username(user.username, WALLET_BUTTON)
    # Check if the command was sent in a private chat
    if update.message.chat.type == 'private':
        # Now let's send a private message to the user
        # We must select the avaialable wallets for the user and let the user choose one or create a new one
        wallets = get_all_wallets_by_t_username(user.username)
        if wallets == []:
            keyboard = [[WALLET_NEW_BUTTON]]
        else:
            keyboard = [[WALLET_NEW_BUTTON]]
            for wallet in wallets:
                keyboard.append([get_wallet_full_name(wallet)])
        keyboard.append([USER_MAIN_MENU_BUTTON])

        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await context.bot.send_message(user.id, MESSAGE_CHOSE_WALLET, reply_markup=reply_markup)

# Each unique wallet has its own options
async def wallet_options(update, context):
    user = update.effective_user
    command = get_command_by_t_username(user.username)
    set_command_by_t_username(user.username, WALLET_SELECT_BUTTON)
    # Check if the command was sent in a private chat
    if update.message.chat.type == 'private':
        # Get the name of the wallet from the user's response

        wallets = get_all_wallets_by_t_username(user.username)

        if command.startswith(WALLET_SELECT_BUTTON):
            wallet_name = command.replace(WALLET_SELECT_BUTTON, "")
            my_wallet = next((wallet for wallet in wallets if wallet['name'] == wallet_name), None)
        else:
            wallet_name = update.message.text
            my_wallet = next((wallet for wallet in wallets if get_wallet_full_name(wallet) == wallet_name), None)

        if my_wallet is None or wallets == []:
            await update.message.reply_text(MESSAGE_WALLET_NOT_FOUND.format(wallet=wallet_name))
        else:
            # Let's get the balance of the wallet
            balance = get_balance(my_wallet['address'])
            balance_tips = get_tip_balance(my_wallet['address'])
            img = qrcode_create(my_wallet['address'])

            keyboard = [
                [WALLET_DEPOSIT_BUTTON + my_wallet['name'], WALLET_TOPUP_BUTTON + my_wallet['name']],
                [WALLET_WITHDRAW_BUTTON + my_wallet['name'], WALLET_ONCHAIN_TRANSFER_BUTTON + my_wallet['name'], WALLET_DELETE_BUTTON + my_wallet['name']],
                [WALLET_BUTTON]
            ]

            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

            await update.message.reply_photo(photo=img, 
                                             caption= MESSAGE_WALLET_MENU.format(wallet=my_wallet['name'], address=my_wallet['address'], balance=human_format(balance), balance_tips=human_format(balance_tips)),
                                             parse_mode='Markdown',
                                             reply_markup=reply_markup)


async def wallet_deposit(update, context):
    user = update.effective_user
    # Check if the command was sent in a private chat
    if update.message.chat.type == 'private':
        command = get_command_by_t_username(user.username)
        print(f"wallet_deposit: command: {command}")
        wallets = get_all_wallets_by_t_username(user.username)
        if is_in_steps(command):
            step = get_step(command)
            arguments = get_arguments(command)
            if step == 1:
                deposited_amount = update.message.text
                print(f"step: {step}")
                print(f"arguments: {arguments}")
                print(f"deposited_amount: {deposited_amount}")

                # Check if the amount is a valid number or contains digits and b,
                if is_int(deposited_amount) == False:
                    await update.message.reply_text(TEXT_INVALID_AMOUNT.format(text=deposited_amount) + EXAMPLE_AMOUNT)
                else:
                    wallet_name = arguments[0].replace(WALLET_DEPOSIT_BUTTON, "")
                    my_wallet = next((wallet for wallet in wallets if wallet['name'] == wallet_name), None)
                    fee_needed = int(get_param(PARAMETER_MINIMUM_FEES))
                    balance = get_balance(my_wallet['address'])
                    deposited_amount_int = convert_to_int(deposited_amount)
                    if fee_needed + deposited_amount_int > balance:
                        max = balance - fee_needed
                        await update.message.reply_text(MESSAGE_WALLET_INSUFFICIENT_BALANCE.format(balance=human_format(balance), fee=fee_needed, max=max))
                    else:

                        # Deposit the amount to the wallet
                        tx = deposit_tip(deposited_amount_int, my_wallet['address'], my_wallet['pk'])

                        set_command_by_t_username(user.username, WALLET_SELECT_BUTTON + wallet_name)

                        url = get_url_by_tx(tx)
                        reply_markup = ReplyKeyboardMarkup([[get_wallet_full_name(my_wallet)], [USER_MAIN_MENU_BUTTON, WALLET_BUTTON]], resize_keyboard=True)

                        if check_tx_status(tx) == True:
                            await update.message.reply_html(
                                RESPONSE_WALLET_DEPOSIT_SUCCESS.format(amount=deposited_amount_int, url=url),
                                reply_markup=reply_markup)
                        else:
                            await update.message.reply_html(
                                RESPONSE_WALLET_DEPOSIT_FAILED.format(amount=deposited_amount_int, url=url),
                                reply_markup=reply_markup)        
        else:
            command = add_step(update.message.text, "STARTED_DEPOSIT")
            set_command_by_t_username(user.username, command)
            # STEP 0 - Get the wallet name from the user's response
            # Get the name of the wallet from the user's response
            wallet_name = update.message.text.replace(WALLET_DEPOSIT_BUTTON, "")
            
            # We must select the available wallets for the user to check if the wallet name exists
            my_wallet = next((wallet for wallet in wallets if wallet['name'] == wallet_name), None)

            if my_wallet is None or wallets == []:
                await update.message.reply_text(MESSAGE_WALLET_NOT_FOUND.format(wallet=wallet_name))
            else:
                balance = get_balance(my_wallet['address'])
                fee_needed = int(get_param(PARAMETER_MINIMUM_FEES))

                if fee_needed > balance:
                    await update.message.reply_text(MESSAGE_WALLET_INSUFFICIENT_FEE.format(fee=human_format(fee_needed)))
                else:
                    await update.message.reply_text(MESSAGE_WALLET_DEPOSIT)


async def wallet_withdraw(update, context):
    user = update.effective_user
    # Check if the command was sent in a private chat
    if update.message.chat.type == 'private':
        command = get_command_by_t_username(user.username)
        wallets = get_all_wallets_by_t_username(user.username)
        if is_in_steps(command):
            step = get_step(command)
            arguments = get_arguments(command)
            if step == 1:
                withdraw_amount = update.message.text
                print(f"step: {step}")
                print(f"arguments: {arguments}")
                print(f"withdraw_amount: {withdraw_amount}")

                if is_int(withdraw_amount) == False:
                    await update.message.reply_text(TEXT_INVALID_AMOUNT.format(text=withdraw_amount) + EXAMPLE_AMOUNT)
                else:
                    # Your code here to deposit the amount
                    wallet_name = arguments[0].replace(WALLET_WITHDRAW_BUTTON, "")
                    my_wallet = next((wallet for wallet in wallets if wallet['name'] == wallet_name), None)
                    if my_wallet is not None:
                        balance = get_tip_balance(my_wallet['address'])
                        withdraw_amount_int = convert_to_int(withdraw_amount)
                        if withdraw_amount_int > balance:
                            max = balance
                            await update.message.reply_text(MESSAGE_WALLET_INSUFFICIENT_TIP.format(balance=human_format(balance), max=max))
                        else:
                            # Deposit the amount to the wallet
                            tx = withdraw_tip(withdraw_amount_int, my_wallet['address'], my_wallet['pk'])

                            set_command_by_t_username(user.username, WALLET_SELECT_BUTTON + wallet_name)

                            # Add inline link to the transaction
                            url = get_url_by_tx(tx)
                            reply_markup = ReplyKeyboardMarkup([[get_wallet_full_name(my_wallet)], [USER_MAIN_MENU_BUTTON, WALLET_BUTTON]], resize_keyboard=True)

                            if check_tx_status(tx) == True:
                                await update.message.reply_html(
                                    RESPONSE_WALLET_WITHDRAW_SUCCESS.format(amount=human_format(withdraw_amount_int), url=url),
                                    reply_markup=reply_markup)
                            else:
                                await update.message.reply_html(
                                    RESPONSE_WALLET_WITHDRAW_FAILED.format(amount=human_format(withdraw_amount_int), url=url),
                                    reply_markup=reply_markup)
                            
                    else:
                        await update.message.reply_text(f"Wallet not found {wallet_name}. Please select one of the available wallets or create a new one.")
        else:
            command = add_step(update.message.text, "STARTED_WITHDRAW")
            set_command_by_t_username(user.username, command)
            # STEP 0 - Get the wallet name from the user's response
            # Get the name of the wallet from the user's response
            wallet_name = update.message.text.replace(WALLET_WITHDRAW_BUTTON, "")
            
            # We must select the available wallets for the user to check if the wallet name exists
            my_wallet = next((wallet for wallet in wallets if wallet['name'] == wallet_name), None)

            if my_wallet is None or wallets == []:
                await update.message.reply_text(MESSAGE_WALLET_NOT_FOUND.format(wallet=wallet_name))
            else:
                balance = get_balance(my_wallet['address'])
                fee_needed = int(get_param(PARAMETER_MINIMUM_FEES))

                if fee_needed > balance:
                    await update.message.reply_text(MESSAGE_WALLET_INSUFFICIENT_FEE.format(fee=human_format(fee_needed)))
                else:
                    await update.message.reply_text(MESSAGE_WALLET_WITHDRAW)

async def wallet_onchain_transfer(update, context):
    user = update.effective_user
    # Check if the command was sent in a private chat
    if update.message.chat.type == 'private':
        command = get_command_by_t_username(user.username)
        wallets = get_all_wallets_by_t_username(user.username)
        if is_in_steps(command):
            step = get_step(command)
            arguments = get_arguments(command)
            if step == 1:
                address = update.message.text.split(" ")[0]
                amount = update.message.text.split(" ")[1]
                print(f"step: {step}")
                print(f"arguments: {arguments}")
                print(f"address: {address}")
                print(f"amount: {amount}")

                if is_int(amount) == False or len(address) != 42 or address[:2] != "0x":
                    await update.message.reply_text("Please input a valid address and amount to transfer")
                else:
                    wallet_name = arguments[0].replace(WALLET_ONCHAIN_TRANSFER_BUTTON, "")
                    my_wallet = next((wallet for wallet in wallets if wallet['name'] == wallet_name), None)
                    fee_needed = int(get_param(PARAMETER_MINIMUM_FEES))
                    balance = get_balance(my_wallet['address'])
                    amount_int = convert_to_int(amount)
                    if fee_needed + amount_int > balance:
                        max = balance - fee_needed
                        await update.message.reply_text(MESSAGE_WALLET_INSUFFICIENT_BALANCE.format(balance=human_format(balance), fee=human_format(fee_needed), max=human_format(max)))
                    else:
                        # Deposit the amount to the wallet
                        tx = transfer_eth(my_wallet['address'], address, amount_int, my_wallet['pk'])

                        set_command_by_t_username(user.username, WALLET_SELECT_BUTTON + wallet_name)

                        # Add inline link to the transaction
                        url = get_url_by_tx(tx)
                        reply_markup = ReplyKeyboardMarkup([[get_wallet_full_name(my_wallet)], [USER_MAIN_MENU_BUTTON, WALLET_BUTTON]], resize_keyboard=True)

                        if check_tx_status(tx) == True:
                            await update.message.reply_html(
                                RESPONSE_WALLET_TRANSFER_SUCCESS.format(amount=human_format(amount_int), url=url),
                                reply_markup=reply_markup)
                        else:
                            await update.message.reply_html(
                                RESPONSE_WALLET_TRANSFER_FAILED.format(amount=human_format(amount_int), url=url),
                                reply_markup=reply_markup)
                            
        else:
            command = add_step(update.message.text, "STARTED_TRANSFER")
            set_command_by_t_username(user.username, command)
            # STEP 0 - Get the wallet name from the user's response
            # Get the name of the wallet from the user's response
            wallet_name = update.message.text.replace(WALLET_ONCHAIN_TRANSFER_BUTTON, "")
            
            # We must select the available wallets for the user to check if the wallet name exists
            my_wallet = next((wallet for wallet in wallets if wallet['name'] == wallet_name), None)

            if my_wallet is None or wallets == []:
                await update.message.reply_text(MESSAGE_WALLET_NOT_FOUND.format(wallet=wallet_name))
            else:
                balance = get_balance(my_wallet['address'])
                fee_needed = int(get_param(PARAMETER_MINIMUM_FEES))

                if fee_needed > balance:
                    await update.message.reply_text(MESSAGE_WALLET_INSUFFICIENT_FEE.format(fee=human_format(fee_needed)))
                else:
                    await update.message.reply_text(MESSAGE_WALLET_TRANSFER_ON_CHAIN)

async def wallet_topup(update, context):
    user = update.effective_user
    # Check if the command was sent in a private chat
    if update.message.chat.type == 'private':
        command = get_command_by_t_username(user.username)
        wallets = get_all_wallets_by_t_username(user.username)
        if is_in_steps(command):
            step = get_step(command)
            arguments = get_arguments(command)
            if step == 1:
                withdraw_amount = update.message.text
                print(f"step: {step}")
                print(f"arguments: {arguments}")
                print(f"withdraw_amount: {withdraw_amount}")

                if is_int(withdraw_amount) == False:
                    await update.message.reply_text(TEXT_INVALID_AMOUNT.format(text=withdraw_amount) + EXAMPLE_AMOUNT)
                else:
                    wallet_name = arguments[0].replace(WALLET_TOPUP_BUTTON, "")
                    my_wallet = next((wallet for wallet in wallets if wallet['name'] == wallet_name), None)
                    balance = get_tip_balance(my_wallet['address'])
                    withdraw_amount_int = convert_to_int(withdraw_amount)
                    if withdraw_amount_int > balance:
                        max = balance
                        await update.message.reply_text(MESSAGE_WALLET_INSUFFICIENT_TIP.format(balance=human_format(balance), max=human_format(max)))
                    else:
                        # Deposit the amount to the wallet
                        set_command_by_t_username(user.username, WALLET_SELECT_BUTTON + wallet_name)
                        tx = top_up_tip(withdraw_amount_int, my_wallet['address'], my_wallet['pk'])
                        url = get_url_by_tx(tx)
                        reply_markup = ReplyKeyboardMarkup([[get_wallet_full_name(my_wallet)], [USER_MAIN_MENU_BUTTON, WALLET_BUTTON]], resize_keyboard=True)
                        if check_tx_status(tx) == True:
                            top_up_balance_by_t_username(tx, user.username, withdraw_amount_int)
                            await update.message.reply_html(RESPONSE_WALLET_TOPUP_SUCCESS.format(amount=human_format(withdraw_amount_int), url=url), reply_markup=reply_markup)
                        else:
                            await update.message.reply_html(RESPONSE_WALLET_TOPUP_FAILED.format(amount=human_format(withdraw_amount_int), url=url), reply_markup=reply_markup)
        else:
            command = add_step(update.message.text, "STARTED_TRANSFER")
            set_command_by_t_username(user.username, command)
            # STEP 0 - Get the wallet name from the user's response
            # Get the name of the wallet from the user's response
            wallet_name = update.message.text.replace(WALLET_TOPUP_BUTTON, "")

            # We must select the available wallets for the user to check if the wallet name exists
            my_wallet = next((wallet for wallet in wallets if wallet['name'] == wallet_name), None)

            if my_wallet is None or wallets == []:
                await update.message.reply_text(MESSAGE_WALLET_NOT_FOUND.format(wallet=wallet_name))
            else:
                balance = get_balance(my_wallet['address'])
                fee_needed = int(get_param(PARAMETER_MINIMUM_FEES))

                if fee_needed > balance:
                    await update.message.reply_text(MESSAGE_WALLET_INSUFFICIENT_FEE.format(fee=human_format(fee_needed)))
                else:
                    await update.message.reply_text(MESSAGE_WALLET_TOP_UP)


async def wallet_delete(update, context):
    user = update.effective_user
    # Check if the command was sent in a private chat
    if update.message.chat.type == 'private':
        command = get_command_by_t_username(user.username)
        
        wallet_name = update.message.text.replace(WALLET_DELETE_BUTTON, "")
        
        # We must select the available wallets for the user to check if the wallet name exists
        delete_wallet_name_by_t_username(user.username, wallet_name)

        reply_markup = ReplyKeyboardMarkup([[USER_MAIN_MENU_BUTTON, WALLET_BUTTON]], resize_keyboard=True)

        await update.message.reply_text(RESPONSE_WALLET_DELETE_SUCCESS.format(wallet=wallet_name), reply_markup=reply_markup)
