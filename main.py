from telegram_bot.telegram_bot import run_bot_telegram
from discord_bot.discord_bot import run_bot_discord
import threading

# Run the main function
if __name__ == '__main__':
    # Create a thread to run the bot
    telegram_bot_thread = threading.Thread(target=run_bot_telegram)
    discord_bot_thread = threading.Thread(target=run_bot_discord)

    # Start the thread
    telegram_bot_thread.start()
    discord_bot_thread.start()

    # Wait for the thread to finish
    telegram_bot_thread.join()
    discord_bot_thread.join()


