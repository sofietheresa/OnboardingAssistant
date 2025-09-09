#!/usr/bin/env python3
"""
Server-Start-Script für Boardy Onboarding Assistant
"""

import uvicorn
from server import app

if __name__ == "__main__":
    print("🚀 Starte Boardy Onboarding Assistant Server...")
    print("📡 Server läuft auf: http://127.0.0.1:8000")
    print("📝 Frontend verfügbar auf: http://127.0.0.1:8000")
    print("🔧 API-Dokumentation: http://127.0.0.1:8000/docs")
    print("⏹️  Zum Beenden: Ctrl+C")
    print("-" * 50)
    
    uvicorn.run(
        app, 
        host="127.0.0.1", 
        port=8000, 
        log_level="info",
        reload=False
    )
