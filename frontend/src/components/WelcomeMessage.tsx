import React from 'react';
import { useOnboarding } from '../contexts/OnboardingContext';
import '../styles/WelcomeMessage.css';

const WelcomeMessage: React.FC = () => {
  const { isNewUser, showOnboardingModal, dismissOnboarding } = useOnboarding();

  if (!isNewUser) {
    return null;
  }

  return (
    <div className="welcome-message">
      <div className="welcome-message__content">
        <div className="welcome-message__icon">
          🎉
        </div>
        <h3 className="welcome-message__title">
          Welcome to Clash Royale Deck Builder!
        </h3>
        <p className="welcome-message__description">
          Your Google account has been successfully connected. Let's get your profile set up!
        </p>
        <div className="welcome-message__actions">
          <button
            className="welcome-message__button welcome-message__button--primary"
            onClick={showOnboardingModal}
          >
            Get Started
          </button>
          <button
            className="welcome-message__button welcome-message__button--secondary"
            onClick={dismissOnboarding}
          >
            Skip for now
          </button>
        </div>
      </div>
    </div>
  );
};

export default WelcomeMessage;