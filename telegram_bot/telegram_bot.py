# Import the required libraries
import os
import logging
from dotenv import load_dotenv
from telegram import Update, ForceReply, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, ContextTypes, MessageHandler, filters
import asyncio

# Local imports
from charts.my_charts import create_chart, create_graph_price

# Import the required responses
## TODO

# Load the environment variables
load_dotenv()

# Set the logging level
logging.basicConfig(level=logging.INFO)

# Set the bot token
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

# Define the image function
async def chart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /chart is issued."""
    user = update.effective_user

    # Get arguments
    token1 = context.args[0].lower() if len(context.args) > 0 else 'btc'
    token2 = context.args[1].lower() if len(context.args) > 1 else 'usdt'
    time_range = context.args[2].lower() if len(context.args) > 2 else '1h'
    exchange = context.args[3].lower() if len(context.args) > 3 else 'sunswap'

    if token1 == 'trx':
        token1 = 'wtrx'

    if token2 == 'trx':
        token2 = 'wtrx'

    # Check time range
    if time_range not in ['1m','5m', '15m', '30m' '1h', '2h', '3h', '4h', '1d', "1m", "5m", "15m", "30m", "1h", "2h", "3h", "4h", "1d"]:
        await update.message.reply_text(f"Invalid time range '{time_range}'. Please use one of the following: 1m, 5m, 15m, 30m, 1h, 2h, 3h, 4h, 1d")
        return

    # Check exchanges
    if exchange not in ['sunswap', 'jm', 'iswapv1', 'iswapv2', "sunswap", "jm", "iswapv1", "iswapv2"]:
        await update.message.reply_text(f"Invalid exchange {exchange}. Please use one of the following: sunswap, iswapv1, iswapv2, jm")
        return

    file = create_chart(token1, token2, exchange, time_range)

    await update.message.reply_photo(
        photo=file,
        caption=f"Chart for {token1}/{token2} on {exchange} and each candle is {time_range}.",
    )

# Define the image function
async def price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /chart is issued."""
    user = update.effective_user

    # Get arguments
    token1 = context.args[0].lower() if len(context.args) > 0 else 'btc'
    token2 = context.args[1].lower() if len(context.args) > 1 else 'usdt'
    exchange = context.args[2].lower() if len(context.args) > 2 else 'sunswap'

    if token1 == 'trx':
        token1 = 'wtrx'

    if token2 == 'trx':
        token2 = 'wtrx'

    # Check exchanges
    if exchange not in ['sunswap', 'jm', 'iswapv1', 'iswapv2', "sunswap", "jm", "iswapv1", "iswapv2"]:
        await update.message.reply_text(f"Invalid exchange {exchange}. Please use one of the following: sunswap, iswapv1, iswapv2, jm")
        return

    data = create_graph_price(token1, token2, exchange)

    await update.message.reply_photo(
        photo=data['file'],
        caption=data['msg'],
    )


# Define the main function
def run_bot_telegram() -> None:
    # Create the event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Create the Updater and pass it the bot's token
    print(f"Bot started with token: {TELEGRAM_TOKEN}")
    application = Application.builder().token(f"{TELEGRAM_TOKEN}").build()

    
    application.add_handler(CommandHandler('chart', chart))
    application.add_handler(CommandHandler('price', price))


    # Add a fallback handler to handle unmatched commands which might be previous commands inputs
    # application.add_handler(MessageHandler(filters.Regex(f'.*'), fallback_handler))

    # Start the Bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)
