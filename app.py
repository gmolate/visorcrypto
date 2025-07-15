from flask import Flask, render_template, jsonify
from api_client import get_buda_balance, get_binance_balance, get_cryptomkt_balance, get_prices_from_binance
import json

app = Flask(__name__)

# Mock API keys for now
# In a real application, these would be stored securely
MOCK_API_KEYS = {
    "buda": {"apiKey": "buda_key", "apiSecret": "buda_secret"},
    "binance": {"apiKey": "binance_key", "apiSecret": "binance_secret"},
    "cryptomkt": {"apiKey": "cryptomkt_key", "apiSecret": "cryptomkt_secret"}
}

@app.route('/')
def index():
    buda_balances = get_buda_balance(MOCK_API_KEYS['buda']['apiKey'], MOCK_API_KEYS['buda']['apiSecret'])
    binance_balances = get_binance_balance(MOCK_API_KEYS['binance']['apiKey'], MOCK_API_KEYS['binance']['apiSecret'])
    cryptomkt_balances = get_cryptomkt_balance(MOCK_API_KEYS['cryptomkt']['apiKey'], MOCK_API_KEYS['cryptomkt']['apiSecret'])

    all_balances = {
        'Buda': buda_balances,
        'Binance': binance_balances,
        'CryptoMKT': cryptomkt_balances
    }

    prices_usd = get_prices_from_binance()

    total_portfolio = {}
    for exchange, balances in all_balances.items():
        for currency, amount in balances.items():
            currency_code = currency.split('-')[0].upper()
            total_portfolio[currency_code] = total_portfolio.get(currency_code, 0) + amount

    total_portfolio_usd_value = 0
    for currency, total_amount in total_portfolio.items():
        price_symbol_usdt = f"{currency}USDT"
        price_symbol_busd = f"{currency}BUSD"
        price = prices_usd.get(price_symbol_usdt)
        if price is None:
            price = prices_usd.get(price_symbol_busd)
        if price:
            total_portfolio_usd_value += total_amount * price

    return render_template('index.html',
                           all_balances=all_balances,
                           total_portfolio=total_portfolio,
                           total_portfolio_usd_value=total_portfolio_usd_value,
                           prices_usd=prices_usd)

@app.route('/api/historical_data/<symbol>')
def historical_data(symbol):
    # Binance API endpoint for historical klines (candlestick data)
    # We will get daily data for the last 30 days
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol.upper()}USDT&interval=1d&limit=30"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        # Format data for Chart.js
        # [ [timestamp, open, high, low, close, volume, ...], ... ]
        # We only need timestamp and close price
        formatted_data = {
            'labels': [item[0] for item in data],
            'datasets': [{
                'label': f'{symbol.upper()} Price (USD)',
                'data': [float(item[4]) for item in data],
                'borderColor': '#3498DB',
                'tension': 0.1
            }]
        }
        return jsonify(formatted_data)
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
