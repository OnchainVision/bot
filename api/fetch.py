from datetime import datetime

from .fetchAPI import fetch_on_chain_tokens, fetch_on_chain_pairs, fetch_on_chain_exchanges, fetch_on_chain_pair_price
from .constants import TOKEN_NAME_AGAINST, EXCHANGE_DEFAULT

fetch_time = datetime.now()
max_catch_time_range = 60 * 24 # 24 hours
cachedWhitelistExchanges = {}
cachedWhitelistTokens = {}


def fetch_token_whitelist():
    global cachedWhitelistTokens
    if not cachedWhitelistTokens or (datetime.now() - fetch_time).min > max_catch_time_range:
        print('fetch_token_whitelist: Fetching whitelist tokens from database')
        fetch_time = datetime.now()
        tokens = fetch_on_chain_tokens()

        # From tokens, get the whitelist tokens
        whitelist_tokens = [ token for token in tokens if token['whitelist'][0] == "Y"]
        print('fetch_token_whitelist: Nr of whitelist tokens:', len(whitelist_tokens))
        return whitelist_tokens

    return cachedWhitelistTokens

def fetch_exchanges():
    if not cachedWhitelistExchanges or (datetime.now() - fetch_time).min > max_catch_time_range:
        print('fetch_exchanges: Fetching exchanges from database')
        fetch_time = datetime.now()
        exchanges = fetch_on_chain_exchanges()
        print('fetch_exchanges: Nr of exchanges:', len(exchanges))
        return exchanges
    return cachedWhitelistExchanges


def fetch_token(token_name='btc'):
    tokens = fetch_token_whitelist()
    my_token = None

    # Search the token by token_name
    for token in tokens:
        if token['symbol'].lower() == token_name.lower():
            print(f'Token="{token}" found in whitelist tokens.')
            my_token = token

    if my_token is None:
        print(f'Token="{token_name}" not found in whitelist tokens.')
        return None
    else:
        return my_token

def fetch_exchange(exchange=EXCHANGE_DEFAULT):
    exchanges = fetch_exchanges()
    my_exchange = None

    # Search the exchange by exchange_name without spaces
    for ex in exchanges:
        if exchange.lower() in ex['name'].replace(" ", "").lower():
            print(f'Exchange="{exchange}" found in whitelist exchanges.')
            my_exchange = ex

    if my_exchange is None:
        print(f'Exchange="{exchange}" not found in whitelist exchanges.')
        return None
    else:
        return my_exchange

def fetch_pair_price(token_input, against_token=TOKEN_NAME_AGAINST, exchange=EXCHANGE_DEFAULT):
    # Get the token
    token0 = fetch_token(token_input)
    token1 = fetch_token(against_token)
    exchange = fetch_exchange(exchange)

    pairs = fetch_on_chain_pairs(exchange=exchange['id'], token0=token0['address'], token1=token1['address'])

    if len(pairs) == 0:
        print(f'fetch_pair_price: No pairs found for token="{token_input}" and exchange="{exchange}"')
        return None
    elif len(pairs) > 1:
        print(f'fetch_pair_price: Multiple pairs found for token="{token_input}" and exchange="{exchange}"')
        return None

    # Fetch the pair data
    df = fetch_on_chain_pair_price(pairs[0], 5000, token0, token1)

    return df

