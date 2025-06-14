# Visor Crypto

Una aplicación de escritorio para visualizar tus balances de criptomonedas en diferentes exchanges:

- Buda
- Binance
- CryptoMKT

## Características

- Visualización de balances en tiempo real
- Soporte para múltiples exchanges
- Conversión de valores a BTC
- Interfaz gráfica intuitiva
- Almacenamiento seguro de API keys

## Requisitos

- Python 3.x
- Bibliotecas requeridas:
  - requests
  - python-dotenv
  - tkinter (incluido en Python)

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/TU_USUARIO/visor-crypto.git
cd visor-crypto
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Ejecutar la aplicación:
```bash
python visor_crypto.py
```

## Configuración

1. Obtener API keys de los exchanges que desees usar:
   - [Buda](https://www.buda.com/api)
   - [Binance](https://www.binance.com/en/my/settings/api-management)
   - [CryptoMKT](https://www.cryptomkt.com/es/cuenta/api)

2. En la aplicación, usar los botones de configuración para cada exchange y agregar las API keys.

## Seguridad

- Las API keys se almacenan localmente en un archivo `.env`
- Se recomienda usar API keys con permisos de solo lectura
- Nunca compartas tus API keys

## Contribuir

Las contribuciones son bienvenidas. Por favor, abre un issue para discutir los cambios que te gustaría hacer.
