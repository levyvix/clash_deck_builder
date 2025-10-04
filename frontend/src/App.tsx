import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes, Link, useNavigate, Navigate, useLocation } from 'react-router-dom';
import { GoogleOAuthProvider } from '@react-oauth/google';
import { GOOGLE_CLIENT_ID } from './config';
import DeckBuilder from './components/DeckBuilder';
import SavedDecks from './components/SavedDecks';
import ProfileSection from './components/ProfileSection';
import Notification from './components/Notification';
import ErrorBoundary from './components/ErrorBoundary';
import AuthDemo from './components/AuthDemo';
import ProtectedRoute from './components/ProtectedRoute';
import Footer from './components/Footer';
import GoogleSignInButton from './components/GoogleSignInButton';
import RedirectHandler from './components/RedirectHandler';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { OnboardingProvider } from './contexts/OnboardingContext';
import OnboardingModal from './components/OnboardingModal';
import { Deck, DeckSlot, Notification as NotificationType } from './types';
import { verifyEndpoints } from './services/api';
import { initializeDeckStorageService } from './services/deckStorageService';
import './App.css';

function AppContent() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, isAuthenticated, isLoading } = useAuth();
  
  // Global state for notifications
  const [notifications, setNotifications] = useState<NotificationType[]>([]);
  
  // Global state for current deck (persists across navigation)
  const [currentDeck, setCurrentDeck] = useState<DeckSlot[]>(
    Array(8).fill(null).map(() => ({ card: null, isEvolution: false }))
  );
  
  // State to trigger refresh of saved decks list
  const [refreshSavedDecks, setRefreshSavedDecks] = useState(0);

  // Initialize deck storage service with auth state provider
  useEffect(() => {
    initializeDeckStorageService(() => isAuthenticated);
    console.log('🔧 DeckStorageService initialized with auth provider');
  }, [isAuthenticated]);

  // Verify API endpoints on app initialization (development only)
  useEffect(() => {
    if (process.env.NODE_ENV === 'development') {
      console.log('🚀 App initialized - Running endpoint verification...');
      verifyEndpoints().catch(error => {
        console.error('Endpoint verification failed:', error);
      });
    }
  }, []);

  // Add notification with auto-dismiss after 3 seconds
  const addNotification = (message: string, type: 'success' | 'error' | 'info') => {
    const id = `${Date.now()}-${Math.random()}`;
    const notification: NotificationType = { id, message, type };
    setNotifications(prev => [...prev, notification]);
    
    // Auto-dismiss after 3 seconds
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== id));
    }, 3000);
  };

  // Dismiss notification manually
  const handleDismissNotification = (id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  // Load deck into builder from saved decks
  const loadDeckIntoBuilder = (deck: Deck) => {
    setCurrentDeck(deck.slots);
    navigate('/');
    addNotification(`Loaded deck: ${deck.name}`, 'success');
  };

  // Handle deck saved callback - trigger refresh of saved decks list
  const handleDeckSaved = () => {
    // Increment refresh counter to trigger SavedDecks to reload
    setRefreshSavedDecks(prev => prev + 1);
  };

  return (
    <div className="app">
      {/* Handle automatic redirects */}
      <RedirectHandler />
      
      {/* Navigation */}
      <nav className="app__nav">
        <div className="app__nav-container">
          <h1 className="app__title">
            <Link to="/" className="app__title-link">
              Clash Royale Deck Builder
            </Link>
          </h1>
          
          {/* Main Navigation - Always visible */}
          <ul className="app__nav-list">
            <li className="app__nav-item">
              <Link 
                to="/" 
                className={`app__nav-link ${location.pathname === '/' ? 'app__nav-link--active' : ''}`}
              >
                Deck Builder
              </Link>
            </li>
            <li className="app__nav-item">
              <Link 
                to="/saved-decks" 
                className={`app__nav-link ${location.pathname === '/saved-decks' ? 'app__nav-link--active' : ''}`}
              >
                Saved Decks
              </Link>
            </li>
            {process.env.NODE_ENV === 'development' && (
              <li className="app__nav-item">
                <Link 
                  to="/auth-demo" 
                  className={`app__nav-link ${location.pathname === '/auth-demo' ? 'app__nav-link--active' : ''}`}
                >
                  Auth Demo
                </Link>
              </li>
            )}
          </ul>
          
          {/* User Navigation */}
          <div className="app__user-section">
            {isLoading ? (
              <div className="app__user-loading">
                <div className="app__user-spinner"></div>
              </div>
            ) : isAuthenticated && user ? (
              <div className="app__user-nav">
                <div className="app__user-info">
                  {user.avatar && (
                    <img 
                      src={`https://api-assets.clashroyale.com/cards/300/${user.avatar}.png`}
                      alt={`${user.name}'s avatar`}
                      className="app__user-avatar"
                      onError={(e) => {
                        // Fallback to a default avatar if card image fails
                        e.currentTarget.style.display = 'none';
                      }}
                    />
                  )}
                  <span className="app__user-greeting">Hello, {user.name}</span>
                </div>
                <Link 
                  to="/profile" 
                  className={`app__nav-link app__nav-link--profile ${location.pathname === '/profile' ? 'app__nav-link--active' : ''}`}
                >
                  Profile
                </Link>
              </div>
            ) : (
              <div className="app__signin-section">
                <GoogleSignInButton
                  onSuccess={() => {
                    // Authentication will be handled by AuthContext
                  }}
                  onError={(error) => {
                    addNotification(`Sign in failed: ${error}`, 'error');
                  }}
                />
              </div>
            )}
          </div>
        </div>
      </nav>

      {/* Global Notifications */}
      <Notification 
        notifications={notifications}
        onDismiss={handleDismissNotification}
      />

      {/* Onboarding Modal */}
      <OnboardingModal />

      {/* Main Content */}
      <main className="app__main">
        <ErrorBoundary>
          <Routes>
            <Route 
              path="/" 
              element={
                <ErrorBoundary>
                  <DeckBuilder 
                    initialDeck={currentDeck}
                    onDeckSaved={handleDeckSaved}
                  />
                </ErrorBoundary>
              } 
            />
            <Route
              path="/saved-decks"
              element={
                <ErrorBoundary>
                  <SavedDecks
                    onSelectDeck={loadDeckIntoBuilder}
                    onNotification={addNotification}
                    refreshTrigger={refreshSavedDecks}
                  />
                </ErrorBoundary>
              }
            />
            <Route
              path="/profile"
              element={
                <ErrorBoundary>
                  <ProtectedRoute>
                    <ProfileSection />
                  </ProtectedRoute>
                </ErrorBoundary>
              }
            />
            {/* Development-only auth demo route */}
            {process.env.NODE_ENV === 'development' && (
              <Route
                path="/auth-demo"
                element={
                  <ErrorBoundary>
                    <AuthDemo />
                  </ErrorBoundary>
                }
              />
            )}
            {/* Redirect unknown routes to home */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </ErrorBoundary>
      </main>

      {/* Footer */}
      <Footer />
    </div>
  );
}

function App() {
  const clientId = GOOGLE_CLIENT_ID;
  
  if (!clientId || clientId === 'your-google-client-id.apps.googleusercontent.com') {
    console.warn('Google Client ID not configured. Google OAuth features will be disabled.');
    console.info('To enable Google OAuth, set REACT_APP_GOOGLE_CLIENT_ID in your environment variables.');
    console.info('Get your Client ID from: https://console.cloud.google.com/');
    
    return (
      <div className="app-error">
        <h1>Setup Required</h1>
        <p>Google OAuth is not configured yet.</p>
        <p>To enable authentication features:</p>
        <ol>
          <li>Go to <a href="https://console.cloud.google.com/" target="_blank" rel="noopener noreferrer">Google Cloud Console</a></li>
          <li>Create OAuth 2.0 credentials</li>
          <li>Add your Client ID to the .env file</li>
          <li>Restart the application</li>
        </ol>
        <p>For detailed instructions, see <code>ENVIRONMENT_SETUP.md</code></p>
      </div>
    );
  }

  return (
    <GoogleOAuthProvider clientId={clientId}>
      <AuthProvider>
        <OnboardingProvider>
          <Router>
            <AppContent />
          </Router>
        </OnboardingProvider>
      </AuthProvider>
    </GoogleOAuthProvider>
  );
}

export default App;