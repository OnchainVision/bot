

from nextcord.ext import commands
from nextcord import File
import io
import datetime

# Local imports
from charts.my_charts import create_chart, create_graph_price, create_volume_info, create_liquidity_info
from api.fetch import fetch_token_whitelist


class Chart(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #/tokens - List of whitelisted tokens
    @commands.command()
    async def tokens(self, ctx):
        token = fetch_token_whitelist()

        msg = f"🤍 Whitelisted tokens: \n\n"
        for t in token:
            msg += f"{t['symbol']} - {t['name']} \n"
        await ctx.send(msg)
    
    #/price <token1> <token2> [<exchange>] - Get the price of a token on an exchange (default: sunswap)
    @commands.command()
    async def price(self, ctx, token1: str, token2: str, exchange: str = 'sunswap'):
        if token1 == 'trx':
            token1 = 'wtrx'

        if token2 == 'trx':
            token2 = 'wtrx'

        # Check exchanges
        if exchange not in ['sunswap', 'jm', 'iswapv1', 'iswapv2', "sunswap", "jm", "iswapv1", "iswapv2"]:
            await ctx.send(f"Invalid exchange {exchange}. Please use one of the following: sunswap, iswapv1, iswapv2, jm")
            return

        data = create_graph_price(token1, token2, exchange)
        
        img_bytes_io = io.BytesIO(data['file'])

        # Get the current date
        date = datetime.datetime.now().strftime("%Y-%m-%d")

        await ctx.send(
            file= File(fp=img_bytes_io, filename=f"p_{token1}/{token2}_on_{exchange}_at_{date}.png"),
            content=data['msg'],
        )
    
    #/chart <token1> <token2> [<timeframe>] [<exchange>] - Get the chart of a token on an exchange (default: susnwap, timeframe: 1d)
    @commands.command()
    async def chart(self, ctx, token1: str, token2: str, timeframe: str = '1d', exchange: str = 'sunswap'):
        if token1 == 'trx':
            token1 = 'wtrx'

        if token2 == 'trx':
            token2 = 'wtrx'

        # Check time range
        if timeframe not in ['1m','5m', '15m', '30m', '1h', '2h', '3h', '4h', '1d']:
            await ctx.send(f"Invalid time range '{timeframe}'. Please use one of the following: 1m, 5m, 15m, 30m, 1h, 2h, 3h, 4h, 1d")
            return

        # Check exchanges
        if exchange not in ['sunswap', 'jm', 'iswapv1', 'iswapv2', "sunswap", "jm", "iswapv1", "iswapv2"]:
            await ctx.send(f"Invalid exchange {exchange}. Please use one of the following: sunswap, iswapv1, iswapv2, jm")
            return

        data = create_chart(token1, token2, exchange, timeframe)
        
        img_bytes_io = io.BytesIO(data)

        # Get the current date
        date = datetime.datetime.now().strftime("%Y-%m-%d")

        await ctx.send(
            file= File(fp=img_bytes_io, filename=f"c_{token1}/{token2}_on_{exchange}_at_{date}.png"),
            content=f"Chart for {token1}/{token2} on {exchange} and each candle is {timeframe}.",
        )
    
    #/volume <token1> <token2> <timeframe> <exchange> - Get the volume of a token on an exchange
    @commands.command()
    async def volume(self, ctx, token1: str, token2: str, timeframe: str, exchange: str):
        if token1 == 'trx':
            token1 = 'wtrx'

        if token2 == 'trx':
            token2 = 'wtrx'

        # Check time range
        if timeframe not in ['1m','5m', '15m', '30m', '1h', '2h', '3h', '4h', '1d']:
            await ctx.send(f"Invalid time range '{timeframe}'. Please use one of the following: 1m, 5m, 15m, 30m, 1h, 2h, 3h, 4h, 1d")
            return

        # Check exchanges
        if exchange not in ['sunswap', 'jm', 'iswapv1', 'iswapv2', "sunswap", "jm", "iswapv1", "iswapv2"]:
            await ctx.send(f"Invalid exchange {exchange}. Please use one of the following: sunswap, iswapv1, iswapv2, jm")
            return

        data = create_volume_info(token1, token2, exchange, timeframe)
        
        img_bytes_io = io.BytesIO(data['file'])

        # Get the current date
        date = datetime.datetime.now().strftime("%Y-%m-%d")

        await ctx.send(
            file= File(fp=img_bytes_io, filename=f"vol_{token1}/{token2}_on_{exchange}_at_{date}.png"),
            content=data['msg'],
        )
    
    #/liquidity <token1> <token2> [<exchange>] - Get the liquidity of a token on an exchange (default: sunswap)
    @commands.command()
    async def liquidity(self, ctx, token1: str, token2: str, exchange: str = 'sunswap'):
        if token1 == 'trx':
            token1 = 'wtrx'

        if token2 == 'trx':
            token2 = 'wtrx'

        # Check exchanges
        if exchange not in ['sunswap', 'jm', 'iswapv1', 'iswapv2', "sunswap", "jm", "iswapv1", "iswapv2"]:
            await ctx.send(f"Invalid exchange {exchange}. Please use one of the following: sunswap, iswapv1, iswapv2, jm")
            return

        data = create_liquidity_info(token1, token2, exchange)

        await ctx.send(
            content=data['msg'],
        )
