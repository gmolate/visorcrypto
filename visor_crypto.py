import requests
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from ttkthemes import ThemedTk
import json
from datetime import datetime
import hmac
import hashlib
import time
import base64
import os
import shutil
from tkinter import simpledialog
import urllib.parse
# Asumiendo que tienes este archivo con las funciones de encriptación
# from crypto_utils import encrypt_api_keys, decrypt_api_keys

# --- Bloque de crypto_utils.py (simulado si no lo tienes) ---
# Para que el script se pueda ejecutar, si no tienes el archivo crypto_utils.py,
# puedes usar este bloque. Si ya lo tienes, puedes eliminarlo.
def encrypt_api_keys(data, password):
    # Implementación de marcador de posición
    print("Simulando encriptación...")
    return {"encryptedHex": "encrypted_data_placeholder", "ivHex": "iv_placeholder", "saltHex": "salt_placeholder"}

def decrypt_api_keys(encrypted_hex, iv_hex, salt_hex, password):
    # Implementación de marcador de posición
    print("Simulando desencriptación...")
    # Devuelve claves de prueba si la contraseña es 'password'
    if password == 'password':
        return {
            "buda": {"apiKey": "buda_key", "apiSecret": "buda_secret"},
            "binance": {"apiKey": "binance_key", "apiSecret": "binance_secret"},
            "cryptomkt": {"apiKey": "cryptomkt_key", "apiSecret": "cryptomkt_secret"}
        }
    raise Exception("Contraseña incorrecta o datos corruptos")
# --- Fin del bloque simulado ---


class CryptoViewer(ThemedTk):
    def __init__(self):
        super().__init__(theme="arc") # Puedes probar otros temas como "plastik", "adapta", etc.

        self.title("Visor Crypto")
        self.geometry("800x600")

        self.buda_api_key = None
        self.buda_api_secret = None
        self.binance_api_key = None
        self.binance_api_secret = None
        self.cryptomkt_api_key = None
        self.cryptomkt_api_secret = None

        self.load_encrypted_api_keys()

        # =========================================================================
        # CORRECCIÓN 1: Actualizar el endpoint de CryptoMKT a la URL correcta
        # =========================================================================
        self.api_endpoints = {
            'buda': 'https://www.buda.com', # Base URL para Buda
            'binance': 'https://api.binance.com', # Base URL para Binance
            'cryptomkt': 'https://api.exchange.cryptomkt.com' # URL correcta para CryptoMKT
        }
        # =========================================================================

        self.setup_ui()


    def load_encrypted_api_keys(self):
        if not os.path.exists('api_keys.json'):
            return

        try:
            with open('api_keys.json', 'r') as f:
                encrypted_data = json.load(f)
        except json.JSONDecodeError:
            messagebox.showerror("Error", "No se pudo leer api_keys.json. El archivo podría estar corrupto.", parent=self)
            return
        except Exception as e:
            messagebox.showerror("Error", f"Fallo al leer api_keys.json. Error: {str(e)}", parent=self)
            return

        encrypted_hex = encrypted_data.get('encryptedHex')
        iv_hex = encrypted_data.get('ivHex')
        salt_hex = encrypted_data.get('saltHex')

        if not all([encrypted_hex, iv_hex, salt_hex]):
            messagebox.showerror("Error", "api_keys.json no contiene los datos de encriptación requeridos (encryptedHex, ivHex, o saltHex).", parent=self)
            return

        password = simpledialog.askstring("Contraseña Maestra", "Ingrese su contraseña para desencriptar las API keys:", show='*', parent=self)
        if not password:
            messagebox.showwarning("API Keys Bloqueadas", "No se ingresó contraseña. Las API keys permanecen bloqueadas.", parent=self)
            return

        try:
            decrypted_keys = decrypt_api_keys(encrypted_hex, iv_hex, salt_hex, password)

            buda_keys = decrypted_keys.get('buda', {})
            self.buda_api_key = buda_keys.get('apiKey')
            self.buda_api_secret = buda_keys.get('apiSecret')

            binance_keys = decrypted_keys.get('binance', {})
            self.binance_api_key = binance_keys.get('apiKey')
            self.binance_api_secret = binance_keys.get('apiSecret')

            cryptomkt_keys = decrypted_keys.get('cryptomkt', {})
            self.cryptomkt_api_key = cryptomkt_keys.get('apiKey')
            self.cryptomkt_api_secret = cryptomkt_keys.get('apiSecret')

            messagebox.showinfo("API Keys Cargadas", "API keys desencriptadas y cargadas exitosamente.", parent=self)

        except Exception as e:
            messagebox.showerror("Fallo en Desencriptación", f"No se pudieron desencriptar las API keys. Contraseña incorrecta o datos corruptos. Error: {str(e)}", parent=self)

    def setup_ui(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(padx=20, pady=20, fill='both', expand=True)

        title_label = ttk.Label(main_frame, text="Visor de Portafolio Crypto", font=("Helvetica", 16))
        title_label.pack(pady=10)

        api_frame = ttk.LabelFrame(main_frame, text="Configuración API")
        api_frame.pack(fill='x', pady=10)

        ttk.Button(api_frame, text="Configurar Buda", command=lambda: self.setup_api_keys('buda')).pack(pady=5, padx=5, side='left')
        ttk.Button(api_frame, text="Configurar Binance", command=lambda: self.setup_api_keys('binance')).pack(pady=5, padx=5, side='left')
        ttk.Button(api_frame, text="Configurar CryptoMKT", command=lambda: self.setup_api_keys('cryptomkt')).pack(pady=5, padx=5, side='left')

        ttk.Button(api_frame, text="Importar Keys", command=self.import_api_keys_file).pack(pady=5, padx=5, side='left')
        ttk.Button(api_frame, text="Exportar Keys", command=self.export_api_keys_file).pack(pady=5, padx=5, side='left')

        self.balance_frame = ttk.LabelFrame(main_frame, text="Balances")
        self.balance_frame.pack(fill='x', pady=10)

        self.balance_tree = ttk.Treeview(self.balance_frame, columns=('Exchange', 'Moneda', 'Cantidad'), show='headings')
        self.balance_tree.heading('Exchange', text='Exchange')
        self.balance_tree.heading('Moneda', text='Moneda')
        self.balance_tree.heading('Cantidad', text='Cantidad')
        self.balance_tree.pack(fill='both', expand=True, pady=5)

        # Frame para saldos acumulados
        self.total_balance_frame = ttk.LabelFrame(main_frame, text="Saldos Acumulados Totales")
        self.total_balance_frame.pack(fill='x', pady=10)

        self.total_balance_tree = ttk.Treeview(self.total_balance_frame, columns=('Moneda', 'Cantidad Total'), show='headings')
        self.total_balance_tree.heading('Moneda', text='Moneda')
        self.total_balance_tree.heading('Cantidad Total', text='Cantidad Total')
        self.total_balance_tree.pack(fill='both', expand=True, pady=5)

        # Label para el valor total del portafolio en USD
        self.total_portfolio_value_label = ttk.Label(main_frame, text="Valor Total Estimado del Portafolio (USD): $0.00", font=("Helvetica", 12))
        self.total_portfolio_value_label.pack(pady=(5,10))

        ttk.Button(main_frame, text="Actualizar Balances", command=self.update_balances).pack(pady=10)

    def setup_api_keys(self, exchange):
        api_key = simpledialog.askstring("Configuración", f"Ingrese su API Key de {exchange.capitalize()}:", parent=self)
        api_secret = simpledialog.askstring("Configuración", f"Ingrese su API Secret de {exchange.capitalize()}:", parent=self, show='*')

        if api_key and api_secret:
            if exchange == 'buda':
                self.buda_api_key = api_key
                self.buda_api_secret = api_secret
            elif exchange == 'binance':
                self.binance_api_key = api_key
                self.binance_api_secret = api_secret
            elif exchange == 'cryptomkt':
                self.cryptomkt_api_key = api_key
                self.cryptomkt_api_secret = api_secret
            self.save_api_keys()

    def save_api_keys(self):
        password = simpledialog.askstring("Contraseña Maestra", "Ingrese una contraseña para encriptar sus API keys:", show='*', parent=self)

        if not password:
            messagebox.showwarning("Cancelado", "No se proveyó contraseña. Las API keys no serán guardadas.", parent=self)
            return

        api_keys_to_encrypt = {}
        if self.buda_api_key and self.buda_api_secret:
            api_keys_to_encrypt["buda"] = {"apiKey": self.buda_api_key, "apiSecret": self.buda_api_secret}

        if self.binance_api_key and self.binance_api_secret:
            api_keys_to_encrypt["binance"] = {"apiKey": self.binance_api_key, "apiSecret": self.binance_api_secret}

        if self.cryptomkt_api_key and self.cryptomkt_api_secret:
            api_keys_to_encrypt["cryptomkt"] = {"apiKey": self.cryptomkt_api_key, "apiSecret": self.cryptomkt_api_secret}

        if not api_keys_to_encrypt:
            messagebox.showinfo("Sin Keys", "No hay API keys configuradas para guardar.", parent=self)
            return

        try:
            encrypted_data = encrypt_api_keys(api_keys_to_encrypt, password)
            with open('api_keys.json', 'w') as f:
                json.dump(encrypted_data, f, indent=4)
            messagebox.showinfo("Éxito", "API keys encriptadas y guardadas en api_keys.json.", parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"Fallo al encriptar y guardar las API keys. Error: {str(e)}", parent=self)

    def import_api_keys_file(self):
        filepath = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")], title="Importar Archivo de API Keys", parent=self)
        if not filepath: return
        try:
            with open(filepath, 'r') as f:
                imported_data = json.load(f)
            if not all(k in imported_data for k in ['encryptedHex', 'ivHex', 'saltHex']):
                messagebox.showerror("Error de Importación", "Formato de archivo inválido.", parent=self)
                return
            with open('api_keys.json', 'w') as f:
                json.dump(imported_data, f, indent=4)
            messagebox.showinfo("Éxito", "API keys importadas. Intentando cargarlas ahora.", parent=self)
            self.load_encrypted_api_keys()
        except Exception as e:
            messagebox.showerror("Error de Importación", f"Fallo al importar el archivo. Error: {str(e)}", parent=self)

    def export_api_keys_file(self):
        if not os.path.exists('api_keys.json'):
            messagebox.showinfo("Exportar Keys", "No hay API keys guardadas para exportar.", parent=self)
            return
        filepath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")], title="Guardar Backup de API Keys", initialfile="crypto_viewer_backup.json", parent=self)
        if not filepath: return
        try:
            shutil.copyfile('api_keys.json', filepath)
            messagebox.showinfo("Éxito", f"API keys exportadas a {filepath}", parent=self)
        except Exception as e:
            messagebox.showerror("Error de Exportación", f"Fallo al exportar las keys. Error: {str(e)}", parent=self)
    
    # --- Métodos de API de Binance ---
    def get_binance_balance(self):
        if not self.binance_api_key or not self.binance_api_secret:
            messagebox.showwarning("Advertencia", "Por favor configure primero sus API keys de Binance.", parent=self)
            return {}
        try:
            timestamp = int(time.time() * 1000)
            query_string = f'timestamp={timestamp}'
            signature = hmac.new(self.binance_api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
            headers = {'X-MBX-APIKEY': self.binance_api_key}
            response = requests.get(f'{self.api_endpoints["binance"]}/api/v3/account', headers=headers, params={'timestamp': timestamp, 'signature': signature})
            response.raise_for_status()
            data = response.json()
            return {b['asset']: float(b['free']) + float(b['locked']) for b in data['balances'] if float(b['free']) > 0 or float(b['locked']) > 0}
        except Exception as e:
            messagebox.showerror("Error", f"Error al conectar con Binance: {e}", parent=self)
            return {}
            
    # --- Métodos de API de Buda ---
    def get_buda_balance(self):
        if not self.buda_api_key or not self.buda_api_secret:
            messagebox.showwarning("Advertencia", "Por favor configure primero sus API keys de Buda.", parent=self)
            return {}
        try:
            nonce = str(int(time.time() * 1000))
            path = '/api/v2/balances'
            text_to_sign = f"GET {path} {nonce}"
            signature = hmac.new(self.buda_api_secret.encode('utf-8'), text_to_sign.encode('utf-8'), hashlib.sha384).hexdigest()
            headers = {'X-SBTC-APIKEY': self.buda_api_key, 'X-SBTC-NONCE': nonce, 'X-SBTC-SIGNATURE': signature}
            response = requests.get(f'{self.api_endpoints["buda"]}{path}', headers=headers)
            response.raise_for_status()
            balances = response.json()['balances']
            return {b['id']: float(b['amount'][0]) for b in balances if float(b['amount'][0]) > 0}
        except Exception as e:
            messagebox.showerror("Error", f"Error al conectar con Buda: {e}", parent=self)
            return {}

    # --- Métodos de API de CryptoMKT ---
    # =========================================================================
    # CORRECCIÓN 2: Lógica completamente corregida para CryptoMKT
    # =========================================================================
    def get_cryptomkt_balance(self):
        if not self.cryptomkt_api_key or not self.cryptomkt_api_secret:
            messagebox.showwarning("Advertencia", "Por favor configure primero sus API keys de CryptoMKT.", parent=self)
            return {}

        try:
            # El path correcto del endpoint
            path = '/api/3/wallet/balances'
            timestamp = str(int(time.time()))
            
            # El mensaje a firmar es: timestamp + path
            message = timestamp + path
            
            # El algoritmo de firma es SHA256
            signature = hmac.new(
                self.cryptomkt_api_secret.encode('utf-8'),
                msg=message.encode('utf-8'),
                digestmod=hashlib.sha256
            ).hexdigest()

            headers = {
                'X-MKT-APIKEY': self.cryptomkt_api_key,
                'X-MKT-TIMESTAMP': timestamp,
                'X-MKT-SIGNATURE': signature
            }

            response = requests.get(f'{self.api_endpoints["cryptomkt"]}{path}', headers=headers)
            response.raise_for_status()
            
            data = response.json()
            balances = data.get('data', [])
            return {
                balance['id'].upper(): float(balance['available']) + float(balance['reserved'])
                for balance in balances
                if float(balance['available']) > 0 or float(balance['reserved']) > 0
            }

        except Exception as e:
            # Captura detalles del error para mostrar un mensaje más útil
            error_details = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_details = e.response.json().get('error', {}).get('message', e.response.text)
                except json.JSONDecodeError:
                    error_details = e.response.text
            messagebox.showerror("Error", f"Error al conectar con CryptoMKT: {error_details}", parent=self)
            return {}
    # =========================================================================
    
    def update_balances(self):
        # Limpiar vistas previas
        for item in self.balance_tree.get_children():
            self.balance_tree.delete(item)
        for item in self.total_balance_tree.get_children():
            self.total_balance_tree.delete(item)

        total_portfolio = {} # Diccionario para acumular los saldos: {'BTC': 0.5, 'ETH': 10}

        # Función auxiliar para agregar al portafolio total
        def add_to_total_portfolio(balances, exchange_name):
            for currency, data in balances.items():
                # Aseguramos que 'amount' exista, si no, asumimos que 'data' es directamente el monto
                amount = data if isinstance(data, (float, int)) else data.get('amount', 0)

                # Normalizar nombres de criptomonedas (ej. BTC-CLP -> BTC)
                currency_code = currency.split('-')[0].upper()

                if amount > 0:
                    self.balance_tree.insert('', 'end', values=(exchange_name, currency_code, f"{amount:.8f}"))
                    total_portfolio[currency_code] = total_portfolio.get(currency_code, 0) + amount

        # Buda
        if self.buda_api_key:
            buda_balances = self.get_buda_balance() # { 'BTC': amount, 'ETH': amount }
            add_to_total_portfolio(buda_balances, 'Buda')

        # Binance
        if self.binance_api_key:
            binance_balances = self.get_binance_balance() # { 'BTC': amount, 'USDT': amount }
            add_to_total_portfolio(binance_balances, 'Binance')

        # CryptoMKT
        # La función get_cryptomkt_balance ya devuelve {'CURRENCY': amount}
        if self.cryptomkt_api_key:
            cryptomkt_balances = self.get_cryptomkt_balance()
            add_to_total_portfolio(cryptomkt_balances, 'CryptoMKT')

        # Obtener precios de Binance para calcular el valor en USD
        prices_usd = self.get_prices_from_binance() # {'BTCUSDT': 60000.0, 'ETHUSDT': 3000.0}

        total_portfolio_usd_value = 0

        # Poblar la tabla de saldos acumulados y calcular valor en USD
        for currency, total_amount in total_portfolio.items():
            if total_amount > 0: # Solo mostrar si hay saldo
                self.total_balance_tree.insert('', 'end', values=(currency, f"{total_amount:.8f}"))

                # Intentar encontrar el precio para la moneda (ej. BTCUSDT, ETHUSDT)
                # Binance usa el par con USDT, ej. BTCUSDT
                price_symbol_usdt = f"{currency}USDT"
                price_symbol_busd = f"{currency}BUSD" # Algunas pueden estar en BUSD

                price = prices_usd.get(price_symbol_usdt)
                if price is None: # Si no se encuentra con USDT, intentar con BUSD
                    price = prices_usd.get(price_symbol_busd)

                if price:
                    total_portfolio_usd_value += total_amount * price

        self.total_portfolio_value_label.config(text=f"Valor Total Estimado del Portafolio (USD): ${total_portfolio_usd_value:,.2f}")

    def get_prices_from_binance(self):
        """Obtiene los precios de todos los tickers de Binance en formato {symbol: price}."""
        try:
            url = f"{self.api_endpoints['binance']}/api/v3/ticker/price"
            response = requests.get(url)
            response.raise_for_status()
            prices_data = response.json() # Lista de diccionarios: [{'symbol': 'BTCUSDT', 'price': '60000.00'}, ...]

            # Convertir la lista de diccionarios a un solo diccionario {symbol: price}
            # y asegurarse de que el precio sea float
            return {item['symbol']: float(item['price']) for item in prices_data}
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error de Precios", f"No se pudieron obtener los precios de Binance: {e}", parent=self)
            return {}
        except Exception as e:
            messagebox.showerror("Error de Precios", f"Error procesando precios de Binance: {str(e)}", parent=self)
            return {}

if __name__ == "__main__":
    app = CryptoViewer()
    app.mainloop()
