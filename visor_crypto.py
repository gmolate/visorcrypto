import requests
import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime
import hmac
import hashlib
import time
import base64
from dotenv import load_dotenv
import os
from tkinter import simpledialog
import urllib.parse

class CryptoViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Visor Crypto")
        self.geometry("800x600")
        
        # Cargar configuración
        load_dotenv()
        self.buda_api_key = os.getenv('BUDA_API_KEY')
        self.buda_api_secret = os.getenv('BUDA_API_SECRET')
        self.binance_api_key = os.getenv('BINANCE_API_KEY')
        self.binance_api_secret = os.getenv('BINANCE_API_SECRET')
        self.cryptomkt_api_key = os.getenv('CRYPTOMKT_API_KEY')
        self.cryptomkt_api_secret = os.getenv('CRYPTOMKT_API_SECRET')
        
        # Configuración de la interfaz
        self.setup_ui()
        
        # APIs endpoints
        self.api_endpoints = {
            'buda': 'https://www.buda.com/api/v2',
            'binance': 'https://api.binance.com/api/v3',
            'cryptomkt': 'https://api.cryptomkt.com/v3'
        }
        
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(padx=20, pady=20, fill='both', expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, text="Visor de Portafolio Crypto", font=("Helvetica", 16))
        title_label.pack(pady=10)
        
        # Frame para configuración de API
        api_frame = ttk.LabelFrame(main_frame, text="Configuración API")
        api_frame.pack(fill='x', pady=10)
        
        # Botones de configuración por exchange
        ttk.Button(api_frame, text="Configurar Buda", command=lambda: self.setup_api_keys('buda')).pack(pady=5, padx=5, side='left')
        ttk.Button(api_frame, text="Configurar Binance", command=lambda: self.setup_api_keys('binance')).pack(pady=5, padx=5, side='left')
        ttk.Button(api_frame, text="Configurar CryptoMKT", command=lambda: self.setup_api_keys('cryptomkt')).pack(pady=5, padx=5, side='left')
        
        # Frame para los balances
        self.balance_frame = ttk.LabelFrame(main_frame, text="Balances")
        self.balance_frame.pack(fill='x', pady=10)
        
        # Lista para mostrar los balances
        self.balance_tree = ttk.Treeview(self.balance_frame, columns=('Exchange', 'Currency', 'Amount', 'BTC Value'), show='headings')
        self.balance_tree.heading('Exchange', text='Exchange')
        self.balance_tree.heading('Currency', text='Moneda')
        self.balance_tree.heading('Amount', text='Cantidad')
        self.balance_tree.heading('BTC Value', text='Valor en BTC')
        self.balance_tree.pack(fill='x', pady=5)
        
        # Botones para actualizar
        ttk.Button(main_frame, text="Actualizar Balances", command=self.update_balances).pack(pady=10)
        
        # Área para mostrar el total
        self.total_label = ttk.Label(main_frame, text="Total en BTC: 0.00000000")
        self.total_label.pack(pady=10)
    
    def setup_api_keys(self, exchange):
        """Configura las API keys del exchange especificado"""
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
        """Guarda todas las API keys en el archivo .env"""
        with open('.env', 'w') as f:
            if self.buda_api_key and self.buda_api_secret:
                f.write(f'BUDA_API_KEY={self.buda_api_key}\n')
                f.write(f'BUDA_API_SECRET={self.buda_api_secret}\n')
            if self.binance_api_key and self.binance_api_secret:
                f.write(f'BINANCE_API_KEY={self.binance_api_key}\n')
                f.write(f'BINANCE_API_SECRET={self.binance_api_secret}\n')
            if self.cryptomkt_api_key and self.cryptomkt_api_secret:
                f.write(f'CRYPTOMKT_API_KEY={self.cryptomkt_api_key}\n')
                f.write(f'CRYPTOMKT_API_SECRET={self.cryptomkt_api_secret}\n')
        messagebox.showinfo("Éxito", "Las API keys han sido guardadas correctamente.")

    def get_binance_signature(self, params):
        """Genera la firma para la autenticación con Binance"""
        query_string = urllib.parse.urlencode(params)
        signature = hmac.new(
            self.binance_api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature

    def get_binance_balance(self):
        """Obtiene los balances de Binance"""
        if not self.binance_api_key or not self.binance_api_secret:
            messagebox.showwarning("Advertencia", "Por favor configure primero sus API keys de Binance.")
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
                messagebox.showerror("Error", f"Error al obtener balances de Binance: {response.text}")
                return {}
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al conectar con Binance: {str(e)}")
            return {}

    def get_buda_signature(self, nonce, method, path, body=''):
        """Genera la firma para la autenticación con Buda"""
        message = f'{nonce}{method}{path}{body}'
        signature = hmac.new(
            self.buda_api_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha384
        ).hexdigest()
        return signature

    def get_buda_balance(self):
        """Obtiene los balances de Buda"""
        if not self.buda_api_key or not self.buda_api_secret:
            messagebox.showwarning("Advertencia", "Por favor configure primero sus API keys de Buda.")
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
                messagebox.showerror("Error", f"Error al obtener balances: {response.text}")
                return {}
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al conectar con Buda: {str(e)}")
            return {}

    def get_cryptomkt_signature(self, timestamp, method, endpoint, body=''):
        """Genera la firma para la autenticación con CryptoMKT"""
        message = f'{timestamp}{method}{endpoint}{body}'
        signature = hmac.new(
            self.cryptomkt_api_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha384
        ).hexdigest()
        return signature

    def get_cryptomkt_balance(self):
        """Obtiene los balances de CryptoMKT"""
        if not self.cryptomkt_api_key or not self.cryptomkt_api_secret:
            messagebox.showwarning("Advertencia", "Por favor configure primero sus API keys de CryptoMKT.")
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
                messagebox.showerror("Error", f"Error al obtener balances de CryptoMKT: {response.text}")
                return {}
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al conectar con CryptoMKT: {str(e)}")
            return {}

    def update_balances(self):
        """Actualiza los balances de todas las exchanges"""
        # Limpiar tabla actual
        for item in self.balance_tree.get_children():
            self.balance_tree.delete(item)
            
        total_btc = 0
        
        # Obtener y mostrar balances de Buda
        buda_balances = self.get_buda_balance()
        for currency, balance in buda_balances.items():
            amount = balance['amount']
            btc_value = amount  # TODO: Implementar conversión a BTC
            if currency == 'BTC':
                btc_value = amount
                total_btc += amount
            
            self.balance_tree.insert('', 'end', values=(
                'Buda',
                currency,
                f"{amount:.8f}",
                f"{btc_value:.8f}"
            ))
            
        # Obtener y mostrar balances de Binance
        binance_balances = self.get_binance_balance()
        for currency, balance in binance_balances.items():
            amount = balance['amount']
            btc_value = amount  # TODO: Implementar conversión a BTC
            if currency == 'BTC':
                btc_value = amount
                total_btc += amount
            
            self.balance_tree.insert('', 'end', values=(
                'Binance',
                currency,
                f"{amount:.8f}",
                f"{btc_value:.8f}"
            ))
            
        # Obtener y mostrar balances de CryptoMKT
        cryptomkt_balances = self.get_cryptomkt_balance()
        for currency, balance in cryptomkt_balances.items():
            amount = balance['amount']
            btc_value = amount  # TODO: Implementar conversión a BTC
            if currency == 'BTC':
                btc_value = amount
                total_btc += amount
            
            self.balance_tree.insert('', 'end', values=(
                'CryptoMKT',
                currency,
                f"{amount:.8f}",
                f"{btc_value:.8f}"
            ))
        
        # Actualizar total
        self.total_label.config(text=f"Total en BTC: {total_btc:.8f}")

if __name__ == "__main__":
    app = CryptoViewer()
    app.mainloop()
