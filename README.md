# Watson X Chat Starter - Boardy Onboarding Assistant

Ein mobiler Chat-Assistent für IBM-Standorte mit Watson X Integration.

## 🚀 Features

- **Mobile-First Design** - Optimiert für alle Bildschirmgrößen
- **Onboarding-Interface** - Location-Auswahl für IBM-Standorte
- **Watson X Integration** - Nutzt IBM's fortschrittliche Sprachmodelle
- **Podman-Container** - Moderne Container-Technologie
- **Responsive Web-App** - Funktioniert auf Desktop und Mobile

## 🎨 Screenshots

### Onboarding Screen
- Freundlicher Robot-Charakter "Boardy"
- Location-Auswahl: IBM Böblingen, IBM München, UDG Ludwigsburg
- Modernes, klares Design

### Chat Interface
- Mobile Chat-Design
- Location-spezifischer Kontext
- Intuitive Bedienung

## 📋 Voraussetzungen

- **WSL2** (Windows Subsystem for Linux)
- **Podman** (in WSL installiert)
- **podman-compose** (in WSL installiert)
- **Watson X API-Zugang**

## 🛠️ Installation

### 1. WSL und Podman einrichten
```bash
# WSL öffnen
wsl

# Podman installieren (falls nicht vorhanden)
sudo apt update
sudo apt install -y podman

# podman-compose installieren
pip install podman-compose
```

### 2. Projekt klonen
```bash
git clone https://github.com/sofietheresa/OnboardingAssistant.git
cd OnboardingAssistant
```

### 3. Umgebungsvariablen konfigurieren
```bash
# .env Datei bearbeiten
cp env.example .env
nano .env
```

**Benötigte Werte:**
```env
WATSONX_API_KEY=your_actual_api_key
WATSONX_PROJECT_ID=your_actual_project_id
WATSONX_URL=https://us-south.ml.cloud.ibm.com
```

## 🚀 Verwendung

### Anwendung starten
```bash
# In WSL ausführen
./start-podman-wsl.sh
```

### Anwendung stoppen
```bash
# In WSL ausführen
./stop-podman-wsl.sh
```

### Anwendung neustarten
```bash
# In WSL ausführen
./restart-podman-wsl.sh
```

### Von Windows aus starten
```bash
wsl --distribution Ubuntu --exec bash -c "cd /mnt/c/Users/SofiePischl/Documents/01_HdM/watsonx-chat-starter && ./start-podman-wsl.sh"
```

## 🌐 Zugriff

- **Frontend**: http://localhost:8000
- **API**: http://localhost:8000/api/chat
- **Health Check**: http://localhost:8000/healthz

## 🔧 Verwaltung

### Container-Status prüfen
```bash
podman-compose -f podman-compose.yml ps
```

### Logs anzeigen
```bash
podman-compose -f podman-compose.yml logs -f
```

### Container neu starten
```bash
podman-compose -f podman-compose.yml restart
```

## 📁 Projektstruktur

```
OnboardingAssistant/
├── backend/                 # FastAPI Backend
│   ├── app.py              # Hauptanwendung
│   ├── static/             # Frontend-Dateien
│   ├── requirements.txt    # Python-Abhängigkeiten
│   └── Dockerfile          # Container-Image
├── litellm-config.yaml     # Watson X Konfiguration
├── podman-compose.yml      # Container-Orchestrierung
├── start-podman-wsl.sh     # Start-Skript (WSL)
├── stop-podman-wsl.sh      # Stopp-Skript (WSL)
├── restart-podman-wsl.sh   # Neustart-Skript (WSL)
├── env.example             # Umgebungsvariablen-Vorlage
└── README.md               # Diese Datei
```

## 🤖 Verfügbare Modelle

- **llama-3-70b** - Meta Llama 3 70B
- **llama-3-8b** - Meta Llama 3 8B (Standard)
- **granite-8b** - IBM Granite 3 8B
- **mistral-large** - Mistral Large
- **mixtral** - Mixtral 8x7B

## 🐛 Troubleshooting

### Container startet nicht
```bash
# Podman-Status prüfen
podman info

# Logs anzeigen
podman-compose -f podman-compose.yml logs
```

### Watson X API-Fehler
- Überprüfen Sie Ihre API-Credentials in der `.env` Datei
- Stellen Sie sicher, dass Ihr Watson X Projekt aktiv ist

### Port-Konflikte
- Falls Port 8000 oder 4000 belegt sind, ändern Sie die Ports in `podman-compose.yml`

## 📝 Lizenz

Dieses Projekt ist für Bildungs- und Entwicklungszwecke gedacht.

## 🤝 Support

Bei Fragen oder Problemen erstellen Sie ein Issue oder kontaktieren Sie das Entwicklungsteam.
