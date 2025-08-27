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
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputValue.trim() || selectedFile) {
      // Convert File to FileAttachment if file is selected
      const fileAttachment = selectedFile ? {
        name: selectedFile.name,
        size: selectedFile.size,
        type: selectedFile.type,
        url: URL.createObjectURL(selectedFile)
      } : undefined;
      
      onSendMessage(inputValue.trim(), fileAttachment);
      setInputValue('');
      setSelectedFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handlePlusClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = ''; // Reset file input to allow re-selection of the same file
    }
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
          {/* Left side: Arrow and Boardy */}
          <div className="header-left">
            {/* Yellow Arrow pointing left - Navigation */}
            <div className="yellow-arrow" onClick={onBackToOnboarding}>←</div>
            
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
          </div>

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
          <div className={`input-background ${selectedFile ? 'has-document' : ''}`}>
            {/* Hidden File Input */}
            <input 
              type="file" 
              ref={fileInputRef} 
              onChange={handleFileChange} 
              style={{ display: 'none' }} 
              accept="*/*"
            />

            {/* Text Input Form */}
            <form onSubmit={handleSubmit} className="chat-input-form">
              <textarea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Frag etwas!"
                className="message-input"
                rows={1}
                onInput={(e) => {
                  // Automatische Höhenanpassung
                  const target = e.target as HTMLTextAreaElement;
                  target.style.height = 'auto';
                  target.style.height = Math.min(target.scrollHeight, 120) + 'px';
                }}
              />
            </form>

            {/* Selected File Display - Bottom Left */}
            {selectedFile && (
              <div className="selected-file-display">
                <div className="file-info">
                  <span className="file-name" title={selectedFile.name}>
                    {selectedFile.name}
                  </span>
                  <button 
                    type="button" 
                    onClick={handleRemoveFile} 
                    className="remove-file-x"
                    aria-label="Dokument entfernen"
                  >
                    ×
                  </button>
                </div>
              </div>
            )}

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

              
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatScreen;
