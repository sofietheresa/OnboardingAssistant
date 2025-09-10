# 🚀 Boardy - IBM Onboarding Assistant

Ein intelligenter Chatbot-Assistent für das IBM Onboarding, der Mitarbeitern hilft, sich an verschiedenen Standorten zurechtzufinden. Das Frontend ist mit einem auf IBM Cloud Code Engine deployed Backend verbunden.

## 📁 Projektstruktur

```
watsonx-chat-starter/
├── 📁 backend/                 # Python FastAPI Backend
│   ├── 📁 app/                # Backend-Anwendung
│   │   ├── config.py          # Konfiguration & Settings
│   │   ├── db.py              # Datenbank-Verbindung
│   │   ├── llm.py             # LLM-Integration
│   │   ├── rag.py             # RAG-System
│   │   ├── security.py        # Sicherheits-Features
│   │   └── schemas.py         # Pydantic-Modelle
│   ├── 📁 ingest/             # Dokumenten-Ingestion
│   ├── 📁 routes/             # API-Routen
│   ├── server.py              # FastAPI-Server
│   ├── Dockerfile             # Container-Konfiguration
│   ├── requirements.txt       # Python-Abhängigkeiten
│   └── env.example            # Umgebungsvariablen-Vorlage
├── 📁 frontend/               # React TypeScript Frontend
│   ├── 📁 src/
│   │   ├── 📁 components/     # React-Komponenten
│   │   │   ├── ChatScreen.tsx # Chat-Interface
│   │   │   └── OnboardingScreen.tsx # Standort-Auswahl
│   │   ├── 📁 types/          # TypeScript-Typen
│   │   ├── 📁 styles/         # CSS-Styles
│   │   ├── App.tsx            # Hauptkomponente
│   │   ├── main.tsx           # Einstiegspunkt
│   │   └── vite-env.d.ts      # Vite-Typen
│   ├── 📁 public/             # Statische Assets
│   ├── 📁 build/              # Produktions-Build
│   ├── package.json           # Node.js-Abhängigkeiten
│   └── vite.config.ts         # Vite-Konfiguration
├── 📁 scripts/                # Start-Skripte
├── 📁 onboarding_docs/        # Onboarding-Dokumente
├── podman-compose.yml         # Container-Orchestrierung
├── litellm-config.yaml        # LiteLLM-Konfiguration
└── README.md                  # Diese Datei
```

## 🚀 Schnellstart - Frontend mit Backend verbinden

### Voraussetzungen
- [Node.js](https://nodejs.org/) (Version 18+)
- [Git](https://git-scm.com/) installiert
- IBM Cloud Account (für Backend-Deployment)

### 1. Repository klonen
```bash
git clone <repository-url>
cd watsonx-chat-starter
```

### 2. Frontend-Abhängigkeiten installieren
```bash
cd frontend
npm install
```

### 3. Frontend starten (Entwicklung)
```bash
# Im frontend/ Verzeichnis
npm run dev
```

Das Frontend läuft dann auf: **http://localhost:5173**

## 🔗 Backend-Verbindung konfigurieren

### Option A: Mit deployed Backend (Empfohlen)
Das Frontend ist bereits für die Verbindung mit dem deployed Backend konfiguriert:
- **Backend-URL**: `https://boardy-app.1zt0zkzab8pz.eu-de.codeengine.appdomain.cloud`
- **API-Endpoints**: `/v1/ask` (Chat), `/api/locations` (Standorte)

### Option B: Lokales Backend
Falls Sie ein lokales Backend verwenden möchten:

1. **Backend-URL ändern** in `frontend/vite.config.ts`:
```typescript
define: {
  'import.meta.env.VITE_API_BASE_URL': JSON.stringify('http://localhost:8080')
}
```

2. **Backend starten**:
```bash
cd backend
pip install -r requirements.txt
python server.py
```

## 🛠️ Detaillierte Setup-Anleitung

### Schritt 1: Frontend-Setup

#### Windows (PowerShell/CMD):
```powershell
# 1. Repository klonen
git clone <repository-url>
cd watsonx-chat-starter

# 2. Frontend-Abhängigkeiten installieren
cd frontend
npm install

# 3. Frontend starten
npm run dev
```

#### Linux/macOS (Bash):
```bash
# 1. Repository klonen
git clone <repository-url>
cd watsonx-chat-starter

# 2. Frontend-Abhängigkeiten installieren
cd frontend
npm install

# 3. Frontend starten
npm run dev
```

### Schritt 2: Backend-Verbindung testen

#### Windows (PowerShell):
```powershell
# Backend-Health-Check
Invoke-WebRequest -Uri "https://boardy-app.1zt0zkzab8pz.eu-de.codeengine.appdomain.cloud/healthz" -Method GET

# Locations-Endpoint testen
Invoke-WebRequest -Uri "https://boardy-app.1zt0zkzab8pz.eu-de.codeengine.appdomain.cloud/api/locations" -Method GET

# Chat-Endpoint testen
$body = '{"query":"Hallo"}'
Invoke-WebRequest -Uri "https://boardy-app.1zt0zkzab8pz.eu-de.codeengine.appdomain.cloud/v1/ask" -Method POST -Body $body -ContentType "application/json"
```

#### Linux/macOS (Bash):
```bash
# Backend-Health-Check
curl https://boardy-app.1zt0zkzab8pz.eu-de.codeengine.appdomain.cloud/healthz

# Locations-Endpoint testen
curl https://boardy-app.1zt0zkzab8pz.eu-de.codeengine.appdomain.cloud/api/locations

# Chat-Endpoint testen
curl -X POST https://boardy-app.1zt0zkzab8pz.eu-de.codeengine.appdomain.cloud/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"query":"Hallo"}'
```

### Schritt 3: Frontend-Build für Produktion

#### Windows (PowerShell):
```powershell
# Im frontend/ Verzeichnis
cd frontend
npm run build

# Build-Ordner wird in frontend/build/ erstellt
# Dieser kann auf jeden Webserver deployed werden
```

#### Linux/macOS (Bash):
```bash
# Im frontend/ Verzeichnis
cd frontend
npm run build

# Build-Ordner wird in frontend/build/ erstellt
# Dieser kann auf jeden Webserver deployed werden
```

## 🌐 Zugriff

- **Entwicklung**: http://localhost:5173 (Frontend mit Hot Reload)
- **Backend-API**: https://boardy-app.1zt0zkzab8pz.eu-de.codeengine.appdomain.cloud
- **Produktion**: Frontend-Build kann auf jeden Webserver deployed werden

## 🛠️ Entwicklung

### Frontend
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite (schnell, Hot Reload)
- **Styling**: CSS mit CSS-Variablen
- **Struktur**: Komponenten-basiert mit getrennten Types
- **Bundle-Optimierung**: Code-Splitting, ESBuild-Minifizierung

### Backend
- **Framework**: FastAPI (Python)
- **AI**: Watson X + RAG-System
- **Deployment**: IBM Cloud Code Engine
- **Datenbank**: PostgreSQL mit SSL

### Hot Reload
Das Frontend lädt automatisch neu, wenn du Dateien änderst. Keine manuellen Browser-Refreshs nötig!

## 🚀 Setup-Skripte

### Windows (PowerShell/CMD)
```bash
# Automatisches Setup und Start
setup-frontend.bat
```

### Linux/macOS (Bash)
```bash
# Automatisches Setup und Start
./setup-frontend.sh
```

### Manuelles Setup
```bash
# 1. Frontend-Abhängigkeiten installieren
cd frontend
npm install

# 2. Frontend starten
npm run dev

# 3. Browser öffnen: http://localhost:5173
```

## 📝 Features

- 🎯 **Standortauswahl**: IBM Böblingen, München, UDG Ludwigsburg
- 💬 **Intelligenter Chat**: Watson X + RAG-System Integration
- 🎨 **Moderne UI**: Responsive Design mit optimierter Performance
- 🔄 **Hot Reload**: Sofortige Änderungen sichtbar
- 🚀 **Optimiert**: Code-Splitting, Bundle-Optimierung
- 🌐 **Cloud-Ready**: Backend auf IBM Cloud Code Engine deployed
- 📱 **Mobile-First**: Responsive Design für alle Geräte

## 🧪 Tests

### Backend-API testen
```bash
# Health-Check
curl https://boardy-app.1zt0zkzab8pz.eu-de.codeengine.appdomain.cloud/healthz

# Locations testen
curl https://boardy-app.1zt0zkzab8pz.eu-de.codeengine.appdomain.cloud/api/locations

# Chat testen
curl -X POST https://boardy-app.1zt0zkzab8pz.eu-de.codeengine.appdomain.cloud/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"query":"Wie beantrage ich Urlaub?"}'
```

### Frontend testen
```bash
# Frontend starten
cd frontend
npm run dev

# Browser öffnen: http://localhost:5173
# Standort auswählen und Chat testen
```

## 📦 Deployment

### Frontend-Build erstellen
```bash
cd frontend
npm run build

# Build-Ordner: frontend/build/
# Kann auf jeden Webserver deployed werden
```

### Backend bereits deployed
- **URL**: https://boardy-app.1zt0zkzab8pz.eu-de.codeengine.appdomain.cloud
- **Status**: Produktiv und verfügbar
- **CORS**: Für Frontend-Domain konfiguriert

## 🤝 Beitragen

1. Fork erstellen
2. Feature-Branch: `git checkout -b feature/amazing-feature`
3. Commits: `git commit -m 'Add amazing feature'`
4. Push: `git push origin feature/amazing-feature`
5. Pull Request erstellen

## 📄 Lizenz

Dieses Projekt ist Teil des IBM Onboarding-Programms.

## 🆘 Support & Troubleshooting

### Häufige Probleme

#### Frontend startet nicht
```bash
# Node.js-Version prüfen (mindestens 18+)
node --version

# Dependencies neu installieren
cd frontend
rm -rf node_modules package-lock.json
npm install
```

#### Backend-Verbindung fehlgeschlagen
```bash
# Backend-Status prüfen
curl https://boardy-app.1zt0zkzab8pz.eu-de.codeengine.appdomain.cloud/healthz

# CORS-Probleme: Browser-DevTools → Network-Tab prüfen
```

#### Build-Fehler
```bash
# TypeScript-Fehler beheben
cd frontend
npm run build

# Bei Terser-Fehlern: Vite-Konfiguration prüfen
```

### Logs überprüfen
- **Frontend**: Browser-DevTools → Console
- **Backend**: IBM Cloud Console → Code Engine → Logs
- **Build**: Terminal-Ausgabe bei `npm run build`

### Support-Kontakt
1. Issues auf GitHub erstellen
2. Logs sammeln und anhängen
3. Fehlerbeschreibung mit Schritten zur Reproduktion

---

**Entwickelt mit ❤️ für IBM Mitarbeiter**

## 📊 Performance-Metriken

- **Bundle-Größe**: ~150KB (gzip: ~49KB)
- **Ladezeit**: < 2 Sekunden
- **Hot Reload**: < 1 Sekunde
- **API-Response**: < 3 Sekunden