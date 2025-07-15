import requests
import time
import hmac
import hashlib
import json

API_ENDPOINTS = {
    'buda': 'https://www.buda.com',
    'binance': 'https://api.binance.com',
    'cryptomkt': 'https://api.exchange.cryptomkt.com'
}

def get_binance_balance(api_key, api_secret):
    if not api_key or not api_secret:
        return None
    try:
        timestamp = int(time.time() * 1000)
        query_string = f'timestamp={timestamp}'
        signature = hmac.new(api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
        headers = {'X-MBX-APIKEY': api_key}
        response = requests.get(f'{API_ENDPOINTS["binance"]}/api/v3/account', headers=headers, params={'timestamp': timestamp, 'signature': signature})
        response.raise_for_status()
        data = response.json()
        return {b['asset']: float(b['free']) + float(b['locked']) for b in data['balances'] if float(b['free']) > 0 or float(b['locked']) > 0}
    except Exception as e:
        print(f"Error connecting to Binance: {e}")
        return None

def get_buda_balance(api_key, api_secret):
    if not api_key or not api_secret:
        return None
    try:
        nonce = str(int(time.time() * 1000))
        path = '/api/v2/balances'
        text_to_sign = f"GET {path} {nonce}"
        signature = hmac.new(api_secret.encode('utf-8'), text_to_sign.encode('utf-8'), hashlib.sha384).hexdigest()
        headers = {'X-SBTC-APIKEY': api_key, 'X-SBTC-NONCE': nonce, 'X-SBTC-SIGNATURE': signature}
        response = requests.get(f'{API_ENDPOINTS["buda"]}{path}', headers=headers)
        response.raise_for_status()
        balances = response.json()['balances']
        return {b['id']: float(b['amount'][0]) for b in balances if float(b['amount'][0]) > 0}
    except Exception as e:
        print(f"Error connecting to Buda: {e}")
        return None

def get_cryptomkt_balance(api_key, api_secret):
    if not api_key or not api_secret:
        return None
    try:
        path = '/api/3/wallet/balances'
        timestamp = str(int(time.time()))
        message = timestamp + path
        signature = hmac.new(
            api_secret.encode('utf-8'),
            msg=message.encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()
        headers = {
            'X-MKT-APIKEY': api_key,
            'X-MKT-TIMESTAMP': timestamp,
            'X-MKT-SIGNATURE': signature
        }
        response = requests.get(f'{API_ENDPOINTS["cryptomkt"]}{path}', headers=headers)
        response.raise_for_status()
        data = response.json()
        balances = data.get('data', [])
        return {
            balance['id'].upper(): float(balance['available']) + float(balance['reserved'])
            for balance in balances
            if float(balance['available']) > 0 or float(balance['reserved']) > 0
        }
    except Exception as e:
        error_details = str(e)
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_details = e.response.json().get('error', {}).get('message', e.response.text)
            except json.JSONDecodeError:
                error_details = e.response.text
        print(f"Error connecting to CryptoMKT: {error_details}")
        return None

def get_prices_from_binance():
    try:
        url = f"{API_ENDPOINTS['binance']}/api/v3/ticker/price"
        response = requests.get(url)
        response.raise_for_status()
        prices_data = response.json()
        return {item['symbol']: float(item['price']) for item in prices_data}
    except requests.exceptions.RequestException as e:
        print(f"Could not get prices from Binance: {e}")
        return {}
    except Exception as e:
        print(f"Error processing prices from Binance: {str(e)}")
        return {}
