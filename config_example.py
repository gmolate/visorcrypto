# Ejemplo de configuración para API keys reales
# Copia este archivo como 'config.py' y reemplaza con tus API keys reales

API_KEYS = {
    "buda": {
        "apiKey": "tu_buda_api_key_aqui",
        "apiSecret": "tu_buda_api_secret_aqui"
    },
    "binance": {
        "apiKey": "tu_binance_api_key_aqui", 
        "apiSecret": "tu_binance_api_secret_aqui"
    },
    "cryptomkt": {
        "apiKey": "tu_cryptomkt_api_key_aqui",
        "apiSecret": "tu_cryptomkt_api_secret_aqui"
    },
    "notbank": {
        "apiKey": "tu_notbank_api_key_aqui",
        "apiSecret": "tu_notbank_api_secret_aqui",
        "userId": "tu_user_id_aqui",
        "accountId": "tu_account_id_aqui"
    }
}

# IMPORTANTE:
# - Asegúrate de que config.py esté en .gitignore para no subir tus API keys
# - Las API keys deben tener permisos de solo lectura
# - Nunca compartas tus API keys
