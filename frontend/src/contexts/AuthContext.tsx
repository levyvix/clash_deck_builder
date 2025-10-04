import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { User, AuthState, GoogleUserInfo } from '../types';
import { 
  loginWithGoogle, 
  logout as logoutService, 
  updateUserProfile, 
  validateToken,
  AuthError 
} from '../services/authService';

// Auth action types
type AuthAction =
  | { type: 'AUTH_START' }
  | { type: 'AUTH_SUCCESS'; payload: User }
  | { type: 'AUTH_FAILURE' }
  | { type: 'LOGOUT' }
  | { type: 'UPDATE_USER'; payload: User }
  | { type: 'SET_LOADING'; payload: boolean };

// Auth context type
interface AuthContextType extends AuthState {
  login: (authCode: string, userInfo: GoogleUserInfo, migrationData?: any) => Promise<void>;
  logout: () => Promise<void>;
  updateProfile: (updates: { name?: string; avatar?: string }) => Promise<void>;
  refreshUser: () => Promise<void>;
}

// Initial state
const initialState: AuthState = {
  user: null,
  isLoading: true, // Start with loading true to check existing session
  isAuthenticated: false,
};

// Auth reducer
const authReducer = (state: AuthState, action: AuthAction): AuthState => {
  switch (action.type) {
    case 'AUTH_START':
      return {
        ...state,
        isLoading: true,
      };
    case 'AUTH_SUCCESS':
      return {
        ...state,
        user: action.payload,
        isLoading: false,
        isAuthenticated: true,
      };
    case 'AUTH_FAILURE':
      return {
        ...state,
        user: null,
        isLoading: false,
        isAuthenticated: false,
      };
    case 'LOGOUT':
      return {
        ...state,
        user: null,
        isLoading: false,
        isAuthenticated: false,
      };
    case 'UPDATE_USER':
      return {
        ...state,
        user: action.payload,
      };
    case 'SET_LOADING':
      return {
        ...state,
        isLoading: action.payload,
      };
    default:
      return state;
  }
};

// Create context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Auth provider props
interface AuthProviderProps {
  children: ReactNode;
}

// Auth provider component
export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Check for existing session on mount
  useEffect(() => {
    const checkExistingSession = async () => {
      try {
        dispatch({ type: 'AUTH_START' });
        const user = await validateToken();
        
        if (user) {
          dispatch({ type: 'AUTH_SUCCESS', payload: user });
        } else {
          dispatch({ type: 'AUTH_FAILURE' });
        }
      } catch (error) {
        console.error('Session validation failed:', error);
        dispatch({ type: 'AUTH_FAILURE' });
      }
    };

    checkExistingSession();
  }, []);

  // Login function
  const login = async (authCode: string, userInfo: GoogleUserInfo, migrationData?: any): Promise<void> => {
    try {
      dispatch({ type: 'AUTH_START' });
      const authResponse = await loginWithGoogle(authCode, userInfo, migrationData);
      dispatch({ type: 'AUTH_SUCCESS', payload: authResponse.user });
      
      // Store onboarding data if present
      if (authResponse.onboarding) {
        // The onboarding context will handle this data
        console.log('Onboarding data received:', authResponse.onboarding);
      }
    } catch (error) {
      dispatch({ type: 'AUTH_FAILURE' });
      throw error;
    }
  };

  // Logout function
  const logout = async (): Promise<void> => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      await logoutService();
      dispatch({ type: 'LOGOUT' });
    } catch (error) {
      // Even if logout API fails, clear local state
      dispatch({ type: 'LOGOUT' });
      console.error('Logout error:', error);
    }
  };

  // Update profile function
  const updateProfile = async (updates: { name?: string; avatar?: string }): Promise<void> => {
    if (!state.user) {
      throw new AuthError('No user logged in');
    }

    try {
      const updatedUser = await updateUserProfile(updates);
      dispatch({ type: 'UPDATE_USER', payload: updatedUser });
    } catch (error) {
      console.error('Profile update failed:', error);
      
      // Don't logout user on profile update errors unless it's an auth error
      if (error instanceof AuthError && error.statusCode === 401) {
        console.warn('Authentication failed during profile update, logging out user');
        dispatch({ type: 'AUTH_FAILURE' });
      }
      
      throw error;
    }
  };

  // Refresh user data
  const refreshUser = async (): Promise<void> => {
    if (!state.isAuthenticated) {
      return;
    }

    try {
      const user = await validateToken();
      if (user) {
        dispatch({ type: 'UPDATE_USER', payload: user });
      } else {
        dispatch({ type: 'AUTH_FAILURE' });
      }
    } catch (error) {
      console.error('User refresh failed:', error);
      dispatch({ type: 'AUTH_FAILURE' });
    }
  };

  const contextValue: AuthContextType = {
    ...state,
    login,
    logout,
    updateProfile,
    refreshUser,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use auth context
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;