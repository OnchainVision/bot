import requests
from datetime import datetime
import heapq

from typing import Final
import requests
from datetime import datetime
import os
from dotenv import load_dotenv


load_dotenv()
API_URL: Final[str] = os.getenv('ONCHAINVISION_API_URL')
TOKEN: Final[str] = os.getenv('ONCHAINVISION_API_TOKEN')

print(f'API_URL: {API_URL}')
print(f'TOKEN: {TOKEN}')



cacheSinglePair = {}
cachedPairs = {}
cachedNetworks = None
cachedExchanges = {}
cachePairData = {}
cachePairTxns = {}

headers = {
    'Authorization': f'Token {TOKEN}',
    'Content-Type': 'application/json',
}

requestOptions = {
    'headers': headers,
    'timeout': 60,  # 60 seconds
}

def fetch_on_chain_single_pair(pair_address):
    if pair_address == "":
        print("pair_address == '' (empty)")
        return {}  # Don't fetch if no network is selected, return an empty dictionary

    print(f'fetch_on_chain_single_pair: pair_address {pair_address}')

    if pair_address in cacheSinglePair:
        return cacheSinglePair[pair_address]

    try:
        api_url = f'{API_URL}/api/dex/pair/?address={pair_address}&forceUpdate=1'
        response = requests.get(api_url, **requestOptions)

        if not response.ok:
            raise Exception('Network response was not ok')

        data = response.json()
        my_pair = data[0]

        # Cache the fetched data
        cachePairData[pair_address] = my_pair
        return my_pair
    except Exception as error:
        print('Error fetching pairs:', error)
        return {}  # Return an empty dictionary if an error occurs

def fetch_on_chain_pairs(network = None, exchange = None, token0 = None, token1 = None, forceUpdate = None):
    if network == -1 and exchange == -1 and token0 == -1 and token1 == -1:
        print("network == exchange == token0 == token1 == -1")
        return []  # Don't fetch if no network, exchange, token0 is selected, return an empty list

    api_url = f'{API_URL}/api/dex/pair?'

    if network != -1 and network is not None:
        print(f'fetch_on_chain_pairs: Fetching Pairs for network={network}')
        api_url += f'network={network}&'

    if exchange != -1 and exchange is not None:
        print(f'fetch_on_chain_pairs: Fetching Pairs for exchange={exchange}')
        api_url += f'exchange={exchange}&'

    if token0 != -1 and token0 is not None:
        print(f'fetch_on_chain_pairs: Fetching Pairs for token0={token0}')
        api_url += f'token0={token0}&'

    if token1 != -1 and token1 is not None:
        print(f'fetch_on_chain_pairs: Fetching Pairs for token1={token1}')
        api_url += f'token1={token1}&'

    if forceUpdate != False and forceUpdate is not None:
        print(f'fetch_on_chain_pairs: Fetching forceUpdate for forceUpdate={forceUpdate}')
        api_url += f'forceUpdate=1&'

    # Remove the last '&'
    api_url = api_url[:-1]
    print(f'fetch_on_chain_pairs: api_url={api_url}')

    try:
        response = requests.get(api_url, **requestOptions)

        if not response.ok:
            raise Exception('Network response was not ok')

        data = response.json()
        print('Pairs done')
        return data
    except Exception as error:
        print('Error fetching pairs:', error)
        return []  # Return an empty list if an error occurs

def fetch_on_chain_networks():
    print('Fetching networks...')
    try:
        response = requests.get(f'{API_URL}/api/dex/networks', **requestOptions)

        if not response.ok:
            raise Exception('Network response was not ok')

        data = response.json()
        print('Networks done')
        return data
    except Exception as error:
        print('Error fetching networks:', error)
        return []  # Return an empty list if an error occurs

def fetch_on_chain_token_id(id):
    print(f'fetch_on_chain_network_id {id}')
    try:
        response = requests.get(f'{API_URL}/api/dex/token/{id}', **requestOptions)

        if not response.ok:
            raise Exception('Network response was not ok')

        data = response.json()
        print('fetch_on_chain_network_id done')
        return data
    except Exception as error:
        print('Error fetching networks:', error)
        return []  # Return an empty list if an error occurs

def fetch_on_chain_network_id(id):
    print(f'fetch_on_chain_network_id {id}')
    try:
        response = requests.get(f'{API_URL}/api/dex/networks/{id}', **requestOptions)

        if not response.ok:
            raise Exception('Network response was not ok')

        data = response.json()
        print('fetch_on_chain_network_id done')
        return data
    except Exception as error:
        print('Error fetching networks:', error)
        return []  # Return an empty list if an error occurs

def fetch_on_chain_exchange_id(id):
    print(f'fetch_on_chain_exchange_id {id}')
    try:
        response = requests.get(f'{API_URL}/api/dex/exchanges/{id}', **requestOptions)

        if not response.ok:
            raise Exception('Network response was not ok')

        data = response.json()
        print('Exchange ID done')
        return data
    except Exception as error:
        print('Error fetching Exchanges:', error)
        return []  # Return an empty list if an error occurs

def fetch_on_chain_tokens(network = None):
    print(f'fetch_on_chain_tokens: network {network}')

    try:
        url = f"{API_URL}/api/dex/token{'?network={network}' if network != None else ''}"
        print(f'fetch_on_chain_tokens: url {url}')
        response = requests.get(url, **requestOptions)

        if not response.ok:
            raise Exception('fetch_on_chain_tokens: Network response was not ok')

        data = response.json()
        print('fetch_on_chain_tokens: tokens done')
        return data

    except Exception as error:
        print('fetch_on_chain_tokens: Error fetching tokens:', error)
        return []  # Return an empty list if an error occurs


def fetch_on_chain_exchanges(network = None):
    print(f'fetch_on_chain_exchanges: network {network}')

    try:
        url = f"{API_URL}/api/dex/exchanges{'?network={network}' if network != None else ''}"
        print(f'fetch_on_chain_exchanges: url {url}')
        response = requests.get(url, **requestOptions)

        if not response.ok:
            raise Exception('fetch_on_chain_exchanges: Network response was not ok')

        data = response.json()
        print('fetch_on_chain_exchanges: Exchanges done')
        return data
    except Exception as error:
        print('fetch_on_chain_exchanges: Error fetching Exchanges:', error)
        return []  # Return an empty list if an error occurs

def fetch_networks():
    global cachedNetworks
    if not cachedNetworks:
        # If cached data is not available, fetch and cache it
        cachedNetworks = fetch_on_chain_networks()
    return cachedNetworks  # Return the cached data

def fetch_exchanges(selected_network):
    cache_exchange_key = str(selected_network)

    if cache_exchange_key in cachedExchanges:
        print(f'fetch_exchanges: Use cache for {cache_exchange_key} return {cachedExchanges[cache_exchange_key]}')
        return cachedExchanges[cache_exchange_key]

    try:
        # Add 'await' to properly wait for the asynchronous operation to complete
        data = fetch_on_chain_exchanges(selected_network)

        # Assuming fetch_on_chain_exchanges returns a promise, resolve it to get the actual data
        resolved_data = data

        cachedExchanges[cache_exchange_key] = resolved_data

        return resolved_data
    except Exception as error:
        print(f'Error fetching exchanges: {error}')
        # Handle the error appropriately (e.g., throw it, return

def fetch_pair_data(selected_pair, time_range, reversed=False, force_update=0):
    if not selected_pair:
        return None  # Don't fetch if no pair is selected
    print('Fetching PairData for pair address:', selected_pair)

    # Check if the data is in the cache and return it
    cache_key = f"{selected_pair}_{time_range}_reversed" if reversed else f"{selected_pair}_{time_range}"
    print("fetchPairData: cacheKey", cache_key)

    api_url = f"{API_URL}/api/dex/pairAudit/?address={selected_pair}{'&forceUpdate=1' if force_update else ''}&timeRange={time_range.lower()}{ '&reversed=true' if reversed else ''}"
    
    try:
        print("fetchPairData: apiUrl", api_url)
        
        response = requests.get(api_url, **requestOptions)
        response.raise_for_status()  # Raise exception for non-OK responses
        
        data = response.json()
        print("fetchPairData response ok")

        cdata = []
        for d in data:
            my_date = datetime.strptime(d['timestamp'], '%Y-%m-%dT%H:%M:%SZ')
            mapped_data = {
                'time': my_date,  # Convert the timestamp to a datetime object
                'open': float(d['open']),
                'high': float(d['high']),
                'low': float(d['low']),
                'close': float(d['close']),
                'volumeTokenA': float(d['volumeTokenA']),
                'volumeTokenB': float(d['volumeTokenB']),
            }
            cdata.append(mapped_data)

        cdata.sort(key=lambda x: x['time'])  # Sort based on timestamps

        return cdata

    except Exception as e:
        print('Error fetching pair data:', e)
        return None

def fetch_on_chain_pair_price(pair, length, token0 = None, token1 = None, reversed= False):
    if not pair:
        return None  # Don't fetch if no pair is selected
    print('Fetching PairData for pair address:', pair['address'])
    print('Fetching PairData for pair:', pair)

    api_url = f"{API_URL}/api/dex/pairTxns/?address={pair['address']}{f'&length={length}' if length else ''}"
    
    try:
        print("fetch_on_chain_pair_price: apiUrl", api_url)
        
        response = requests.get(api_url, **requestOptions)
        response.raise_for_status()  # Raise exception for non-OK responses
        
        data = response.json()
        # print("fetch_on_chain_pair_price response ok", data)

        cdata = []
        for d in data:
            my_date = datetime.strptime(d['timestamp'], '%Y-%m-%dT%H:%M:%SZ')
            price = -1
            if (d['buyToken0'] and pair['tokenA'] == token0['address']) or (d['buyToken0'] == False and pair['tokenB'] == token0['address']):
                if reversed:
                    price = float(d['valueToken1']) / float(d['valueToken0'])
                else:
                    price = float(d['valueToken0']) / float(d['valueToken1'])
            else:
                if reversed:
                    price = float(d['valueToken0']) / float(d['valueToken1'])
                else:
                    price = float(d['valueToken1']) / float(d['valueToken0'])

            mapped_data = {
                'time': my_date,  # Convert the timestamp to a datetime object
                'price': price
            }
            cdata.append(mapped_data)

        cdata.sort(key=lambda x: x['time'])  # Sort based on timestamps

        return cdata

    except Exception as e:
        print('Error fetching pair data:', e)
        return None

def fetch_pair_analyze(selected_pair, time_range, reversed=False, force_update=0):
    if not selected_pair:
        return None  # Don't fetch if no pair is selected
    print('Fetching PairData for pair address:', selected_pair)

    # Check if the data is in the cache and return it
    cache_key = f"{selected_pair}_{time_range}_reversed" if reversed else f"{selected_pair}_{time_range}"
    print("fetch_pair_analyze: cacheKey", cache_key)

    api_url = f"{API_URL}/api/dex/pairAnalyse/?address={selected_pair}{'&forceUpdate=1' if force_update else ''}&timeRange={time_range.lower()}{ '&reversed=true' if reversed else ''}"
    print("fetch_pair_analyze: apiUrl", api_url)
    
    try:
        print("fetch_pair_analyze: apiUrl", api_url)
        
        response = requests.get(api_url, **requestOptions)
        response.raise_for_status()  # Raise exception for non-OK responses
        
        data = response.json()

        return data

    except Exception as e:
        print('Error fetching pair data:', e)
        return None
