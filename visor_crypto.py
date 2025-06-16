import os
import time
import hmac
import hashlib
import requests
import json
from dotenv import load_dotenv
from tkinter import Tk, Label, Button, Frame, messagebox, font

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# --- Funciones para obtener balances de cada exchange ---

def get_buda_balances():
    """
    Obtiene los balances de la cuenta en Buda.com.
    """
    # --- Credenciales de Buda.com ---
    API_KEY = os.getenv("BUDA_API_KEY")
    API_SECRET = os.getenv("BUDA_SECRET_KEY")

    if not API_KEY or not API_SECRET:
        return "Error: Credenciales de Buda.com no configuradas."

    # --- Endpoint para obtener balances ---
    BASE_URL = "https://www.buda.com"
    BALANCES_PATH = "/api/v2/balances"

    try:
        # 1. Generar Nonce
        nonce = str(int(time.time() * 1000))

        # 2. Preparar el string para firmar (para una solicitud GET)
        text_to_sign = f"GET {BALANCES_PATH} {nonce}"

        # 3. Generar la firma con HMAC-SHA384
        signature = hmac.new(
            API_SECRET.encode('utf-8'),
            text_to_sign.encode('utf-8'),
            hashlib.sha384
        ).hexdigest()

        # 4. Preparar los headers de la solicitud
        headers = {
            "X-SBTC-APIKEY": API_KEY,
            "X-SBTC-NONCE": nonce,
            "X-SBTC-SIGNATURE": signature,
        }

        # 5. Realizar la solicitud GET
        response = requests.get(BASE_URL + BALANCES_PATH, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        formatted_balances = ""
        for balance in data['balances']:
            if float(balance['amount'][0]) > 0:
                formatted_balances += f"{balance['id']}: {balance['amount'][0]}\n"
        return formatted_balances.strip() if formatted_balances else "No hay balances con fondos en Buda.com."

    except requests.exceptions.RequestException as e:
        error_message = f"Error al obtener balances de Buda.com: {e}"
        if e.response:
            error_message += f" - {e.response.text}"
        return error_message

def get_cryptomkt_balances():
    """
    Obtiene los balances de la cuenta en CryptoMKT.
    """
    # --- Credenciales de CryptoMKT ---
    API_KEY = os.getenv("CRYPTO_MKT_API_KEY")
    API_SECRET = os.getenv("CRYPTO_MKT_SECRET_KEY")

    if not API_KEY or not API_SECRET:
        return "Error: Credenciales de CryptoMKT no configuradas."

    # =========================================================================
    # AQUÍ ESTÁ LA CORRECCIÓN PARA SOLUCIONAR EL ERROR 404
    # =========================================================================
    BASE_URL = "https://api.exchange.cryptomkt.com"  # <-- CORREGIDO
    BALANCES_PATH = "/api/3/wallet/balances"        # <-- CORREGIDO
    
    # El código antiguo que causaba el error era:
    # BASE_URL = "https://api.cryptomkt.com/v1/"
    # BALANCES_PATH = "balances"
    # =========================================================================

    try:
        # El timestamp es necesario para la firma
        timestamp = str(int(time.time()))
        
        # El cuerpo de la solicitud GET está vacío, el path y el timestamp forman el mensaje
        message = timestamp + BALANCES_PATH
        
        # Generar la firma con HMAC-SHA256
        signature = hmac.new(
            API_SECRET.encode('utf-8'),
            msg=message.encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()

        # Preparar los headers
        headers = {
            'X-MKT-APIKEY': API_KEY,
            'X-MKT-SIGNATURE': signature,
            'X-MKT-TIMESTAMP': timestamp
        }

        # Realizar la solicitud GET
        response = requests.get(BASE_URL + BALANCES_PATH, headers=headers)
        response.raise_for_status()

        data = response.json()
        
        # La documentación indica que el resultado puede no ser 'data' directamente
        # Es mejor verificar la estructura del JSON que retorna la API
        balances_list = data.get('data', []) # Asumiendo que los balances están en una llave 'data'
        if not isinstance(balances_list, list): # Si la respuesta no es una lista
             return f"Respuesta inesperada de CryptoMKT: {data}"

        formatted_balances = ""
        for balance in balances_list:
            # Filtra para mostrar solo balances con fondos disponibles
            if float(balance.get('available', 0)) > 0:
                currency = balance.get('id', 'N/A')
                amount = balance.get('available', '0')
                formatted_balances += f"{currency}: {amount}\n"
        
        return formatted_balances.strip() if formatted_balances else "No hay balances con fondos en CryptoMKT."

    except requests.exceptions.RequestException as e:
        error_message = f"Error al obtener balances de CryptoMKT: {e}"
        if e.response:
            error_message += f" - {e.response.text}"
        return error_message

# --- Lógica de la Interfaz Gráfica (Tkinter) ---

class CryptoVisor:
    def __init__(self, root):
        self.root = root
        self.root.title("Visor de Criptomonedas")
        self.root.geometry("400x300")
        self.root.configure(bg='#2E2E2E')

        # Definir fuentes
        self.title_font = font.Font(family="Helvetica", size=16, weight="bold")
        self.label_font = font.Font(family="Helvetica", size=12)
        self.button_font = font.Font(family="Helvetica", size=12, weight="bold")

        # Frame principal
        main_frame = Frame(root, bg='#2E2E2E', padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')
        
        # Título
        title_label = Label(main_frame, text="Balances de Exchanges", font=self.title_font, bg='#2E2E2E', fg='white')
        title_label.pack(pady=(0, 20))

        # Botones para cada exchange
        self.create_exchange_button(main_frame, "Obtener Balances de Buda.com", self.show_buda_balances)
        self.create_exchange_button(main_frame, "Obtener Balances de CryptoMKT", self.show_cryptomkt_balances)
        
    def create_exchange_button(self, parent, text, command):
        button = Button(parent, text=text, command=command, font=self.button_font, bg='#4A4A4A', fg='white', relief='flat', padx=10, pady=5)
        button.pack(pady=10, fill='x')

    def show_balances(self, exchange_name, balance_func):
        try:
            balances = balance_func()
            messagebox.showinfo(f"Balances de {exchange_name}", balances)
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error inesperado en {exchange_name}: {e}")

    def show_buda_balances(self):
        self.show_balances("Buda.com", get_buda_balances)

    def show_cryptomkt_balances(self):
        self.show_balances("CryptoMKT", get_cryptomkt_balances)


if __name__ == "__main__":
    root = Tk()
    app = CryptoVisor(root)
    root.mainloop()
