import requests
import time
import hmac
import hashlib
import json
from notbank_python_sdk.notbank_client import NotbankClient
from notbank_python_sdk.requests_models import *
from notbank_python_sdk.client_connection_factory import new_rest_client_connection
from notbank_python_sdk.error import NotbankException

API_ENDPOINTS = {
    'buda': 'https://www.buda.com',
    'binance': 'https://api.binance.com',
    'notbank': 'https://api.notbank.exchange'
}

def get_binance_balance(api_key, api_secret):
    if not api_key or not api_secret:
        print("Binance: API key o secret no proporcionados")
        return None
    
    # Si es una API key mock, retornar datos de prueba
    if api_key == "binance_key" or api_secret == "binance_secret":
        print("Binance: Usando datos mock para prueba")
        return {"BTC": 0.12345678, "ETH": 2.34567891, "BNB": 10.5, "USDT": 1000.0}
        
    try:
        timestamp = int(time.time() * 1000)
        query_string = f'timestamp={timestamp}'
        signature = hmac.new(api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
        headers = {'X-MBX-APIKEY': api_key}
        
        print(f"Binance: Realizando petición a {API_ENDPOINTS['binance']}/api/v3/account")
        response = requests.get(f'{API_ENDPOINTS["binance"]}/api/v3/account', headers=headers, params={'timestamp': timestamp, 'signature': signature})
        print(f"Binance: Status code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Binance: Error HTTP {response.status_code}: {response.text}")
            return None
            
        response.raise_for_status()
        data = response.json()
        
        result = {b['asset']: float(b['free']) + float(b['locked']) for b in data['balances'] if float(b['free']) > 0 or float(b['locked']) > 0}
        print(f"Binance: Balances procesados: {len(result)} monedas con balance > 0")
        return result
    except Exception as e:
        print(f"Error connecting to Binance: {e}")
        print(f"Binance: Detalles del error: {str(e)}")
        return None

def get_buda_balance(api_key, api_secret):
    if not api_key or not api_secret:
        print("Buda: API key o secret no proporcionados")
        return None
    
    # Si es una API key mock, retornar datos de prueba
    if api_key == "buda_key" or api_secret == "buda_secret":
        print("Buda: Usando datos mock para prueba")
        return {"BTC": 0.01234567, "ETH": 1.23456789, "CLP": 50000.0}
        
    try:
        nonce = str(int(time.time() * 1000000))  # Microsegundos según documentación de Buda
        path = '/api/v2/balances'
        text_to_sign = f"GET {path} {nonce}"
        signature = hmac.new(api_secret.encode('utf-8'), text_to_sign.encode('utf-8'), hashlib.sha384).hexdigest()
        headers = {
            'X-SBTC-APIKEY': api_key, 
            'X-SBTC-NONCE': nonce, 
            'X-SBTC-SIGNATURE': signature,
            'Content-Type': 'application/json'
        }
        
        print(f"Buda: Realizando petición a {API_ENDPOINTS['buda']}{path}")
        print(f"Buda: Nonce: {nonce}")
        print(f"Buda: String to sign: {text_to_sign}")
        
        response = requests.get(f'{API_ENDPOINTS["buda"]}{path}', headers=headers)
        print(f"Buda: Status code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Buda: Error HTTP {response.status_code}: {response.text}")
            return None
            
        response.raise_for_status()
        data = response.json()
        print(f"Buda: Respuesta recibida: {data}")
        
        balances = data['balances']
        result = {b['id']: float(b['amount'][0]) for b in balances if float(b['amount'][0]) > 0}
        print(f"Buda: Balances procesados: {result}")
        return result
    except Exception as e:
        print(f"Error connecting to Buda: {e}")
        print(f"Buda: Detalles del error: {str(e)}")
        return None

def get_notbank_balance(api_key, api_secret, user_id, account_id):
    if not all([api_key, api_secret, user_id, account_id]):
        print("NotBank: API key, secret, user_id, or account_id not provided")
        return None

    if api_key == "notbank_key" and api_secret == "notbank_secret":
        print("NotBank: Using mock data for testing")
        return {"BTC": 0.05678901, "ETH": 0.78901234, "CLP": 25000.0}

    client = None
    try:
        rest_connection = new_rest_client_connection()
        client = NotbankClient(rest_connection)
        
        authenticate = client.authenticate(
            AuthenticateRequest(
                api_public_key=api_key,
                api_secret_key=api_secret,
                user_id=int(user_id),
            )
        )
        if not authenticate.authenticated:
            raise Exception("Authentication failed")

        positions = client.get_account_positions(GetAccountPositionsRequest(account_id=int(account_id)))
        
        result = {
            pos.product_symbol: pos.amount
            for pos in positions
            if pos.amount > 0
        }
        print(f"NotBank: Processed balances: {len(result)} coins with balance > 0")
        return result
    except NotbankException as e:
        print(f"Error connecting to NotBank: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred with NotBank: {e}")
        return None
    finally:
        if client:
            client.close()

def get_prices_from_binance():
    try:
        url = f"{API_ENDPOINTS['binance']}/api/v3/ticker/price"
        print(f"Binance: Obteniendo precios desde {url}")
        response = requests.get(url)
        print(f"Binance: Status code para precios: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Binance: Error al obtener precios HTTP {response.status_code}: {response.text}")
            return {}
            
        response.raise_for_status()
        prices_data = response.json()
        result = {item['symbol']: float(item['price']) for item in prices_data}
        print(f"Binance: Precios obtenidos para {len(result)} pares")
        return result
    except requests.exceptions.RequestException as e:
        print(f"Could not get prices from Binance: {e}")
        return {}
    except Exception as e:
        print(f"Error processing prices from Binance: {str(e)}")
        return {}
