# Anonymous Mode

Anonymous mode allows users to build and save decks without authentication, using browser localStorage.

## Overview

- Build decks without signing in
- Save decks to browser localStorage
- Maximum 20 decks (same as authenticated users)
- Data persists across browser sessions
- Migrates to server on login

## How It Works

### localStorage Structure

```typescript
// Storage key
const STORAGE_KEY = 'clash_decks_anonymous';

// Stored data format
interface AnonymousStorage {
  decks: LocalDeck[];
  version: string;
  lastUpdated: string;
}

interface LocalDeck {
  id: string;           // Format: "local-{timestamp}"
  name: string;
  slots: DeckSlot[];
  createdAt: string;
  updatedAt: string;
}
```

### Local Storage Service

```typescript
// src/services/localStorageService.ts
export const localStorageService = {
  saveDecks(decks: LocalDeck[]): void {
    const data = {
      decks,
      version: '1.0',
      lastUpdated: new Date().toISOString()
    };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  },

  getDecks(): LocalDeck[] {
    try {
      const data = localStorage.getItem(STORAGE_KEY);
      if (!data) return [];

      const parsed = JSON.parse(data);
      return parsed.decks || [];
    } catch (error) {
      console.error('Failed to load local decks:', error);
      return [];
    }
  },

  addDeck(deck: Omit<LocalDeck, 'id' | 'createdAt' | 'updatedAt'>): LocalDeck {
    const newDeck: LocalDeck = {
      ...deck,
      id: `local-${Date.now()}`,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };

    const decks = this.getDecks();
    decks.push(newDeck);
    this.saveDecks(decks);

    return newDeck;
  },

  updateDeck(id: string, updates: Partial<LocalDeck>): void {
    const decks = this.getDecks();
    const index = decks.findIndex(d => d.id === id);

    if (index !== -1) {
      decks[index] = {
        ...decks[index],
        ...updates,
        updatedAt: new Date().toISOString()
      };
      this.saveDecks(decks);
    }
  },

  deleteDeck(id: string): void {
    const decks = this.getDecks().filter(d => d.id !== id);
    this.saveDecks(decks);
  },

  clearDecks(): void {
    localStorage.removeItem(STORAGE_KEY);
  }
};
```

## Unified Storage Service

The `DeckStorageService` provides a single interface for both anonymous and authenticated users:

```typescript
class DeckStorageService {
  private authStateProvider: () => boolean;

  constructor(authStateProvider: () => boolean) {
    this.authStateProvider = authStateProvider;
  }

  async getAllDecks(): Promise<UnifiedDeck[]> {
    if (this.authStateProvider()) {
      // Authenticated - use server
      return await this.getServerDecks();
    } else {
      // Anonymous - use localStorage
      return await this.getLocalDecks();
    }
  }

  async saveDeck(deck: DeckInput): Promise<DeckStorageResult> {
    if (this.authStateProvider()) {
      return await this.saveToServer(deck);
    } else {
      return await this.saveToLocal(deck);
    }
  }

  private async getLocalDecks(): Promise<UnifiedDeck[]> {
    const localDecks = localStorageService.getDecks();
    return localDecks.map(d => ({
      ...d,
      storageType: 'local' as const
    }));
  }

  private async saveToLocal(deck: DeckInput): Promise<DeckStorageResult> {
    const saved = localStorageService.addDeck(deck);
    return {
      success: true,
      deck: { ...saved, storageType: 'local' },
      storageType: 'local'
    };
  }
}
```

## Migration on Login

When a user logs in, their local decks are migrated to the server:

```typescript
// src/services/migration_service.ts (frontend)
async function migrateLocalDecksOnLogin(): Promise<MigrationResult> {
  const localDecks = localStorageService.getDecks();

  if (localDecks.length === 0) {
    return { migrated: 0, failed: 0 };
  }

  let migrated = 0;
  let failed = 0;

  for (const localDeck of localDecks) {
    try {
      // Transform local format to backend format
      const backendDeck = transformDeckForBackend(localDeck);

      // Save to server
      await createDeck(backendDeck);
      migrated++;
    } catch (error) {
      console.error(`Failed to migrate deck "${localDeck.name}":`, error);
      failed++;
    }
  }

  // Clear local storage after successful migration
  if (migrated > 0) {
    localStorageService.clearDecks();
  }

  return { migrated, failed };
}

// Call during login process
async function handleLogin(idToken: string) {
  const authResponse = await loginWithGoogle(idToken);

  // Show migration results
  const migrationResult = await migrateLocalDecksOnLogin();

  if (migrationResult.migrated > 0) {
    showNotification(`${migrationResult.migrated} decks migrated to your account!`);
  }

  if (migrationResult.failed > 0) {
    showWarning(`${migrationResult.failed} decks could not be migrated`);
  }
}
```

## UI Indicators

### Storage Type Badge

```typescript
function DeckCard({ deck }: { deck: UnifiedDeck }) {
  return (
    <div className="deck-card">
      <h3>{deck.name}</h3>

      {deck.storageType === 'local' && (
        <span className="storage-badge storage-badge--local">
          Local
        </span>
      )}

      {deck.storageType === 'server' && (
        <span className="storage-badge storage-badge--server">
          Saved
        </span>
      )}
    </div>
  );
}
```

### Anonymous User Notice

```typescript
function WelcomeMessage() {
  const { isAuthenticated } = useAuth();

  if (isAuthenticated) return null;

  return (
    <div className="notice notice--info">
      <p>
        You're building as a guest. Your decks are saved in your browser.
      </p>
      <p>
        <strong>Sign in with Google</strong> to save decks to your account
        and access them from any device.
      </p>
      <GoogleSignInButton />
    </div>
  );
}
```

## Storage Limits

### Browser Quota

localStorage has a 5-10MB limit per domain:

```typescript
function checkStorageQuota(): { used: number; available: number } {
  let used = 0;

  for (const key in localStorage) {
    if (localStorage.hasOwnProperty(key)) {
      used += localStorage[key].length + key.length;
    }
  }

  return {
    used: used,
    available: 5 * 1024 * 1024  // Assume 5MB limit
  };
}

// Warn user if approaching limit
function checkAndWarnStorageLimit() {
  const quota = checkStorageQuota();
  const percentUsed = (quota.used / quota.available) * 100;

  if (percentUsed > 80) {
    showWarning('Your browser storage is almost full. Sign in to save decks to the cloud.');
  }
}
```

### Deck Limit

Same 20 deck limit as authenticated users:

```typescript
function canSaveNewDeck(): boolean {
  const decks = localStorageService.getDecks();
  return decks.length < 20;
}

// UI
{!canSaveNewDeck() && (
  <p className="warning">
    You've reached the maximum of 20 saved decks.
    Sign in to increase your storage capacity.
  </p>
)}
```

## Error Handling

```typescript
export class LocalStorageError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'LocalStorageError';
  }
}

try {
  localStorageService.saveDecks(decks);
} catch (error) {
  if (error instanceof LocalStorageError) {
    // Show user-friendly message
    showError('Failed to save deck to browser storage. Please try again.');

    // Prompt to sign in
    showNotification('Sign in to save decks to the cloud instead.');
  }
}
```

## Privacy Considerations

- Data stored only in user's browser
- No data sent to server unless user logs in
- User can clear browser data anytime
- Migration to server is optional

## Testing

```typescript
describe('Anonymous Mode', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('saves deck to localStorage', () => {
    const deck = { name: 'Test', slots: mockSlots() };
    localStorageService.addDeck(deck);

    const saved = localStorageService.getDecks();
    expect(saved).toHaveLength(1);
    expect(saved[0].name).toBe('Test');
  });

  it('migrates local decks on login', async () => {
    // Setup: Add local decks
    localStorageService.addDeck(mockDeck());
    localStorageService.addDeck(mockDeck());

    // Simulate login
    await handleLogin('mock-token');

    // Verify migration
    const localDecks = localStorageService.getDecks();
    expect(localDecks).toHaveLength(0);  // Cleared after migration

    const serverDecks = await fetchDecks();
    expect(serverDecks).toHaveLength(2);  // Migrated to server
  });
});
```

## Related Documentation

- [Deck Management](deck-management.md) - Overall deck system
- [Google OAuth](google-oauth.md) - Authentication and migration
- [Frontend Architecture](../architecture/frontend.md) - Storage architecture
