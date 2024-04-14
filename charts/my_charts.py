import plotly.graph_objects as go
import plotly.express as px

from api.fetchAPI import fetch_pair_data, fetch_pair_analyze, fetch_on_chain_pairs, fetch_on_chain_exchanges
from api.fetch import fetch_pair_price, fetch_token, fetch_exchange
from utils.convert import human_format

ONCHAINVISION_WEBSITE = "https://onchainvision.com"

def create_chart(token_name = 'btc', token_again = 'usdt', exchange = 'sunswap', time_range = '1h'):
    reversed = False
    # Add trace
    token0 = fetch_token(token_name)
    token1 = fetch_token(token_again)
    exchange = fetch_exchange(exchange)

    
    pairs = fetch_on_chain_pairs(exchange=exchange['id'], token0=token0['address'], token1=token1['address'])

    if len(pairs) == 0:
        print(f'create_chart: No pairs found for token="{token_name}" and exchange="{exchange}"')
        # we might have a reversed pair
        pairs = fetch_on_chain_pairs(exchange=exchange['id'], token0=token1['address'], token1=token0['address'])
        reversed = True
        if len(pairs) == 0:
            return None
    elif len(pairs) > 1:
        print(f'create_chart: Multiple pairs found for token="{token_name}" and exchange="{exchange}"')
        return None

    df = fetch_pair_data(pairs[0]['address'], time_range, reversed=reversed, force_update=1)

    # Iterate over all list and get a list of df['time']
    times = [df[i]['time'] for i in range(len(df))]
    highs = [df[i]['high'] for i in range(len(df))]
    lows = [df[i]['low'] for i in range(len(df))]
    opens = [df[i]['open'] for i in range(len(df))]
    closes = [df[i]['close'] for i in range(len(df))]


    fig = go.Figure(data=go.Candlestick(x=times,
                    open=opens,
                    high=highs,
                    low=lows,
                    close=closes))
    
    fig.update(layout_xaxis_rangeslider_visible=False)

    # Add images
    fig.add_layout_image(
            dict(
                source="https://media.discordapp.net/attachments/1138135373688623245/1138135500566319214/On-Chain_Vision-512.png?ex=661d4b48&is=660ad648&hm=3951a294c3ca36a73a03d7f3d7dd86cad0acbf440a1553485d52ea501717eac1&=&format=webp&quality=lossless&width=640&height=640",
                xref="x",
                yref="y",
                x=0,
                y=3,
                sizex=2,
                sizey=2,
                sizing="stretch",
                opacity=0.5,
                layer="below"
                )
    )

    # Set templates
    fig.update_layout(template="plotly_white")
    # img_bytes = fig.to_image(format="png", width=fig.layout.width, height=fig.layout.height)
    img_bytes = fig.to_image(format="png", width=600, height=350, scale=2)
    return img_bytes


def create_graph_price(token1, token2, exchange):
    # Add trace
    df = fetch_pair_price(token1, token2, exchange)

    # Iterate over all list and get a list of df['time']
    times = [df[i]['time'] for i in range(len(df))]
    prices = [df[i]['price'] for i in range(len(df))]

    last_price = prices[-1]
    last_time = times[-1]
    start_time = times[0]
    length = len(prices)
    avg_price = sum(prices) / len(prices)


    fig = go.Figure()

    fig.add_trace(go.Scatter(x=times, y=prices,
                    mode='lines+markers',
                    name='lines+markers'))

    # Add images
    fig.add_layout_image(
            dict(
                source="https://media.discordapp.net/attachments/1138135373688623245/1138135500566319214/On-Chain_Vision-512.png?ex=661d4b48&is=660ad648&hm=3951a294c3ca36a73a03d7f3d7dd86cad0acbf440a1553485d52ea501717eac1&=&format=webp&quality=lossless&width=640&height=640",
                xref="x",
                yref="y",
                x=0,
                y=3,
                sizex=2,
                sizey=2,
                sizing="stretch",
                opacity=0.5,
                layer="below"
                )
    )

    # Set templates
    fig.update_layout(template="plotly_white")
    # img_bytes = fig.to_image(format="png", width=fig.layout.width, height=fig.layout.height)
    img_bytes = fig.to_image(format="png", width=600, height=350, scale=2)
    msg = f"""
DEX data 🗃️ for {exchange}:

👉Last price for {token1} is {last_price} {token2} 

📐 Average price for {token1} is {avg_price} {token2}

🕘Last time traded: {last_time} UTC

With a total of {length} trades since {start_time} UTC
"""
    return {'file': img_bytes, 'msg': msg}


def create_liquidity_info(token1_in = "btc", token2_in = "all", exchange = "all"):
    token0 = fetch_token(token1_in)
    token1 = None if token2_in == "all" else fetch_token(token2_in)
    exchange = None if exchange == "all" else fetch_exchange(exchange)

    pairs = fetch_on_chain_pairs(exchange=exchange['id'], token0=token0['address'], token1=token1['address'], forceUpdate = True)
    pairs_reverse = None
    msg = None

    if token2_in == "all" or len(pairs) == 0:
        pairs_reverse = fetch_on_chain_pairs(exchange=exchange['id'], token0=token1['address'], token1=token0['address'], forceUpdate = True)
    
    if len(pairs) == 0 and pairs_reverse is None:
        print(f'create_liquidity_info: No pairs found for token="{token1_in}/{token2_in}" and exchange="{exchange}"')
        return None
    elif len(pairs) == 1:
        if pairs[0]['tokenA'] == token0['id']:
            msg = f"🧮 A total of {human_format(pairs[0]['tokenABalance'])} {token0['symbol']} and {human_format(pairs[0]['tokenBBalance'])} {token1['symbol']} are in the liquidity pool for {token1_in}/{token2_in} over {exchange['name']}. \n\n"
        else:
            msg = f"🧮 A total of {human_format(pairs[0]['tokenBBalance'])} {token0['symbol']} and {human_format(pairs[0]['tokenABalance'])} {token1['symbol']} are in the liquidity pool for {token1_in}/{token2_in} over {exchange['name']}. \n\n"
    elif len(pairs_reverse) == 1:
        if pairs[0]['tokenA'] == token0['id']:
            msg = f"🧮 A total of {human_format(pairs[0]['tokenABalance'])} {token0['symbol']} and {human_format(pairs[0]['tokenBBalance'])} {token1['symbol']} are in the liquidity pool for {token1_in}/{token2_in} over {exchange['name']}. \n\n"
        else:
            msg = f"🧮 A total of {human_format(pairs[0]['tokenBBalance'])} {token0['symbol']} and {human_format(pairs[0]['tokenABalance'])} {token1['symbol']} are in the liquidity pool for {token1_in}/{token2_in} over {exchange['name']}. \n\n"


    return {'file': None, 'msg': msg}
    
    # all_pairs = pairs if pairs_reverse is None else pairs + pairs_reverse
    
    # Iterate over all the pairs check the pair 
    # if exchange is None and len(all_pairs) > 1:
    #     all_exchanges = fetch_on_chain_exchanges()
    
    # msg = f"🧮 A total of {len(all_pairs)} pairs found for {token1_in} over all exchanges. \n\n"

    # Iterate over all the pairs look at the token1 for pairs and token0 for pairs_reverse 
    # Query the token id and get the symbol





    

        



def create_volume_info(token1_in = "btc", token2_in = "all", exchange = "all", time_range = "1h"):
    # Add trace
    token0 = fetch_token(token1_in)
    token1 = None if token2_in == "all" else fetch_token(token2_in)
    exchange = None if exchange == "all" else fetch_exchange(exchange)

    if token2_in != "all" and exchange != "all":
        msg_initial = f"Volume data 📈 for {token1_in}/{token2_in} over {exchange['name']}"
    elif token2_in == "all" and exchange != "all":
        msg_initial = f"Volume data 📈 for {token1_in} over {exchange['name']}"
    elif token2_in != "all" and exchange == "all":
        msg_initial = f"Volume data 📈 for {token1_in}/{token2_in} over all exchanges"
    else:
        msg_initial = f"Volume data 📈 for {token1_in} over all exchanges"

    
    pairs = fetch_on_chain_pairs(exchange=exchange['id'], token0=token0['address'], token1=token1['address'])

    if len(pairs) == 0:
        print(f'create_volume_info: No pairs found for token="{token1_in}" and exchange="{exchange}"')
        return None
    elif len(pairs) > 1 and token2_in != "all" and exchange != "all":
        print(f'create_volume_info: Multiple pairs found for token="{token2_in}" and exchange="{exchange}"')
        return None

    if (token2_in == "all" or exchange == "all" ) and len(pairs) > 1:
        # Cumulate all the volumes
        # d = fetch_pair_analyze(pairs, time_range, reversed=False, force_update=1)

        # # Iterate over all list and get a list of df['time']
        # times = [df[i]['time'] for i in range(len(df))]
        # volumeTokenA = [df[i]['volumeTokenA'] for i in range(len(df))]
        # volumeTokenB = [df[i]['volumeTokenB'] for i in range(len(df))]
        # fig = px.bar(x=times, y=volumeTokenA, title=f"Volume of {token1_in} in {exchange['name']}")
        pass
    elif len(pairs) == 1:
        df = fetch_pair_data(pairs[0]['address'], time_range, reversed=False, force_update=1)
        # Iterate over all list and get a list of df['time']
        times = [df[i]['time'] for i in range(len(df))]
        volumeTokenA = [df[i]['volumeTokenA'] for i in range(len(df))]
        volumeTokenB = [df[i]['volumeTokenB'] for i in range(len(df))]

        totalVolumeTokenA = sum(volumeTokenA)
        totalVolumeTokenB = sum(volumeTokenB)
        first_time = df[0]['time']

        msg = f"🧮 A total of {human_format(totalVolumeTokenA)} {token0['symbol']} were traded against {human_format(totalVolumeTokenB)} {token1['symbol']} were traded over {exchange['name']} starting with {first_time} UTC. \n\n"
        if pairs[0]['tokenA'] == token0['id']:
            fig = px.bar(df, x=times, y=volumeTokenB, title=msg_initial, labels={'x': 'Timestamp', 'y': f"{token1['symbol']} volume"})
            last_volume = df[-1]['volumeTokenB']
            ante_volume = df[-2]['volumeTokenB']
            print("df[-1]", df[-1])
            print("df[-2]", df[-2])
            percent = (last_volume - ante_volume) / ante_volume * 100
            print(f"last_volume={last_volume}, ante_volume={ante_volume}, percent={percent}")
            msg += f" 🕘 Last {time_range} volume traded: {human_format(last_volume)} {token1['symbol']} \n"
        else:
            fig = px.bar(x=times, y=volumeTokenA, title=msg_initial, labels={'x': 'Timestamp', 'y': f"{token0['symbol']} volume"})
            last_volume = df[-1]['volumeTokenA']
            msg += f" 🕘 Last {time_range} volume traded: {human_format(last_volume)} {token0['symbol']} \n"
        
    else:
        print(f'fetch_pair_price: No pairs found for token="{token1_in}" and exchange="{exchange}"')
        return None
    
    fig.update(layout_xaxis_rangeslider_visible=False)

    # Add images
    fig.add_layout_image(
            dict(
                source="https://media.discordapp.net/attachments/1138135373688623245/1138135500566319214/On-Chain_Vision-512.png?ex=661d4b48&is=660ad648&hm=3951a294c3ca36a73a03d7f3d7dd86cad0acbf440a1553485d52ea501717eac1&=&format=webp&quality=lossless&width=640&height=640",
                xref="x",
                yref="y",
                x=0,
                y=3,
                sizex=2,
                sizey=2,
                sizing="stretch",
                opacity=0.5,
                layer="below"
                )
    )

    # Set templates
    fig.update_layout(template="plotly_white")
    # img_bytes = fig.to_image(format="png", width=fig.layout.width, height=fig.layout.height)
    img_bytes = fig.to_image(format="png", width=600, height=350, scale=2)
    return {'file': img_bytes, 'msg': msg}

def create_figure(token_name = 'btc'):
    # Add trace
    selected_pair = 'TTQpjqQUjMJjF3MAvWWVURn3YrRxg2quTM'
    time_range = '1h'

    df = fetch_pair_data(selected_pair, time_range, reversed=False, force_update=0)

    # Iterate over all list and get a list of df['time']
    times = [df[i]['time'] for i in range(len(df))]
    highs = [df[i]['high'] for i in range(len(df))]
    lows = [df[i]['low'] for i in range(len(df))]
    opens = [df[i]['open'] for i in range(len(df))]
    closes = [df[i]['close'] for i in range(len(df))]


    fig = go.Figure(data=go.Ohlc(x=times,
                    open=opens,
                    high=highs,
                    low=lows,
                    close=closes))
    
    fig.update(layout_xaxis_rangeslider_visible=False)

    # Add images
    fig.add_layout_image(
            dict(
                source="https://media.discordapp.net/attachments/1138135373688623245/1138135500566319214/On-Chain_Vision-512.png?ex=661d4b48&is=660ad648&hm=3951a294c3ca36a73a03d7f3d7dd86cad0acbf440a1553485d52ea501717eac1&=&format=webp&quality=lossless&width=640&height=640",
                # xref="x",
                # yref="y",
                # x=0,
                # y=3,
                # sizex=2,
                # sizey=2,
                # sizing="stretch",
                # opacity=0.5,
                # layer="below"
                )
    )

    # Set templates
    fig.update_layout(template="plotly_white")

    # No margin for figure
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))

    img_bytes = fig.to_image(format="png", width=fig.layout.width, height=fig.layout.height)

    return img_bytes