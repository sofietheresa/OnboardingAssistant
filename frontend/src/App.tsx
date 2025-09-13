import React, { useState, useEffect } from 'react';
import ChatScreen from './components/ChatScreen';
import OnboardingScreen from './components/OnboardingScreen';
import { Location, Message, FileAttachment, AudioAttachment } from './types';
import './styles.css';

const LOCATIONS: Location[] = [
  { id: 'boeblingen', name: 'IBM Böblingen', description: 'Entwicklungs- und Innovationszentrum.' },
  { id: 'muenchen', name: 'IBM München', description: 'Client Center und Lab Standorte.' },
  { id: 'ludwigsburg', name: 'UDG Ludwigsburg', description: 'Digitalagentur im IBM iX Netzwerk.' }
];

const App: React.FC = () => {
  const [selectedLocation, setSelectedLocation] = useState<Location | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const locationById = LOCATIONS.reduce((map, location) => {
    map[location.id] = location;
    return map;
  }, {} as Record<string, Location>);

  const handleChooseLocation = (id: string) => {
    setSelectedLocation(locationById[id]);
    setMessages([
      {
        id: crypto.randomUUID(),
        text: `Hallo! Ich bin Boardy. Wie kann ich dir am Standort ${locationById[id].name} helfen?`,
        isUser: false,
        timestamp: new Date()
      }
    ]);
  };

  // Load locations from backend if available (keeps UI in sync)
  useEffect(() => {
    const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'https://boardy-app.1zt0zkzab8pz.eu-de.codeengine.appdomain.cloud';
    fetch(`${apiBaseUrl}/api/locations`).catch(() => {});
  }, []);

  const handleBackToOnboarding = () => {
    setSelectedLocation(null);
    setMessages([]);
  };

const handleSendMessage = (
  text: string,
  fileAttachment?: FileAttachment,
  audioAttachment?: AudioAttachment,
  isUser: boolean = true,
  skipBackend: boolean = false
) => {
  const newMessage: Message = {
    id: crypto.randomUUID(),
    text,
    isUser,
    timestamp: new Date(),
    fileAttachment,
    audioAttachment
  };

  setMessages((prev: Message[]) => [...prev, newMessage]);

  // 🚫 Nur wenn User UND kein skipBackend → Backend call
  if (isUser && !skipBackend) {
    setIsLoading(true);
    const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'https://boardy-app.1zt0zkzab8pz.eu-de.codeengine.appdomain.cloud';
    // Chatverlauf für den Backend-Call vorbereiten (ohne file/audio)
    const history = (messages as Message[]).map((m: Message) => ({
      role: m.isUser ? "user" : "assistant",
      content: m.text
    }));
    fetch(`${apiBaseUrl}/v1/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: text, history })
    })
      .then((r) => r.json())
      .then((data) => {
        setMessages((prev: Message[]) => [
          ...prev,
          {
            id: crypto.randomUUID(),
            text: data.answer,
            isUser: false,
            timestamp: new Date(),
            sources: data.sources || []
          }
        ]);
      })
      .catch(() => {
        setMessages((prev: Message[]) => [
          ...prev,
          {
            id: crypto.randomUUID(),
            text: '(Fehler) Keine Antwort vom Server.',
            isUser: false,
            timestamp: new Date()
          }
        ]);
      })
      .finally(() => {
        setIsLoading(false);
      });
  }
};



  // Render onboarding when no location selected
  if (!selectedLocation) {
    return (
      <div className="app-shell">
        <OnboardingScreen onChooseLocation={handleChooseLocation} />
      </div>
    );
  }

  return (
    <div className="app-shell">
      <ChatScreen
        location={selectedLocation}
        messages={messages}
        onSendMessage={handleSendMessage}
        onBackToOnboarding={handleBackToOnboarding}
        isLoading={isLoading}
      />
    </div>
  );
};

export default App;

