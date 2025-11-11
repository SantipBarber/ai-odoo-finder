import os
import sys

# Añadir el directorio backend al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.app.database import init_db


if __name__ == "__main__":
    print("🔧 Inicializando base de datos...")
    init_db()
    print("✅ ¡Base de datos lista!")

