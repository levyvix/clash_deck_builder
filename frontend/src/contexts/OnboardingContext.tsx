import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useAuth } from './AuthContext';
import { getOnboardingStatus } from '../services/authService';

// Onboarding step interface
interface OnboardingStep {
  id: string;
  title: string;
  description: string;
  completed: boolean;
  required: boolean;
  action?: string;
}

// Onboarding state interface
interface OnboardingState {
  isNewUser: boolean;
  needsProfileSetup: boolean;
  steps: OnboardingStep[];
  profileCompletion: {
    percentage: number;
    completedItems: number;
    totalItems: number;
    items: Record<string, boolean>;
    isComplete: boolean;
  };
  showOnboarding: boolean;
  currentStepIndex: number;
}

// Onboarding context type
interface OnboardingContextType extends OnboardingState {
  refreshOnboardingStatus: () => Promise<void>;
  nextStep: () => void;
  previousStep: () => void;
  goToStep: (stepIndex: number) => void;
  completeOnboarding: () => void;
  dismissOnboarding: () => void;
  showOnboardingModal: () => void;
}

// Initial state
const initialState: OnboardingState = {
  isNewUser: false,
  needsProfileSetup: false,
  steps: [],
  profileCompletion: {
    percentage: 0,
    completedItems: 0,
    totalItems: 0,
    items: {},
    isComplete: false,
  },
  showOnboarding: false,
  currentStepIndex: 0,
};

// Create context
const OnboardingContext = createContext<OnboardingContextType | undefined>(undefined);

// Onboarding provider props
interface OnboardingProviderProps {
  children: ReactNode;
}

// Onboarding provider component
export const OnboardingProvider: React.FC<OnboardingProviderProps> = ({ children }) => {
  const { user, isAuthenticated } = useAuth();
  const [state, setState] = useState<OnboardingState>(initialState);

  // Fetch onboarding status when user is authenticated (only on initial auth, not on user updates)
  useEffect(() => {
    if (isAuthenticated && user) {
      // Check if user has previously dismissed onboarding
      const onboardingDismissed = localStorage.getItem('onboarding_dismissed') === 'true';
      if (onboardingDismissed) {
        // Don't show onboarding if user has dismissed it
        setState(prevState => ({
          ...prevState,
          isNewUser: false,
          showOnboarding: false,
        }));
      } else {
        refreshOnboardingStatus();
      }
    } else {
      // Reset onboarding state when user logs out
      setState(initialState);
      localStorage.removeItem('onboarding_dismissed');
    }
  }, [isAuthenticated]); // Removed 'user' dependency to prevent triggering on profile updates

  // Refresh onboarding status from API
  const refreshOnboardingStatus = async (): Promise<void> => {
    try {
      const onboardingData = await getOnboardingStatus();
      
      console.log('📋 Onboarding data received:', onboardingData);
      
      setState(prevState => ({
        ...prevState,
        isNewUser: onboardingData.is_new_user,
        needsProfileSetup: onboardingData.needs_profile_setup,
        steps: onboardingData.onboarding_steps,
        profileCompletion: onboardingData.profile_completion,
        // Show onboarding automatically for new users or users who need profile setup
        showOnboarding: prevState.showOnboarding || onboardingData.is_new_user || onboardingData.needs_profile_setup,
      }));
    } catch (error) {
      console.error('Failed to fetch onboarding status:', error);
    }
  };

  // Navigate to next step
  const nextStep = (): void => {
    setState(prevState => ({
      ...prevState,
      currentStepIndex: Math.min(prevState.currentStepIndex + 1, prevState.steps.length - 1),
    }));
  };

  // Navigate to previous step
  const previousStep = (): void => {
    setState(prevState => ({
      ...prevState,
      currentStepIndex: Math.max(prevState.currentStepIndex - 1, 0),
    }));
  };

  // Go to specific step
  const goToStep = (stepIndex: number): void => {
    setState(prevState => ({
      ...prevState,
      currentStepIndex: Math.max(0, Math.min(stepIndex, prevState.steps.length - 1)),
    }));
  };

  // Complete onboarding
  const completeOnboarding = (): void => {
    setState(prevState => ({
      ...prevState,
      showOnboarding: false,
      currentStepIndex: 0,
      isNewUser: false,
    }));
    
    // Store completion in localStorage
    localStorage.setItem('onboarding_dismissed', 'true');
  };

  // Dismiss onboarding (user can reopen it later)
  const dismissOnboarding = (): void => {
    setState(prevState => ({
      ...prevState,
      showOnboarding: false,
      isNewUser: false, // Mark as no longer a new user
    }));
    
    // Store dismissal in localStorage to persist across sessions
    localStorage.setItem('onboarding_dismissed', 'true');
  };

  // Show onboarding modal
  const showOnboardingModal = (): void => {
    setState(prevState => ({
      ...prevState,
      showOnboarding: true,
      currentStepIndex: 0,
    }));
  };

  const contextValue: OnboardingContextType = {
    ...state,
    refreshOnboardingStatus,
    nextStep,
    previousStep,
    goToStep,
    completeOnboarding,
    dismissOnboarding,
    showOnboardingModal,
  };

  return (
    <OnboardingContext.Provider value={contextValue}>
      {children}
    </OnboardingContext.Provider>
  );
};

// Custom hook to use onboarding context
export const useOnboarding = (): OnboardingContextType => {
  const context = useContext(OnboardingContext);
  if (context === undefined) {
    throw new Error('useOnboarding must be used within an OnboardingProvider');
  }
  return context;
};

export default OnboardingContext;