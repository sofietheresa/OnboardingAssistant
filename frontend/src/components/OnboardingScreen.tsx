import React, { useState } from 'react';
import { OnboardingScreenProps } from '../types';

const OnboardingScreen: React.FC<OnboardingScreenProps> = ({ onChooseLocation }) => {
  const [imageFailed, setImageFailed] = useState(false);

  return (
    <div className="onboarding" role="main">
      <div id="screen1" className="screen-1">
        <div className="title-hey">Hey!</div>
        <div className="subtitle">Ich bin Boardy, dein Onboarding-Assistent.</div>
        <div className="choose">Wähle deine Location:</div>

        {/* Sprechblase mit Bild */}
        <div className="bubble">
          {imageFailed ? (
            <div className="bubble-fallback" aria-hidden="true" />
          ) : (
            <img src="/boardy.svg" alt="Boardy" className="bubble-img" onError={() => setImageFailed(true)} />
          )}
        </div>

        <div className="btn-outline-1"></div>
        <div className="btn-outline-2"></div>
        <div className="btn-outline-3"></div>

        <div className="btn-1"></div>
        <div className="btn-2"></div>
        <div className="btn-3"></div>

        <div className="btn-text text-1">IBM Böblingen</div>
        <div className="btn-text text-2">IBM München</div>
        <div className="btn-text text-3">UDG Ludwigsburg</div>

        <button className="btn-link link-1" onClick={() => onChooseLocation('boeblingen')} aria-label="IBM Böblingen" />
        <button className="btn-link link-2" onClick={() => onChooseLocation('muenchen')} aria-label="IBM München" />
        <button className="btn-link link-3" onClick={() => onChooseLocation('ludwigsburg')} aria-label="UDG Ludwigsburg" />
      </div>
    </div>
  );
};

export default OnboardingScreen;

