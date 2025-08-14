# 🚀 Boardy - IBM Onboarding Assistant

Ein intelligenter Chatbot-Assistent für das IBM Onboarding, der Mitarbeitern hilft, sich an verschiedenen Standorten zurechtzufinden.

## 📁 Projektstruktur

```
watsonx-chat-starter/
├── 📁 backend/                 # Python Flask Backend
│   ├── 📁 models/             # Datenmodelle
│   ├── 📁 routes/             # API-Routen
│   ├── app.py                 # Hauptanwendung
│   ├── Dockerfile             # Container-Konfiguration
│   └── requirements.txt       # Python-Abhängigkeiten
├── 📁 frontend/               # React TypeScript Frontend
│   ├── 📁 src/
│   │   ├── 📁 components/     # React-Komponenten
│   │   ├── 📁 types/          # TypeScript-Typen
│   │   ├── 📁 hooks/          # Custom React Hooks
│   │   ├── 📁 utils/          # Hilfsfunktionen
│   │   ├── App.tsx            # Hauptkomponente
│   │   ├── main.tsx           # Einstiegspunkt
│   │   └── styles.css         # Styling
│   ├── 📁 public/             # Statische Assets
│   ├── package.json           # Node.js-Abhängigkeiten
│   └── vite.config.ts         # Vite-Konfiguration
├── 📁 scripts/                # Start-Skripte
│   ├── start-dev.bat          # Entwicklung starten
│   └── start-prod.bat         # Produktion starten
├── 📁 docs/                   # Dokumentation
├── 📁 tests/                  # Test-Dateien
├── podman-compose.yml         # Container-Orchestrierung
├── litellm-config.yaml        # LiteLLM-Konfiguration
└── README.md                  # Diese Datei
```

## 🚀 Schnellstart

### Voraussetzungen
- [Podman](https://podman.io/) installiert
- [Node.js](https://nodejs.org/) (Version 18+)
- [WSL2](https://docs.microsoft.com/en-us/windows/wsl/) (Windows)

### 1. Repository klonen
```bash
git clone <repository-url>
cd watsonx-chat-starter
```

### 2. Umgebungsvariablen konfigurieren
```bash
# env.example zu .env kopieren
cp env.example .env

# .env mit deinen Watson X Credentials bearbeiten
WATSONX_API_KEY=your_api_key
WATSONX_PROJECT_ID=your_project_id
WATSONX_URL=https://us-south.ml.cloud.ibm.com
```

### 3. Frontend-Abhängigkeiten installieren
```bash
cd frontend
npm install
cd ..
```

### 4. Anwendung starten

#### Entwicklung (mit Hot Reload)
```bash
# Windows
scripts\start-dev.bat

# Oder manuell:
# Terminal 1: Backend starten
podman-compose up --build

# Terminal 2: Frontend starten
cd frontend && npm run dev
```

#### Produktion
```bash
# Windows
scripts\start-prod.bat
```

## 🌐 Zugriff

- **Entwicklung**: http://localhost:5173 (Frontend) + http://localhost:8000 (Backend)
- **Produktion**: http://localhost:8000 (alles über Backend)

## 🛠️ Entwicklung

### Frontend
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite (schnell, Hot Reload)
- **Styling**: CSS mit CSS-Variablen
- **Struktur**: Komponenten-basiert mit getrennten Types

### Backend
- **Framework**: Flask (Python)
- **AI**: LiteLLM + Watson X
- **Container**: Podman + Docker Compose

### Hot Reload
Das Frontend lädt automatisch neu, wenn du Dateien änderst. Keine manuellen Browser-Refreshs nötig!

## 📝 Features

- 🎯 **Standortauswahl**: IBM Böblingen, München, UDG Ludwigsburg
- 💬 **Intelligenter Chat**: Watson X Integration
- 🎨 **Moderne UI**: Responsive Design
- 🔄 **Hot Reload**: Sofortige Änderungen sichtbar
- 🐳 **Containerisiert**: Einfache Bereitstellung

## 🧪 Tests

```bash
# Frontend Tests (wenn implementiert)
cd frontend
npm test

# Backend Tests (wenn implementiert)
cd backend
python -m pytest
```

## 📦 Deployment

### Lokale Produktion
```bash
scripts\start-prod.bat
```

### Cloud Deployment
1. Frontend builden: `cd frontend && npm run build`
2. Container pushen: `podman-compose push`
3. Auf Ziel-Server deployen

## 🤝 Beitragen

1. Fork erstellen
2. Feature-Branch: `git checkout -b feature/amazing-feature`
3. Commits: `git commit -m 'Add amazing feature'`
4. Push: `git push origin feature/amazing-feature`
5. Pull Request erstellen

## 📄 Lizenz

Dieses Projekt ist Teil des IBM Onboarding-Programms.

## 🆘 Support

Bei Problemen:
1. Issues auf GitHub erstellen
2. Logs überprüfen: `podman-compose logs`
3. Frontend-Logs im Browser-DevTools

---

**Entwickelt mit ❤️ für IBM Mitarbeiter**