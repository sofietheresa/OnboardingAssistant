import React, { useMemo, useState, useEffect } from 'react';
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

  const locationById = useMemo(() => {
    const map: Record<string, Location> = {};
    LOCATIONS.forEach((l) => { map[l.id] = l; });
    return map;
  }, []);

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
    fetch('/api/locations')
      .then((r) => (r.ok ? r.json() : []))
      .catch(() => []);
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
    
    // Create FormData for file uploads
    const formData = new FormData();
    formData.append('message', text);
    formData.append('location', selectedLocation?.name ?? '');
    
    if (fileAttachment) {
      formData.append('hasFile', 'true');
      formData.append('fileName', fileAttachment.name);
      formData.append('fileType', fileAttachment.type);
      // In a real implementation, you would append the actual file here
    }
    
    if (audioAttachment) {
      formData.append('hasAudio', 'true');
      formData.append('audioDuration', audioAttachment.duration.toString());
      // In a real implementation, you would append the actual audio blob here
    }
    
    // Send to backend (non-blocking, append response when returned)
    fetch('/api/chat', {
      method: 'POST',
      body: formData
    })
      .then((r) => r.json())
      .then((data) => {
        setMessages((prev) => [...prev, { 
          id: crypto.randomUUID(), 
          text: data.response, 
          isUser: false, 
          timestamp: new Date() 
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

