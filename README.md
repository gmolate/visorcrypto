# Visor Crypto

¡Échale un ojo a tus cryptos con Visor Crypto! Esta aplicación de escritorio te ayuda a cachar al tiro cómo van tus inversiones en criptomonedas a través de varios exchanges populares:

- Buda
- Binance
- CryptoMKT

## Características

- Mira tus saldos actualizados al instante.
- Conéctate a varios exchanges sin atados.
- Calcula el total de tu portafolio en BTC.
- Una interfaz clarita y fácil de usar.
- Guarda tus API keys de forma segura en tu equipo.

## Requisitos

- Python 3.x
- Bibliotecas requeridas:
  - requests
  - python-dotenv
  - tkinter (incluido en Python)

## Instalación

¡Manos a la obra! Sigue estos pasos para tener Visor Crypto funcionando:

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

Para que la magia ocurra, necesitas tus API keys. ¡Ojo! Te recomendamos que sean con permisos de solo lectura, pa' mayor seguridad.

1. Obtener API keys de los exchanges que desees usar (busca las que sean de "solo lectura" o "read-only"):
   - [Buda](https://www.buda.com/api)
   - [Binance](https://www.binance.com/en/my/settings/api-management)
   - [CryptoMKT](https://www.cryptomkt.com/es/cuenta/api)

2. En la aplicación, usa los botones de "Configurar [Exchange]" para ingresar tus API keys. Se guardarán en tu computador.

## Seguridad

¡Cuida tus API Keys como hueso de santo! Aquí unos consejos pa' que no tengas dramas:

- Las API keys se guardan en tu computador, en un archivo `.env`. ¡No lo compartas con nadie!
- Usa siempre API keys con permisos de **solo lectura**. En serio, es clave pa' tu seguridad.
- Nunca, pero nunca, compartas tus claves API. El que comparte, pierde (y harto).

## Contribuir

¿Tienes ideas bacanes para mejorar Visor Crypto? ¡Genial! Abre un 'issue' y cuéntanos qué se te ocurre. ¡Toda ayuda es bienvenida!
