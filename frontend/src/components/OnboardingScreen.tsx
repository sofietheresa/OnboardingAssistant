import React from 'react';
import { OnboardingScreenProps } from '../types';
import '../styles/OnboardingScreen.css';

const OnboardingScreen: React.FC<OnboardingScreenProps> = ({ onChooseLocation }) => {

  return (
    <div className="onboarding" role="main">
      <div id="screen1" className="screen-1">
        {/* Header Section */}
        <div className="title-hey">Hey!</div>
        <div className="subtitle">Ich bin Boardy, dein Onboarding-Assistent.</div>
        
        {/* Boardy Image Section */}
        <div className="bubble">
          <img 
            src="/boardy.svg" 
            alt="Boardy" 
            className="bubble-img"
          />
        </div>

        {/* Location Selection Section */}
        <div className="choose">Wähle deine Location:</div>

        {/* Location Buttons Container */}
        <div className="location-buttons">
          {/* IBM Böblingen */}
          <div className="location-button-wrapper">
            <div className="btn-outline-1"></div>
            <div className="btn-1"></div>
            <div className="btn-text text-1">IBM Böblingen</div>
            <button 
              className="btn-link link-1" 
              onClick={() => onChooseLocation('boeblingen')} 
              aria-label="IBM Böblingen"
              type="button"
            />
          </div>

          {/* IBM München */}
          <div className="location-button-wrapper">
            <div className="btn-outline-2"></div>
            <div className="btn-2"></div>
            <div className="btn-text text-2">IBM München</div>
            <button 
              className="btn-link link-2" 
              onClick={() => onChooseLocation('muenchen')} 
              aria-label="IBM München"
              type="button"
            />
          </div>

          {/* UDG Ludwigsburg */}
          <div className="location-button-wrapper">
            <div className="btn-outline-3"></div>
            <div className="btn-3"></div>
            <div className="btn-text text-3">UDG Ludwigsburg</div>
            <button 
              className="btn-link link-3" 
              onClick={() => onChooseLocation('ludwigsburg')} 
              aria-label="UDG Ludwigsburg"
              type="button"
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default OnboardingScreen;

