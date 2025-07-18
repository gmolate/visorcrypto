# Crypto Visor

Visor de criptomonedas con soporte para Buda, Binance y CryptoMKT.

## Descripción

Este proyecto consta de dos aplicaciones:

1.  **Aplicación de Escritorio:** Una aplicación de escritorio creada con Python y Tkinter que te permite ver los balances de tus cuentas en diferentes exchanges de criptomonedas.
2.  **Aplicación Web:** una versión web creada con Flask que muestra la misma información en tu navegador.

Ambas aplicaciones te permiten:

*   Ver los balances de tus cuentas de Buda, Binance y CryptoMKT.
*   Ver un resumen total de tu portafolio.
*   Ver gráficos con el histórico de precios de los últimos 30 días para cada criptomoneda.

## Requisitos

*   Python 3.6+
*   Dependencias de Python listadas en `requirements.txt`.

## Instalación

1.  Clona este repositorio:
    ```bash
    git clone https://github.com/tu-usuario/crypto-visor.git
    ```
2.  Navega al directorio del proyecto:
    ```bash
    cd crypto-visor
    ```
3.  Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    ```

## Uso

### Aplicación de Escritorio

Para ejecutar la aplicación de escritorio, corre el siguiente comando:

```bash
python visor_crypto.py
```

La primera vez que ejecutes la aplicación, necesitarás configurar tus API keys. Puedes hacerlo desde el menú `Configuración`.

### Aplicación Web

Para ejecutar la aplicación web, corre el siguiente comando:

```bash
python app.py
```

La aplicación web estará disponible en `http://127.0.0.1:5001`.

**Nota:** La aplicación web utiliza API keys de prueba por defecto. Para utilizar tus propias API keys, deberás modificarlas en el archivo `app.py`.
