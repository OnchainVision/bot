
from nextcord.ext import commands

from db.balances import get_balance_by_d_username
from constants.responses import RESPONSE_BALANCE_MAIN

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



class Start(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def start(self, ctx):
        user = ctx.author
        print(f'user="{user}"')

        # Check if the message is in a private chat or the bot is tagged in the message
        if ctx.guild is None or self.bot.user in ctx.message.mentions:
            result = setup_user(t_first_name=user.global_name, 
                                t_last_name=user.nick, 
                                t_username='', 
                                t_id_telegram=user.id, 
                                t_is_bot=user.bot, 
                                d_username=user.name)
            if result == USER_NEW_USER_ADDED:
                message_text = DEFAULT_WELCOME_MESSAGE.format(user=user.name)
                record_welcome_bonus_by_t_username(user.name)
            else:
                message_text = DEFAULT_WELCOME_BACK_MESSAGE.format(user=user.name)
            
            # Update the command state
            previous_state = '/start'
            set_command_by_t_username(user.name, previous_state)
            
            await ctx.send(message_text)
        else:
            await ctx.send('Please use this command in a private chat or tag me in a message.')
