import nextcord
from nextcord import Intents, Client, Message, Embed, File, ActionRow, ButtonStyle
from nextcord.ui import Button
from nextcord.ext import commands

# from .cog.Wallet import Wallet
# from .cog.Balance import Balance
from .cog.Start import Start
from .cog.Chart import Chart

from typing import Final
from time import sleep
import os
import io
import logging
import random
from random import randint
from dotenv import load_dotenv
from .responses import get_response

from charts.my_charts import create_chart

# STEP 0: LOAD OUR TOKEN FROM SOMEWHERE SAFE
load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

description = '''Commands for OnChainVisionBot.

Price, charts, analyses and more on chain data.'''

# STEP 1: BOT SETUP
intents: Intents = Intents.default()
intents.message_content = True
intents.members = True

# client: Client = Client(intents=intents)
bot = commands.Bot(command_prefix='/', description=description, intents=intents)

# STEP 3: HANDLING THE STARTUP FOR OUR BOT
@bot.event
async def on_ready() -> None:
    print(f'{bot.user} is now running!')



# Define the price command
# @bot.command(description='Check the price of a token.')
# async def price(ctx, amount: int, receiver: str):
#     """SCheck the price of a token."""
#     sender = ctx.author
#     await ctx.send(
#         f"Price undef"
#     )


# @bot.command(description='Command for a chart onchain')
# async def chart(ctx):
#     """Send a message when the command /gm is issued."""
#     user = ctx.author
#     imgBytes = create_chart()
#     # Create a BytesIO object from the image bytes
#     img_bytes_io = io.BytesIO(imgBytes)
#     await ctx.send(file=File(fp=img_bytes_io, filename='image.png'))


def run_bot_discord():
    """Run the Discord bot."""
    # Run the bot
    bot.add_cog(Start(bot))
    bot.add_cog(Chart(bot))
    bot.run(TOKEN)