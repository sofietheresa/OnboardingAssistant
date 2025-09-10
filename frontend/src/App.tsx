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
  const API_BASE_URL = "http://localhost:8080";
  const locationById = LOCATIONS.reduce((map, location) => {
    map[location.id] = location;
    return map;
  }, {} as Record<string, Location>);
  // The OnboardingScreen component is imported from './components/OnboardingScreen'
  // Its file path is:
  // /Users/furkansaygin/Documents/Master/AI Labs/OnboardingAssistant/frontend/src/components/OnboardingScreen.tsx
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
    fetch(`${API_BASE_URL}/api/locations`).catch((err) => {
        console.error("Failed to fetch locations:", err);
    });
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
    setIsLoading(true);
    
    // Prepare chat history for backend (exclude the current message we just added)
    const chatHistory = messages.map(msg => ({
      id: msg.id,
      text: msg.text,
      isUser: msg.isUser,
      timestamp: msg.timestamp.toISOString()
    }));
    
    // Send to backend (non-blocking, append response when returned)
    fetch(`${API_BASE_URL}/v1/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        query: text,
        location: selectedLocation,
        chatHistory: chatHistory
      })
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
      })
      .finally(() => {
        setIsLoading(false);
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

