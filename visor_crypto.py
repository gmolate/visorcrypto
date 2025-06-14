import requests
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
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
from crypto_utils import encrypt_api_keys, decrypt_api_keys

class CryptoViewer(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Visor Crypto")
        self.geometry("800x600")

        self.buda_api_key = None
        self.buda_api_secret = None
        self.binance_api_key = None
        self.binance_api_secret = None
        self.cryptomkt_api_key = None
        self.cryptomkt_api_secret = None

        self.load_encrypted_api_keys()

        self.setup_ui()

        self.api_endpoints = {
            'buda': 'https://www.buda.com/api/v2',
            'binance': 'https://api.binance.com/api/v3',
            'cryptomkt': 'https://api.cryptomkt.com/v3'
        }

    def load_encrypted_api_keys(self):
        if not os.path.exists('api_keys.json'):
            return

        try:
            with open('api_keys.json', 'r') as f:
                encrypted_data = json.load(f)
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Could not read api_keys.json. File might be corrupted.", parent=self)
            return
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read api_keys.json. Error: {str(e)}", parent=self)
            return

        encrypted_hex = encrypted_data.get('encryptedHex')
        iv_hex = encrypted_data.get('ivHex')
        salt_hex = encrypted_data.get('saltHex')

        if not all([encrypted_hex, iv_hex, salt_hex]):
            messagebox.showerror("Error", "api_keys.json is missing required encryption data (encryptedHex, ivHex, or saltHex).", parent=self)
            return

        password = simpledialog.askstring("Master Password", "Enter your password to decrypt API keys:", show='*', parent=self)
        if not password:
            messagebox.showwarning("API Keys Locked", "No password entered. API keys remain locked.", parent=self)
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

            messagebox.showinfo("API Keys Loaded", "API keys successfully decrypted and loaded.", parent=self)

        except Exception as e:
            messagebox.showerror("Decryption Failed", f"Failed to decrypt API keys. Incorrect password or corrupted data. Error: {str(e)}", parent=self)

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

        ttk.Button(api_frame, text="Import Keys", command=self.import_api_keys_file).pack(pady=5, padx=5, side='left')
        ttk.Button(api_frame, text="Export Keys", command=self.export_api_keys_file).pack(pady=5, padx=5, side='left')

        self.balance_frame = ttk.LabelFrame(main_frame, text="Balances")
        self.balance_frame.pack(fill='x', pady=10)

        self.balance_tree = ttk.Treeview(self.balance_frame, columns=('Exchange', 'Currency', 'Amount', 'BTC Value'), show='headings')
        self.balance_tree.heading('Exchange', text='Exchange')
        self.balance_tree.heading('Currency', text='Moneda')
        self.balance_tree.heading('Amount', text='Cantidad')
        self.balance_tree.heading('BTC Value', text='Valor en BTC')
        self.balance_tree.pack(fill='x', pady=5)

        ttk.Button(main_frame, text="Actualizar Balances", command=self.update_balances).pack(pady=10)

        self.total_label = ttk.Label(main_frame, text="Total en BTC: 0.00000000")
        self.total_label.pack(pady=10)

    def setup_api_keys(self, exchange):
        if exchange == 'buda':
            api_key = simpledialog.askstring("Configuración", "Ingrese su API Key de Buda:", parent=self)
            api_secret = simpledialog.askstring("Configuración", "Ingrese su API Secret de Buda:", parent=self)

            if api_key and api_secret:
                self.buda_api_key = api_key
                self.buda_api_secret = api_secret
                self.save_api_keys()
        elif exchange == 'binance':
            api_key = simpledialog.askstring("Configuración", "Ingrese su API Key de Binance:", parent=self)
            api_secret = simpledialog.askstring("Configuración", "Ingrese su API Secret de Binance:", parent=self)

            if api_key and api_secret:
                self.binance_api_key = api_key
                self.binance_api_secret = api_secret
                self.save_api_keys()
        elif exchange == 'cryptomkt':
            api_key = simpledialog.askstring("Configuración", "Ingrese su API Key de CryptoMKT:", parent=self)
            api_secret = simpledialog.askstring("Configuración", "Ingrese su API Secret de CryptoMKT:", parent=self)

            if api_key and api_secret:
                self.cryptomkt_api_key = api_key
                self.cryptomkt_api_secret = api_secret
                self.save_api_keys()

    def save_api_keys(self):
        password = simpledialog.askstring("Master Password", "Enter a password to encrypt your API keys:", show='*', parent=self)

        if not password:
            messagebox.showwarning("Cancelled", "Password not provided. API keys will not be saved.", parent=self)
            return

        api_keys_to_encrypt = {}
        if hasattr(self, 'buda_api_key') and self.buda_api_key and \
           hasattr(self, 'buda_api_secret') and self.buda_api_secret:
            api_keys_to_encrypt["buda"] = {"apiKey": self.buda_api_key, "apiSecret": self.buda_api_secret}

        if hasattr(self, 'binance_api_key') and self.binance_api_key and \
           hasattr(self, 'binance_api_secret') and self.binance_api_secret:
            api_keys_to_encrypt["binance"] = {"apiKey": self.binance_api_key, "apiSecret": self.binance_api_secret}

        if hasattr(self, 'cryptomkt_api_key') and self.cryptomkt_api_key and \
           hasattr(self, 'cryptomkt_api_secret') and self.cryptomkt_api_secret:
            api_keys_to_encrypt["cryptomkt"] = {"apiKey": self.cryptomkt_api_key, "apiSecret": self.cryptomkt_api_secret}

        if not api_keys_to_encrypt:
            messagebox.showinfo("No Keys", "No API keys are configured to save.", parent=self)
            return

        try:
            encrypted_data = encrypt_api_keys(api_keys_to_encrypt, password)
            with open('api_keys.json', 'w') as f:
                json.dump(encrypted_data, f, indent=4)
            messagebox.showinfo("Success", "API keys encrypted and saved to api_keys.json.", parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to encrypt and save API keys. Error: {str(e)}", parent=self)

    def import_api_keys_file(self):
        filepath = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Import API Keys File",
            parent=self
        )

        if not filepath:
            # User cancelled the dialog
            return

        try:
            with open(filepath, 'r') as f:
                imported_data = json.load(f)
        except json.JSONDecodeError:
            messagebox.showerror("Import Error", "Invalid JSON file. Could not decode the file.", parent=self)
            return
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to read the selected file. Error: {str(e)}", parent=self)
            return

        # Validate structure
        if not isinstance(imported_data, dict) or \
           'encryptedHex' not in imported_data or \
           'ivHex' not in imported_data or \
           'saltHex' not in imported_data:
            messagebox.showerror("Import Error", "Invalid file format. The file must contain 'encryptedHex', 'ivHex', and 'saltHex' fields.", parent=self)
            return

        try:
            # Overwrite api_keys.json with the imported data
            with open('api_keys.json', 'w') as f:
                json.dump(imported_data, f, indent=4)

            messagebox.showinfo("Import Successful",
                                f"API keys successfully imported from {filepath}. "
                                "Attempting to load them now.",
                                parent=self)

            # Attempt to load the newly imported keys
            self.load_encrypted_api_keys()

        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to write to api_keys.json. Error: {str(e)}", parent=self)

    def export_api_keys_file(self):
        if not os.path.exists('api_keys.json') or os.path.getsize('api_keys.json') == 0:
            messagebox.showinfo("Export Keys", "No API keys are currently saved to export.", parent=self)
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save API Keys Backup",
            initialfile="crypto_glance_session_backup.json",
            parent=self
        )

        if not filepath:
            return

        try:
            shutil.copyfile('api_keys.json', filepath)
            messagebox.showinfo("Export Successful", f"API keys successfully exported to {filepath}", parent=self)
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export API keys. Error: {str(e)}", parent=self)

    def get_binance_signature(self, params):
        query_string = urllib.parse.urlencode(params)
        signature = hmac.new(
            self.binance_api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature

    def get_binance_balance(self):
        if not self.binance_api_key or not self.binance_api_secret:
            messagebox.showwarning("Advertencia", "Por favor configure primero sus API keys de Binance.", parent=self)
            return {}

        try:
            timestamp = int(time.time() * 1000)
            params = {
                'timestamp': timestamp
            }

            signature = self.get_binance_signature(params)
            params['signature'] = signature

            headers = {
                'X-MBX-APIKEY': self.binance_api_key
            }

            response = requests.get(
                f'{self.api_endpoints["binance"]}/account',
                headers=headers,
                params=params
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    balance['asset']: {
                        'amount': float(balance['free']) + float(balance['locked']),
                        'available': float(balance['free'])
                    }
                    for balance in data['balances']
                    if float(balance['free']) > 0 or float(balance['locked']) > 0
                }
            else:
                messagebox.showerror("Error", f"Error al obtener balances de Binance: {response.text}", parent=self)
                return {}

        except Exception as e:
            messagebox.showerror("Error", f"Error al conectar con Binance: {str(e)}", parent=self)
            return {}

    def get_buda_signature(self, nonce, method, path, body=''):
        message = f'{nonce}{method}{path}{body}'
        signature = hmac.new(
            self.buda_api_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha384
        ).hexdigest()
        return signature

    def get_buda_balance(self):
        if not self.buda_api_key or not self.buda_api_secret:
            messagebox.showwarning("Advertencia", "Por favor configure primero sus API keys de Buda.", parent=self)
            return {}

        try:
            nonce = str(int(time.time() * 1000))
            path = '/api/v2/balances'
            signature = self.get_buda_signature(nonce, 'GET', path)

            headers = {
                'X-SBTC-APIKEY': self.buda_api_key,
                'X-SBTC-NONCE': nonce,
                'X-SBTC-SIGNATURE': signature
            }

            response = requests.get(
                f'{self.api_endpoints["buda"]}/balances',
                headers=headers
            )

            if response.status_code == 200:
                balances = response.json()['balances']
                return {
                    balance['currency']: {
                        'amount': float(balance['amount'][0]),
                        'available': float(balance['available'][0])
                    }
                    for balance in balances
                    if float(balance['amount'][0]) > 0
                }
            else:
                messagebox.showerror("Error", f"Error al obtener balances: {response.text}", parent=self)
                return {}

        except Exception as e:
            messagebox.showerror("Error", f"Error al conectar con Buda: {str(e)}", parent=self)
            return {}

    def get_cryptomkt_signature(self, timestamp, method, endpoint, body=''):
        message = f'{timestamp}{method}{endpoint}{body}'
        signature = hmac.new(
            self.cryptomkt_api_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha384
        ).hexdigest()
        return signature

    def get_cryptomkt_balance(self):
        if not self.cryptomkt_api_key or not self.cryptomkt_api_secret:
            messagebox.showwarning("Advertencia", "Por favor configure primero sus API keys de CryptoMKT.", parent=self)
            return {}

        try:
            timestamp = str(int(time.time() * 1000))
            method = 'GET'
            endpoint = '/balance'

            signature = self.get_cryptomkt_signature(timestamp, method, endpoint)

            headers = {
                'X-MKT-APIKEY': self.cryptomkt_api_key,
                'X-MKT-TIMESTAMP': timestamp,
                'X-MKT-SIGNATURE': signature
            }

            response = requests.get(
                f'{self.api_endpoints["cryptomkt"]}/balance',
                headers=headers
            )

            if response.status_code == 200:
                data = response.json()
                balances = data.get('data', [])
                return {
                    balance['currency']: {
                        'amount': float(balance['available']) + float(balance['locked']),
                        'available': float(balance['available'])
                    }
                    for balance in balances
                    if float(balance['available']) > 0 or float(balance['locked']) > 0
                }
            else:
                messagebox.showerror("Error", f"Error al obtener balances de CryptoMKT: {response.text}", parent=self)
                return {}

        except Exception as e:
            messagebox.showerror("Error", f"Error al conectar con CryptoMKT: {str(e)}", parent=self)
            return {}

    def update_balances(self):
        for item in self.balance_tree.get_children():
            self.balance_tree.delete(item)

        total_btc = 0

        if self.buda_api_key and self.buda_api_secret:
            buda_balances = self.get_buda_balance()
            for currency, balance in buda_balances.items():
                amount = balance['amount']
                btc_value = amount
                if currency == 'BTC':
                    btc_value = amount
                    total_btc += amount

                self.balance_tree.insert('', 'end', values=(
                    'Buda',
                    currency,
                    f"{amount:.8f}",
                    f"{btc_value:.8f}"
                ))

        if self.binance_api_key and self.binance_api_secret:
            binance_balances = self.get_binance_balance()
            for currency, balance in binance_balances.items():
                amount = balance['amount']
                btc_value = amount
                if currency == 'BTC':
                    btc_value = amount
                    total_btc += amount

                self.balance_tree.insert('', 'end', values=(
                    'Binance',
                    currency,
                    f"{amount:.8f}",
                    f"{btc_value:.8f}"
                ))

        if self.cryptomkt_api_key and self.cryptomkt_api_secret:
            cryptomkt_balances = self.get_cryptomkt_balance()
            for currency, balance in cryptomkt_balances.items():
                amount = balance['amount']
                btc_value = amount
                if currency == 'BTC':
                    btc_value = amount
                    total_btc += amount

                self.balance_tree.insert('', 'end', values=(
                    'CryptoMKT',
                    currency,
                    f"{amount:.8f}",
                    f"{btc_value:.8f}"
                ))

        self.total_label.config(text=f"Total en BTC: {total_btc:.8f}")

if __name__ == "__main__":
    app = CryptoViewer()
    app.mainloop()
