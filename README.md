# 🤖 Boardy - IBM Onboarding Assistant

Ein intelligenter Chat-Assistent für IBM-Standorte mit Watson X Integration.

## ✨ Features

- 🎯 **Location-spezifisches Onboarding** - Angepasst an IBM-Standorte
- 🤖 **Watson X Integration** - Nutzt IBMs fortschrittliche KI-Modelle
- 💻 **Desktop-optimiert** - Professionelles, responsives Design
- 🐳 **Container-basiert** - Einfache Bereitstellung mit Podman

## 🚀 Quick Start

### 1. Voraussetzungen

- **WSL2** mit Ubuntu
- **Podman** und **podman-compose** in WSL
- **Watson X API-Zugang**

### 2. Installation

```bash
# Projekt klonen
git clone https://github.com/sofietheresa/OnboardingAssistant.git
cd OnboardingAssistant

# Umgebungsvariablen konfigurieren
cp env.example .env
# Bearbeiten Sie .env mit Ihren Watson X Credentials
```

### 3. Anwendung starten

```cmd
# Windows - Einfach doppelklicken oder ausführen:
run.bat
```

Das war's! 🎉

## 📁 Projektstruktur

```
boardy-onboarding-assistant/
├── backend/                    # FastAPI Backend
│   ├── app.py                 # Hauptanwendung
│   ├── requirements.txt       # Python Dependencies
│   └── Dockerfile            # Container Definition
├── frontend/                  # Frontend (fertig gebaut)
│   └── build/                # Produktive HTML/CSS/JS Dateien
├── litellm-config.yaml       # Watson X Konfiguration
├── podman-compose.yml        # Container Orchestrierung
├── run.bat                   # Start/Restart Script
├── env.example              # Umgebungsvariablen Vorlage
└── README.md               # Diese Datei
```

## ⚙️ Konfiguration

Erstellen Sie eine `.env` Datei mit Ihren Watson X Credentials:

```env
WATSONX_API_KEY=your_actual_api_key
WATSONX_PROJECT_ID=your_actual_project_id
WATSONX_URL=https://us-south.ml.cloud.ibm.com
```

## 🌐 Zugriff

Nach dem Start ist die Anwendung verfügbar unter:

- **Frontend**: http://localhost:8000
- **API**: http://localhost:8000/api/chat
- **Health Check**: http://localhost:8000/healthz

## 🤖 Verfügbare KI-Modelle

- **llama-3-8b** - Meta Llama 3 8B (Standard)
- **llama-3-70b** - Meta Llama 3 70B
- **granite-8b** - IBM Granite 3 8B
- **mistral-large** - Mistral Large
- **mixtral** - Mixtral 8x7B

## 🎯 Standorte

- **IBM Böblingen** - Innovationszentrum für Cloud & AI
- **IBM München** - Enterprise Solutions & Consulting  
- **UDG Ludwigsburg** - Digital Business & Transformation

## 🔧 Verwaltung

```bash
# Container Status prüfen
wsl --exec bash -c "cd /mnt/c/Users/SofiePischl/Documents/01_HdM/watsonx-chat-starter && podman-compose ps"

# Logs anzeigen
wsl --exec bash -c "cd /mnt/c/Users/SofiePischl/Documents/01_HdM/watsonx-chat-starter && podman-compose logs -f"

# Anwendung stoppen
wsl --exec bash -c "cd /mnt/c/Users/SofiePischl/Documents/01_HdM/watsonx-chat-starter && podman-compose down"
```

## 🐛 Troubleshooting

### Container starten nicht
```bash
# Podman Status prüfen
wsl --exec podman info

# Logs prüfen
wsl --exec bash -c "cd /mnt/c/Users/SofiePischl/Documents/01_HdM/watsonx-chat-starter && podman-compose logs"
```

### API-Fehler
- Überprüfen Sie Ihre Watson X Credentials in `.env`
- Stellen Sie sicher, dass Ihr Watson X Projekt aktiv ist

### Port-Konflikte
- Standard-Ports: 8000 (Frontend/API), 4000 (LiteLLM)
- Bei Konflikten ändern Sie die Ports in `podman-compose.yml`

## 📝 Lizenz

Dieses Projekt ist für Bildungs- und Entwicklungszwecke gedacht.

## 🤝 Support

Bei Fragen oder Problemen erstellen Sie ein Issue im Repository.