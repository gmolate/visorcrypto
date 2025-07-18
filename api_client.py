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

def get_cryptomkt_balance(api_key, api_secret):
    if not api_key or not api_secret:
        print("CryptoMKT: API key o secret no proporcionados")
        return None
    
    # Si es una API key mock, retornar datos de prueba
    if api_key == "cryptomkt_key" or api_secret == "cryptomkt_secret":
        print("CryptoMKT: Usando datos mock para prueba")
        return {"BTC": 0.05678901, "ETH": 0.78901234, "CLP": 25000.0}
        
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
        
        print(f"CryptoMKT: Realizando petición a {API_ENDPOINTS['cryptomkt']}{path}")
        response = requests.get(f'{API_ENDPOINTS["cryptomkt"]}{path}', headers=headers)
        print(f"CryptoMKT: Status code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"CryptoMKT: Error HTTP {response.status_code}: {response.text}")
            return None
            
        response.raise_for_status()
        data = response.json()
        print(f"CryptoMKT: Respuesta recibida: {data}")
        
        balances = data.get('data', [])
        result = {
            balance['id'].upper(): float(balance['available']) + float(balance['reserved'])
            for balance in balances
            if float(balance['available']) > 0 or float(balance['reserved']) > 0
        }
        print(f"CryptoMKT: Balances procesados: {len(result)} monedas con balance > 0")
        return result
    except Exception as e:
        error_details = str(e)
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_details = e.response.json().get('error', {}).get('message', e.response.text)
            except json.JSONDecodeError:
                error_details = e.response.text
        print(f"Error connecting to CryptoMKT: {error_details}")
        print(f"CryptoMKT: Detalles del error: {str(e)}")
        return None

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
