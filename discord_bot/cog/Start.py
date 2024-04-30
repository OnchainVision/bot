
from nextcord.ext import commands

HELP_MESSAGE = '''
Hello! I am OnChainVisionBot on Tron. I am here to provide you with on-chain data.
/tokens - List of whitelisted tokens
/price <token1> <token2> [<exchange>] - Get the price of a token on an exchange (default: sunwap)
/chart <token1> <token2> [<timeframe>] [<exchange>] - Get the chart of a token on an exchange (default: sunwap, timeframe: 1d)
/volume <token1> <token2> <timeframe> <exchange> - Get the volume of a token on an exchange
/liquidity <token1> <token2> [<exchange>] - Get the liquidity of a token on an exchange (default: sunwap)


'''

class Start(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def start(self, ctx):
        user = ctx.author
        print(f'user="{user}"')
        ret = await ctx.send(f"Hello {user.mention}! I am OnChainVisionBot. I am here to provide you with on-chain data. "
                       f"Type /help to see the list of commands available.")
        

    # @commands.command()
    # async def help(self, ctx):
    #     user = ctx.author
    #     print(f'user="{user}"')
    #     ret = await ctx.send(text = HELP_MESSAGE)
        