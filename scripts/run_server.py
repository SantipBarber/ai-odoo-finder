import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import uvicorn
from backend.app.main import app

if __name__ == "__main__":
    print("="*70)
    print("🚀 AI-OdooFinder API")
    print("="*70)
    print("\n📍 Endpoints disponibles:")
    print("   - http://localhost:8989/docs (Swagger UI)")
    print("   - http://localhost:8989/redoc (ReDoc)")
    print("   - http://localhost:8989/health (Health Check)")
    print("   - http://localhost:8989/search (Búsqueda)")
    print("   - http://localhost:8989/stats (Estadísticas)")
    print("\n⚡ Servidor corriendo...\n")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8989,
        log_level="info"
    )
