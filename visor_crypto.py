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
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
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

from api_client import get_buda_balance, get_binance_balance, get_cryptomkt_balance, get_prices_from_binance

class CryptoViewer(ThemedTk):
    def __init__(self):
        super().__init__(theme="equilux")  # Tema oscuro

        self.title("Visor Crypto")
        self.geometry("1024x768")
        self.configure(bg='#1A1A1A')

        # Estilo para los widgets
        style = ttk.Style(self)
        style.theme_use("equilux")
        style.configure("Treeview",
                        background="#2A2D30",
                        foreground="white",
                        fieldbackground="#2A2D30",
                        rowheight=25)
        style.map('Treeview', background=[('selected', '#1A1A1A')])
        style.configure("Treeview.Heading",
                        background="#1A1A1A",
                        foreground="white",
                        font=('Helvetica', 10, 'bold'))
        style.configure("TLabel",
                        background='#1A1A1A',
                        foreground='white',
                        font=('Helvetica', 12))
        style.configure("TLabelframe",
                        background='#1A1A1A',
                        foreground='white',
                        labelmargins= (10, 5))
        style.configure("TLabelframe.Label",
                        background='#1A1A1A',
                        foreground='white',
                        font=('Helvetica', 12, 'bold'))
        style.configure("TButton",
                        background='#3498DB',
                        foreground='white',
                        font=('Helvetica', 10, 'bold'),
                        padding=5)
        style.map("TButton",
                  background=[('active', '#2980B9')])

        self.buda_api_key = None
        self.buda_api_secret = None
        self.binance_api_key = None
        self.binance_api_secret = None
        self.cryptomkt_api_key = None
        self.cryptomkt_api_secret = None

        self.load_encrypted_api_keys()

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
        main_frame = ttk.Frame(self, style="TFrame")
        main_frame.pack(padx=20, pady=20, fill='both', expand=True)

        # --- Menú ---
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        api_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Configuración", menu=api_menu)
        api_menu.add_command(label="Configurar Buda", command=lambda: self.setup_api_keys('buda'))
        api_menu.add_command(label="Configurar Binance", command=lambda: self.setup_api_keys('binance'))
        api_menu.add_command(label="Configurar CryptoMKT", command=lambda: self.setup_api_keys('cryptomkt'))
        api_menu.add_separator()
        api_menu.add_command(label="Importar Keys", command=self.import_api_keys_file)
        api_menu.add_command(label="Exportar Keys", command=self.export_api_keys_file)

        title_label = ttk.Label(main_frame, text="Visor de Portafolio Crypto", font=("Helvetica", 20, 'bold'))
        title_label.pack(pady=20)

        self.total_portfolio_value_label = ttk.Label(main_frame, text="Valor Total Estimado del Portafolio (USD): $0.00", font=("Helvetica", 16))
        self.total_portfolio_value_label.pack(pady=(0, 20))

        # --- Balances por Exchange ---
        self.balance_frame = ttk.LabelFrame(main_frame, text="Balances por Exchange")
        self.balance_frame.pack(fill='both', expand=True, pady=10)

        self.balance_tree = ttk.Treeview(self.balance_frame, columns=('Exchange', 'Moneda', 'Cantidad', 'Acciones'), show='headings')
        self.balance_tree.heading('Exchange', text='Exchange')
        self.balance_tree.heading('Moneda', text='Moneda')
        self.balance_tree.heading('Cantidad', text='Cantidad')
        self.balance_tree.heading('Acciones', text='')
        self.balance_tree.pack(fill='both', expand=True, pady=5)
        self.balance_tree.bind('<ButtonRelease-1>', self.on_tree_click)

        # --- Saldos Acumulados ---
        self.total_balance_frame = ttk.LabelFrame(main_frame, text="Saldos Acumulados Totales")
        self.total_balance_frame.pack(fill='both', expand=True, pady=10)

        self.total_balance_tree = ttk.Treeview(self.total_balance_frame, columns=('Moneda', 'Cantidad Total'), show='headings')
        self.total_balance_tree.heading('Moneda', text='Moneda')
        self.total_balance_tree.heading('Cantidad Total', text='Cantidad Total')
        self.total_balance_tree.pack(fill='both', expand=True, pady=5)

        ttk.Button(main_frame, text="Actualizar Balances", command=self.update_balances).pack(pady=20)

    def on_tree_click(self, event):
        region = self.balance_tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.balance_tree.identify_column(event.x)
            if column == '#4':  # Columna "Acciones"
                item_id = self.balance_tree.identify_row(event.y)
                item_values = self.balance_tree.item(item_id, 'values')
                currency = item_values[1]
                self.show_chart(currency)

    def show_chart(self, currency):
        symbol = f"{currency.upper()}USDT"
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1d&limit=30"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            chart_window = tk.Toplevel(self)
            chart_window.title(f"Gráfico de {currency}")
            chart_window.geometry("800x600")

            fig = Figure(figsize=(8, 6), dpi=100)
            plot = fig.add_subplot(1, 1, 1)

            prices = [float(item[4]) for item in data]
            timestamps = [datetime.fromtimestamp(item[0] / 1000) for item in data]

            plot.plot(timestamps, prices, marker='o', linestyle='-')
            plot.set_title(f"Precio de {currency} (Últimos 30 días)")
            plot.set_xlabel("Fecha")
            plot.set_ylabel("Precio (USD)")
            fig.autofmt_xdate()

            canvas = FigureCanvasTkAgg(fig, master=chart_window)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"No se pudieron obtener los datos del gráfico: {e}", parent=self)

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

    def update_balances(self):
        for item in self.balance_tree.get_children():
            self.balance_tree.delete(item)
        for item in self.total_balance_tree.get_children():
            self.total_balance_tree.delete(item)

        total_portfolio = {}

        def add_to_total_portfolio(balances, exchange_name):
            for currency, data in balances.items():
                amount = data if isinstance(data, (float, int)) else data.get('amount', 0)
                currency_code = currency.split('-')[0].upper()

                if amount > 0:
                    self.balance_tree.insert('', 'end', values=(exchange_name, currency_code, f"{amount:.8f}", "Ver Gráfico"))
                    total_portfolio[currency_code] = total_portfolio.get(currency_code, 0) + amount

        if self.buda_api_key:
            buda_balances = get_buda_balance(self.buda_api_key, self.buda_api_secret)
            add_to_total_portfolio(buda_balances, 'Buda')

        if self.binance_api_key:
            binance_balances = get_binance_balance(self.binance_api_key, self.binance_api_secret)
            add_to_total_portfolio(binance_balances, 'Binance')

        if self.cryptomkt_api_key:
            cryptomkt_balances = get_cryptomkt_balance(self.cryptomkt_api_key, self.cryptomkt_api_secret)
            add_to_total_portfolio(cryptomkt_balances, 'CryptoMKT')

        prices_usd = get_prices_from_binance()
        total_portfolio_usd_value = 0

        for currency, total_amount in sorted(total_portfolio.items()):
            if total_amount > 0:
                self.total_balance_tree.insert('', 'end', values=(currency, f"{total_amount:.8f}"))

                price_symbol_usdt = f"{currency}USDT"
                price_symbol_busd = f"{currency}BUSD"

                price = prices_usd.get(price_symbol_usdt)
                if price is None:
                    price = prices_usd.get(price_symbol_busd)

                if price:
                    total_portfolio_usd_value += total_amount * price

        self.total_portfolio_value_label.config(text=f"Valor Total Estimado del Portafolio (USD): ${total_portfolio_usd_value:,.2f}")

if __name__ == "__main__":
    app = CryptoViewer()
    app.mainloop()
