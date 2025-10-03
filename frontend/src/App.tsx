import { useState } from 'react';
import { BrowserRouter as Router, Route, Routes, Link, useNavigate } from 'react-router-dom';
import DeckBuilder from './components/DeckBuilder';
import SavedDecks from './components/SavedDecks';
import Notification from './components/Notification';
import ErrorBoundary from './components/ErrorBoundary';
import { Deck, DeckSlot, Notification as NotificationType } from './types';
import './App.css';

function AppContent() {
  const navigate = useNavigate();
  
  // Global state for notifications
  const [notifications, setNotifications] = useState<NotificationType[]>([]);
  
  // Global state for current deck (persists across navigation)
  const [currentDeck, setCurrentDeck] = useState<DeckSlot[]>(
    Array(8).fill(null).map(() => ({ card: null, isEvolution: false }))
  );

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

  // Handle deck saved callback
  const handleDeckSaved = () => {
    addNotification('Deck saved successfully!', 'success');
  };

  return (
    <div className="app">
      {/* Navigation */}
      <nav className="app__nav">
        <div className="app__nav-container">
          <h1 className="app__title">Clash Royale Deck Builder</h1>
          <ul className="app__nav-list">
            <li className="app__nav-item">
              <Link to="/" className="app__nav-link">Deck Builder</Link>
            </li>
            <li className="app__nav-item">
              <Link to="/saved-decks" className="app__nav-link">Saved Decks</Link>
            </li>
          </ul>
        </div>
      </nav>

      {/* Global Notifications */}
      <Notification 
        notifications={notifications}
        onDismiss={handleDismissNotification}
      />

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
                  />
                </ErrorBoundary>
              }
            />
          </Routes>
        </ErrorBoundary>
      </main>
    </div>
  );
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}

export default App;