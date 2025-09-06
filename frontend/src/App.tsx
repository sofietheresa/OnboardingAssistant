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
  const isLoading = false; // wire up to backend later

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

  const handleSendMessage = (text: string, fileAttachment?: FileAttachment, audioAttachment?: AudioAttachment) => {
    const newMessage: Message = {
      id: crypto.randomUUID(),
      text,
      isUser: true,
      timestamp: new Date(),
      fileAttachment,
      audioAttachment
    };
    
    setMessages((prev) => [...prev, newMessage]);
    
    // Send to backend (non-blocking, append response when returned)
    const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'https://boardy-app.1zt0zkzab8pz.eu-de.codeengine.appdomain.cloud';
    fetch(`${apiBaseUrl}/v1/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: text })
    })
      .then((r) => r.json())
      .then((data) => {
        setMessages((prev) => [...prev, { 
          id: crypto.randomUUID(), 
          text: data.answer, 
          isUser: false, 
          timestamp: new Date(),
          sources: data.sources || []
        }]);
      })
      .catch(() => {
        setMessages((prev) => [...prev, { 
          id: crypto.randomUUID(), 
          text: '(Fehler) Keine Antwort vom Server.', 
          isUser: false, 
          timestamp: new Date() 
        }]);
      });
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

