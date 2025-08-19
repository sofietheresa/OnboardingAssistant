import React, { useState, useRef, useEffect } from 'react';
import { ChatScreenProps } from '../types';
import '../styles/ChatScreen.css';

const ChatScreen: React.FC<ChatScreenProps> = ({ 
  location, 
  messages, 
  onSendMessage, 
  onBackToOnboarding, 
  isLoading 
}) => {
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputValue.trim()) {
      onSendMessage(inputValue.trim());
      setInputValue('');
    }
  };

  const handlePlusClick = () => {
    // Create file input element
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.multiple = true;
    fileInput.accept = '*/*'; // Accept all file types
    
    fileInput.onchange = (event) => {
      const files = (event.target as HTMLInputElement).files;
      if (files && files.length > 0) {
        console.log('Selected files:', Array.from(files).map(f => f.name));
        // TODO: Handle file upload to backend
      }
    };
    
    fileInput.click();
  };

  const handleVoiceClick = () => {
    // TODO: Implement voice recording functionality
    console.log('Voice button clicked');
  };

  return (
    <div className="chat-container">
      <div className="chat-screen">
        {/* Header Section - Exact from Figma */}
        <div className="chat-header">
          {/* Back Button with Boardy Robot */}
          <div className="back-button-container">
            <button className="back-button" onClick={onBackToOnboarding}>
              <img 
                src="/boardy_small.svg" 
                alt="Boardy Robot" 
                className="boardy-icon"
              />
            </button>
          </div>

          {/* Yellow Arrow pointing left - Navigation */}
          <div className="yellow-arrow" onClick={onBackToOnboarding}>←</div>

          {/* Location Title (e.g., "UDG Ludwigsburg") */}
          <div className="location-title">
            {location.name}
          </div>
        </div>

        {/* Chat Messages Area */}
        <div className="chat-messages">
          {/* Initial Boardy Message - styled exactly like Figma */}
          <div className="message assistant">
            <div className="message-content">
              Wie kann ich dir helfen?
            </div>
          </div>

          {/* Additional messages */}
          {messages.slice(1).map((message) => (
            <div key={message.id} className={`message ${message.isUser ? 'user' : 'assistant'}`}>
              <div className="message-content">
                {message.text}
              </div>
            </div>
          ))}

          {/* Loading indicator */}
          {isLoading && (
            <div className="loading-indicator">
              <span>Boardy tippt</span>
              <div className="typing-animation">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Chat Input Section - Neuanordnung wie Screenshot */}
        <div className="chat-input-container">
          {/* Plus Button - Außerhalb der blauen Box, links */}
          <button className="plus-button-outside" onClick={handlePlusClick}>
            <span className="plus-icon">+</span>
          </button>

          {/* Light blue input background container */}
          <div className="input-background">
            {/* Text Input - füllt den verfügbaren Platz */}
            <form onSubmit={handleSubmit} className="chat-input-form">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Frag etwas!"
                className="message-input"
              />
            </form>

            {/* Conditional buttons based on input */}
            {inputValue.trim() ? (
              /* Send Button - Arrow pointing up */
              <button className="send-button" onClick={handleSubmit}>
                <div className="send-arrow">↑</div>
              </button>
            ) : (
              <>
                {/* Voice Button with Microphone Icon */}
                <button className="microphone-button" onClick={handleVoiceClick}>
                  <img 
                    src="/microphone.svg" 
                    alt="Voice Input" 
                    className="microphone-icon"
                  />
                </button>

                {/* Soundwave Button - Dark blue circle with yellow bars */}
                <button className="soundwave-button">
                  <div className="soundwave-bars">
                    <div className="bar bar-1"></div>
                    <div className="bar bar-2"></div>
                    <div className="bar bar-3"></div>
                    <div className="bar bar-4"></div>
                  </div>
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatScreen;
