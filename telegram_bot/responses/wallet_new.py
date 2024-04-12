
from telegram import ReplyKeyboardMarkup
from blockchain.wallet import create_wallet, get_address_and_private_key
from db.wallets import add_wallet_by_t_username
from db.users import set_command_by_t_username
from constants.globals import (
    WALLET_PK_PROVIDED,
    WALLET_GENERATE_BUTTON,
    WALLET_IMPORT_BUTTON,
    WALLET_NEW_BUTTON,
    WALLET_BUTTON,
    WALLET_GENERATE_BUTTON,
    WALLET_IMPORT_BUTTON,
    USER_MAIN_MENU_BUTTON,
)

# Wallet goes to 
# 1. Wallet (wallet_private)
#   1.1. New Wallet (wallet_new)
#     1.1.1. Generate Wallet (wallet_generate_address)
#     1.1.2. Import Wallet (wallet_import_address)

async def wallet_new(update, context):
    user = update.effective_user
    # Check if the command was sent in a private chat
    set_command_by_t_username(user.username, WALLET_NEW_BUTTON)

    reply_markup = ReplyKeyboardMarkup([[WALLET_GENERATE_BUTTON, WALLET_IMPORT_BUTTON]], resize_keyboard=True)

    if update.message.chat.type == 'private':
        # Let's create a new wallet for the user
        # Ask the user for the name of the wallet
        await update.message.reply_text("Please choose if you want to import or generate. We recommend to generate a new one", reply_markup=reply_markup)

async def wallet_generate_address(update, context):
    user = update.effective_user
    # Check if the command was sent in a private chat
    set_command_by_t_username(user.username, WALLET_GENERATE_BUTTON)

    if update.message.chat.type == 'private':
        # Let's create a new wallet for the user
        # Ask the user for the name of the wallet
        await update.message.reply_text("Please input the name of the new wallet")


async def wallet_generate_address_response(update, context):
    user = update.effective_user
    # Check if the command was sent in a private chat
    if update.message.chat.type == 'private':
        # Get the name of the wallet from the user's response
        wallet_name = update.message.text

        # Now let's create a new wallet for the user
        wallet = create_wallet()
        print(f"wallet: {wallet}")
        address = wallet['address']

        add_wallet_by_t_username(user.username, wallet_name, address, wallet['pk'])
        
        set_command_by_t_username(user.username, WALLET_BUTTON)
        reply_markup = ReplyKeyboardMarkup([[USER_MAIN_MENU_BUTTON, WALLET_BUTTON]], resize_keyboard=True)

        # Your code here to create a new wallet with the given name
        await update.message.reply_text(f"New wallet '{wallet_name}' with address {address} created!", reply_markup=reply_markup)


async def wallet_import_address(update, context):
    user = update.effective_user
    set_command_by_t_username(user.username, WALLET_IMPORT_BUTTON)

    # Check if the command was sent in a private chat
    if update.message.chat.type == 'private':
        # Let's create a new wallet for the user
        # Ask the user for the name of the wallet
        await update.message.reply_text("Please provide a primary key:")


async def wallet_import_address_response_pk(update, context):
    user = update.effective_user
    
    # Check if the command was sent in a private chat
    if update.message.chat.type == 'private':
        # Get the name of the wallet from the user's response
        wallet_pk = update.message.text
        set_command_by_t_username(user.username, WALLET_PK_PROVIDED + wallet_pk)

        # Your code here to create a new wallet with the given name
        await update.message.reply_text(f"Pk provided: {wallet_pk}. Please input the name of the new wallet")


async def wallet_import_address_response_name(update, context, pk):
    user = update.effective_user
    # Check if the command was sent in a private chat
    if update.message.chat.type == 'private':
        # Get the name of the wallet from the user's response
        wallet_name = update.message.text

        if len(pk) != 66: 
            set_command_by_t_username(user.username, WALLET_IMPORT_BUTTON)
            await update.message.reply_text(f"Invalid pk provided: {pk}. Please input the primary key again.")
            return

        # Now let's create a new wallet for the user
        wallet = get_address_and_private_key(pk)
        print(f"wallet: {wallet}")
        address = wallet['address']

        add_wallet_by_t_username(user.username, wallet_name, address, wallet['pk'])

        set_command_by_t_username(user.username, WALLET_BUTTON)
                                  
        #reply back
        reply_markup = ReplyKeyboardMarkup([[USER_MAIN_MENU_BUTTON, WALLET_BUTTON]], resize_keyboard=True)

        # Your code here to create a new wallet with the given name
        await update.message.reply_text(f"New wallet '{wallet_name}' with address {address} address!", reply_markup=reply_markup)