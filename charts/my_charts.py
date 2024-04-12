import plotly.graph_objects as go

from api.fetchAPI import fetch_pair_data, fetch_pair_analyze, fetch_on_chain_pairs
from api.fetch import fetch_pair_price, fetch_token, fetch_exchange

def create_chart(token_name = 'btc', token_again = 'usdt', exchange = 'sunswap', time_range = '1h'):
    # Add trace
    token0 = fetch_token(token_name)
    token1 = fetch_token(token_again)
    exchange = fetch_exchange(exchange)

    
    pairs = fetch_on_chain_pairs(exchange=exchange['id'], token0=token0['address'], token1=token1['address'])

    if len(pairs) == 0:
        print(f'fetch_pair_price: No pairs found for token="{token_name}" and exchange="{exchange}"')
        return None
    elif len(pairs) > 1:
        print(f'fetch_pair_price: Multiple pairs found for token="{token_name}" and exchange="{exchange}"')
        return None

    df = fetch_pair_data(pairs[0]['address'], time_range, reversed=False, force_update=1)

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


def create_graph_price(token_name = 'btc'):
    # Add trace
    selected_pair = 'TTQpjqQUjMJjF3MAvWWVURn3YrRxg2quTM'
    time_range = '1h'

    df = fetch_pair_price(token_name)

    # Iterate over all list and get a list of df['time']
    times = [df[i]['time'] for i in range(len(df))]
    prices = [df[i]['price'] for i in range(len(df))]


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
    return img_bytes


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