import React from 'react';
import { useOnboarding } from '../contexts/OnboardingContext';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import '../styles/OnboardingModal.css';

const OnboardingModal: React.FC = () => {
  const { 
    showOnboarding, 
    steps, 
    currentStepIndex, 
    profileCompletion,
    nextStep, 
    previousStep, 
    completeOnboarding, 
    dismissOnboarding 
  } = useOnboarding();
  const { user } = useAuth();
  const navigate = useNavigate();

  if (!showOnboarding || !user) {
    return null;
  }

  const currentStep = steps[currentStepIndex];
  const isLastStep = currentStepIndex === steps.length - 1;
  const isFirstStep = currentStepIndex === 0;

  const handleActionClick = () => {
    if (!currentStep?.action) return;

    switch (currentStep.action) {
      case 'select_avatar':
        navigate('/profile');
        dismissOnboarding();
        break;
      case 'edit_profile':
        navigate('/profile');
        dismissOnboarding();
        break;
      case 'build_deck':
        navigate('/');
        dismissOnboarding();
        break;
      default:
        break;
    }
  };

  const handleComplete = () => {
    completeOnboarding();
  };

  const handleSkip = () => {
    dismissOnboarding();
  };

  return (
    <div className="onboarding-modal__overlay">
      <div className="onboarding-modal">
        <div className="onboarding-modal__header">
          <h2 className="onboarding-modal__title">
            Welcome to Clash Royale Deck Builder!
          </h2>
          <button
            className="onboarding-modal__close"
            onClick={handleSkip}
            aria-label="Close onboarding"
          >
            ×
          </button>
        </div>

        <div className="onboarding-modal__content">
          {/* Progress indicator */}
          <div className="onboarding-modal__progress">
            <div className="onboarding-modal__progress-bar">
              <div 
                className="onboarding-modal__progress-fill"
                style={{ width: `${((currentStepIndex + 1) / steps.length) * 100}%` }}
              />
            </div>
            <span className="onboarding-modal__progress-text">
              Step {currentStepIndex + 1} of {steps.length}
            </span>
          </div>

          {/* Profile completion indicator */}
          {profileCompletion && (
            <div className="onboarding-modal__profile-completion">
              <div className="onboarding-modal__completion-header">
                <span className="onboarding-modal__completion-title">Profile Completion</span>
                <span className="onboarding-modal__completion-percentage">
                  {profileCompletion.percentage}%
                </span>
              </div>
              <div className="onboarding-modal__completion-bar">
                <div 
                  className="onboarding-modal__completion-fill"
                  style={{ width: `${profileCompletion.percentage}%` }}
                />
              </div>
            </div>
          )}

          {/* Current step content */}
          {currentStep && (
            <div className="onboarding-modal__step">
              <div className="onboarding-modal__step-icon">
                {currentStep.completed ? '✅' : getStepIcon(currentStep.id)}
              </div>
              <h3 className="onboarding-modal__step-title">
                {currentStep.title}
              </h3>
              <p className="onboarding-modal__step-description">
                {currentStep.description}
              </p>
              
              {currentStep.action && !currentStep.completed && (
                <button
                  className="onboarding-modal__action-button"
                  onClick={handleActionClick}
                >
                  {getActionButtonText(currentStep.action)}
                </button>
              )}
            </div>
          )}

          {/* User info display */}
          <div className="onboarding-modal__user-info">
            <div className="onboarding-modal__user-avatar">
              {user.avatar ? (
                <img 
                  src={`https://api-assets.clashroyale.com/cards/300/${user.avatar}.png`}
                  alt={`${user.name}'s avatar`}
                  className="onboarding-modal__avatar-image"
                />
              ) : (
                <div className="onboarding-modal__avatar-placeholder">
                  👤
                </div>
              )}
            </div>
            <div className="onboarding-modal__user-details">
              <span className="onboarding-modal__user-name">{user.name}</span>
              <span className="onboarding-modal__user-email">{user.email}</span>
            </div>
          </div>
        </div>

        <div className="onboarding-modal__footer">
          <div className="onboarding-modal__navigation">
            <button
              className="onboarding-modal__nav-button onboarding-modal__nav-button--secondary"
              onClick={previousStep}
              disabled={isFirstStep}
            >
              Previous
            </button>
            
            {isLastStep ? (
              <button
                className="onboarding-modal__nav-button onboarding-modal__nav-button--primary"
                onClick={handleComplete}
              >
                Get Started!
              </button>
            ) : (
              <button
                className="onboarding-modal__nav-button onboarding-modal__nav-button--primary"
                onClick={nextStep}
              >
                Next
              </button>
            )}
          </div>
          
          <button
            className="onboarding-modal__skip-button"
            onClick={handleSkip}
          >
            Skip for now
          </button>
        </div>
      </div>
    </div>
  );
};

// Helper function to get step icon
const getStepIcon = (stepId: string): string => {
  switch (stepId) {
    case 'welcome':
      return '👋';
    case 'avatar_selection':
      return '🎭';
    case 'profile_setup':
      return '✏️';
    case 'start_building':
      return '🏗️';
    default:
      return '📋';
  }
};

// Helper function to get action button text
const getActionButtonText = (action: string): string => {
  switch (action) {
    case 'select_avatar':
      return 'Choose Avatar';
    case 'edit_profile':
      return 'Edit Profile';
    case 'build_deck':
      return 'Build Your First Deck';
    default:
      return 'Continue';
  }
};

export default OnboardingModal;