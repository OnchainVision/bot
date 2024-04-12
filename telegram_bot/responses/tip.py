
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from blockchain.tip_contract import tip_call
from db.transactions import record_tip_by_t_username
from db.wallets import get_all_wallets_by_t_username
from blockchain.tip_contract import get_tip_balance
from blockchain.tx import check_tx_status
from utils.wallet import is_address, get_url_by_tx
from utils.convert import is_int, convert_to_int, human_format
from utils.jokes import get_tip_joke_text_and_animation
from constants.parameters import PARAMETER_MIN_AMOUNT_JOKE
from db.parameters import get_param
from db.balances import get_balance_by_t_username
from constants.parameters import PARAMETER_TIP_FEE_BTT
from constants.globals import TIP_INSUFFICIENT_BALANCE


# Define the tip function
async def tip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # If the context args length is less than 2, return an error message
    if len(context.args) < 2:
        await update.message.reply_text('Usage: /tip amount @user')
        return

    # Get the user and amount
    sender = update.message.from_user
    amount = context.args[0]
    receiver = context.args[1][1:]

    if is_int(amount) == False:
        await update.message.reply_text('Invalid amount')
        return

    if context.args[1][0] != '@':
        await update.message.reply_text("You must include the @ to send to a user \n\n Usage: /tip amount @user")
        return
    
    if sender.username == receiver:
        await update.message.reply_text("You can't tip yourself! 🤦‍♂️")
        return

    amount_int = convert_to_int(amount)
    balance_sender = get_balance_by_t_username(sender.username)
    fee = int(get_param(PARAMETER_TIP_FEE_BTT))

    if balance_sender + fee < amount_int:
        await update.message.reply_text(TIP_INSUFFICIENT_BALANCE.format(balance=human_format(balance_sender), max=human_format(balance_sender)))
        return

    result = record_tip_by_t_username(sender.username, receiver, amount_int)
    min_joke_amount = get_param(PARAMETER_MIN_AMOUNT_JOKE)

    if amount_int >= min_joke_amount:
        tip_animation = get_tip_joke_text_and_animation(amount_int)
        joke_animation = tip_animation['animation']
        joke = tip_animation['joke']
        await update.message.reply_animation(
            animation=joke_animation,
            caption=f"{result} \n\n {joke}",
        )
    else:
        await update.message.reply_text(result)
        

# Define the tip function
async def tipOnChain(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # If the context args length is less than 2, return an error message
    if len(context.args) < 2:
        await update.message.reply_text('Usage: /tipOnChain <amount> <address>/@user')
        return

    # Get the user and amount
    sender = update.message.from_user
    amount = context.args[0]
    receiver = context.args[1]
    print(f"TipOnChain: sender={sender} amount={amount} receiver={receiver}, receiver[0]={receiver[0]}")
    

    # Get all the user's wallets
    wallets = get_all_wallets_by_t_username(sender.username)
    
    # If the user has no wallets, return an error message
    if wallets == []:
        await update.message.reply_text('You have no wallets. Please create a wallet first.')
        return

    # Validate the amount 
    if is_int(amount) == False:
        await update.message.reply_text('Invalid amount \n\n Usage: /tipOnChain <amount> <address>/@user')
        return

    # Validate the address or the username
    address_input = is_address(receiver)

    print(f" receiver[0] != '@'={ receiver[0] != '@'} receiver[0]={receiver[0]}, address_input={address_input}")

    if address_input or receiver[0] != '@':
        await update.message.reply_text('Invalid address or username(use @). \n\n Usage: /tipOnChain <amount> <address>/@user')
        return

    amount_int = convert_to_int(amount)

    if address_input == True:
        my_wallet = None
        # Iterate through the wallets and get the $TIP balance
        for wallet in wallets:
            balance = get_tip_balance(wallet['address'])
            if balance >= amount_int:
                my_wallet = wallet
        
        if my_wallet is None:
            await update.message.reply_text('You do not have enough $TIP to send')
            return
        else:
            print(f"TipOnChain by address: sender={sender} amount={amount} receiver={receiver}")

            tx = tip_call(my_wallet['address'],receiver, amount_int, my_wallet['pk'])
            url = get_url_by_tx(tx)
            reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Explorer", url=url)]])
            if check_tx_status(tx) == True:
                await update.message.reply_html(f"Tip successful!", reply_markup=reply_markup)
            else:
                await update.message.reply_html(f"Tip failed!", reply_markup=reply_markup)
    elif receiver[0] == '@':
        username = receiver[1:]
        if sender.username == username:
            await update.message.reply_text("You can't tip yourself! 🤦‍♂️")
            return

        # Get the user's wallets
        wallets_receiver = get_all_wallets_by_t_username(username)

        if wallets_receiver == []:
            await update.message.reply_text(f'The receiver has no wallets. Please ask them to create a wallet first. \n\n User @{sender.username} wants to tip you @{username} \n\n Please create a wallet @{username} to receive OnChain Tips.')
            return

        receiver_wallet = wallets_receiver[0]
        my_wallet = None

        for wallet in wallets:
            balance = get_tip_balance(wallet['address'])
            if balance >= amount_int:
                my_wallet = wallet

        if my_wallet is None:
            await update.message.reply_text('You do not have enough $TIP to send')
            return
        else:
            print(f"TipOnChain by username: sender={sender} amount={amount} receiver={receiver_wallet}")

            tx = tip_call(my_wallet['address'], receiver_wallet['address'], amount_int, my_wallet['pk'])
            url = get_url_by_tx(tx)
            reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Explorer", url=url)]])
            if check_tx_status(tx) == True:
                await update.message.reply_html(f"Tip successful from user @{sender.username} from his wallet #{my_wallet['name']} to user @{username}! to wallet #{receiver_wallet['name']}", reply_markup=reply_markup)
            else:
                await update.message.reply_html(f"Tip failed for user @{username}!", reply_markup=reply_markup)


    else:
        await update.message.reply_text('Error: Invalid address or username(use @). \n\n Usage: /tipOnChain <amount> <address>/@user')
        return



# Define the rain function
async def rain(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # If the context args length is less than 2, return an error message
    if len(context.args) < 1:
        await update.message.reply_text('Usage: /rain amount')
        return

    # Get the user and amount
    sender = update.message.from_user
    amount = context.args[0]
    receiver = context.args[1][1:]

    if is_int(amount) == False:
        await update.message.reply_text('Invalid amount')
        return

    # Get all the users in the group
    users = update.message.chat.get_members_count()

    # Get a list of the usersname in the group
    return
    


