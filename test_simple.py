#!/usr/bin/env python
"""
Script simple para probar la aplicación
"""

print("🚀 Probando aplicación...")

try:
    import app
    print("✅ App importada correctamente")
    print(f"✅ Exchanges configurados: {list(app.API_KEYS.keys())}")
    
    # Probar función NotBank
    from api_client import get_notbank_balance
    
    # Con datos mock
    balance = get_notbank_balance("notbank_key", "notbank_secret", "123", "456")
    if balance:
        print(f"✅ NotBank funciona: {len(balance)} monedas")
        print(f"   Ejemplo: BTC={balance.get('BTC', 0)}, USD={balance.get('USD', 0)}")
    
    print("✅ ¡Aplicación lista!")
    print("✅ Ejecuta: .venv\\Scripts\\python.exe app.py")
    print("✅ Luego abre: http://localhost:5001")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
