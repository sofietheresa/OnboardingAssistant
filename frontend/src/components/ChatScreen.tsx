import React, { useState, useRef, useEffect } from 'react';
import { ChatScreenProps } from '../types';

const ChatScreen: React.FC<ChatScreenProps> = ({
  location,
  messages,
  onSendMessage,
  onBackToOnboarding,
  isLoading
}) => {
  const [inputText, setInputText] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputText.trim() && !isLoading) {
      onSendMessage(inputText);
      setInputText('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="chat-screen">
      {/* Header mit blauem Hintergrund */}
      <div className="chat-header">
        <button className="back-button" onClick={onBackToOnboarding}>
          <div className="arrow"></div>
        </button>
        <div className="location-title">
          {location.name}
        </div>
      </div>

      {/* Chat-Nachrichten */}
      <div className="chat-messages">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`message ${message.isUser ? 'user' : 'assistant'}`}
          >
            <div className="message-content">
              {message.text}
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="loading-indicator">
            Boardy schreibt...
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Eingabefeld */}
      <form className="chat-input" onSubmit={handleSubmit}>
        <div className="input-container">
          <button type="button" className="plus-button" aria-label="Anhang hinzufügen">
            {/* Plus-Zeichen wird durch CSS hinzugefügt */}
          </button>
          
          <input
            type="text"
            className="message-input"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Frag etwas!"
            disabled={isLoading}
          />
          
          <button
            type="submit"
            className="send-button"
            disabled={!inputText.trim() || isLoading}
            aria-label="Nachricht senden"
          >
            {/* Senden-Icon wird durch CSS hinzugefügt */}
          </button>
        </div>
      </form>

      {/* Gelbe Akzente */}
      <div className="yellow-accent"></div>
      <div className="yellow-accent"></div>
      <div className="yellow-accent"></div>
      <div className="yellow-accent"></div>
    </div>
  );
};

export default ChatScreen; 