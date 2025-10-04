/**
 * Integration tests for enhanced SavedDecks component with mixed storage support
 */

import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import SavedDecks from './SavedDecks';

// Mock the deck storage service
jest.mock('../services/deckStorageService', () => ({
    initializeDeckStorageService: jest.fn(),
    deckStorageService: {
        getAllDecks: jest.fn(),
        updateDeck: jest.fn(),
        deleteDeck: jest.fn(),
    },
    DeckStorageError: class MockDeckStorageError extends Error {
        public code: string;
        constructor(message: string, mockCode: string) {
            super(message);
            this.name = 'DeckStorageError';
            this.code = mockCode;
        }
    },
}));

// Mock useAuth hook
jest.mock('../contexts/AuthContext', () => ({
    useAuth: jest.fn(),
}));

const mockDeckStorageService = require('../services/deckStorageService').deckStorageService;
const mockUseAuth = require('../contexts/AuthContext').useAuth;

// Mock deck data
const mockLocalDeck = {
    id: 'local_123456789_abc',
    name: 'Local Test Deck',
    slots: Array(8).fill({ card: null, isEvolution: false }),
    average_elixir: 3.5,
    storageType: 'local' as const,
    created_at: '2024-01-01T00:00:00Z',
};

const mockServerDeck = {
    id: 1,
    name: 'Server Test Deck',
    slots: Array(8).fill({ card: null, isEvolution: false }),
    average_elixir: 4.0,
    storageType: 'server' as const,
    created_at: '2024-01-01T00:00:00Z',
};

describe('SavedDecks Enhanced Component', () => {
    const mockOnSelectDeck = jest.fn();
    const mockOnNotification = jest.fn();

    beforeEach(() => {
        jest.clearAllMocks();
        // Default mock for useAuth
        mockUseAuth.mockReturnValue({
            isAuthenticated: false,
            user: null,
            isLoading: false,
        });
    });

    it('should display mixed storage summary when both local and server decks exist', async () => {
        // Mock authenticated user with mixed storage
        mockUseAuth.mockReturnValue({
            isAuthenticated: true,
            user: { id: '1', name: 'Test User' },
            isLoading: false,
        });

        // Mock mixed storage scenario
        mockDeckStorageService.getAllDecks.mockResolvedValue({
            localDecks: [mockLocalDeck],
            serverDecks: [mockServerDeck],
            totalCount: 2,
            storageType: 'mixed',
        });

        render(
            <SavedDecks
                onSelectDeck={mockOnSelectDeck}
                onNotification={mockOnNotification}
            />
        );

        await waitFor(() => {
            expect(screen.getByText('Local Test Deck')).toBeInTheDocument();
            expect(screen.getByText('Server Test Deck')).toBeInTheDocument();
        });

        // Check for storage summary with new format
        expect(screen.getByText('Local')).toBeInTheDocument();
        expect(screen.getByText('Server')).toBeInTheDocument();
    });

    it('should display storage type indicators on deck cards', async () => {
        mockDeckStorageService.getAllDecks.mockResolvedValue({
            localDecks: [mockLocalDeck],
            serverDecks: [mockServerDeck],
            totalCount: 2,
            storageType: 'mixed',
        });

        render(
            <SavedDecks
                onSelectDeck={mockOnSelectDeck}
                onNotification={mockOnNotification}
            />
        );

        await waitFor(() => {
            expect(screen.getByText('Local Test Deck')).toBeInTheDocument();
            expect(screen.getByText('Server Test Deck')).toBeInTheDocument();
        });

        // Check for storage badges on deck cards
        const localBadges = screen.getAllByText('💾 Local');
        const serverBadges = screen.getAllByText('☁️ Server');

        expect(localBadges.length).toBeGreaterThan(0);
        expect(serverBadges.length).toBeGreaterThan(0);
    });

    it('should handle deck selection with storage type notification', async () => {
        mockDeckStorageService.getAllDecks.mockResolvedValue({
            localDecks: [mockLocalDeck],
            serverDecks: [],
            totalCount: 1,
            storageType: 'local',
        });

        render(
            <SavedDecks
                onSelectDeck={mockOnSelectDeck}
                onNotification={mockOnNotification}
            />
        );

        await waitFor(() => {
            expect(screen.getByText('Local Test Deck')).toBeInTheDocument();
        });

        // Click load deck button
        const loadButton = screen.getByText('Load Deck');
        fireEvent.click(loadButton);

        expect(mockOnSelectDeck).toHaveBeenCalledWith(
            expect.objectContaining({
                name: 'Local Test Deck',
                slots: expect.any(Array),
            })
        );

        expect(mockOnNotification).toHaveBeenCalledWith(
            'Loaded deck: Local Test Deck (Local)',
            'success'
        );
    });

    it('should handle rename operation for both local and server decks', async () => {
        mockDeckStorageService.getAllDecks.mockResolvedValue({
            localDecks: [mockLocalDeck],
            serverDecks: [],
            totalCount: 1,
            storageType: 'local',
        });

        mockDeckStorageService.updateDeck.mockResolvedValue({
            ...mockLocalDeck,
            name: 'Renamed Local Deck',
        });

        render(
            <SavedDecks
                onSelectDeck={mockOnSelectDeck}
                onNotification={mockOnNotification}
            />
        );

        await waitFor(() => {
            expect(screen.getByText('Local Test Deck')).toBeInTheDocument();
        });

        // Click rename button
        const renameButton = screen.getByText('Rename');
        fireEvent.click(renameButton);

        // Find and update the input
        const input = screen.getByDisplayValue('Local Test Deck');
        fireEvent.change(input, { target: { value: 'Renamed Local Deck' } });

        // Click save button (checkmark)
        const saveButton = screen.getByTitle('Save');
        fireEvent.click(saveButton);

        await waitFor(() => {
            expect(mockDeckStorageService.updateDeck).toHaveBeenCalledWith(
                'local_123456789_abc',
                { name: 'Renamed Local Deck' }
            );
        });

        expect(mockOnNotification).toHaveBeenCalledWith(
            'Deck renamed successfully',
            'success'
        );
    });

    it('should handle delete operation for both local and server decks', async () => {
        mockDeckStorageService.getAllDecks.mockResolvedValue({
            localDecks: [mockLocalDeck],
            serverDecks: [],
            totalCount: 1,
            storageType: 'local',
        });

        mockDeckStorageService.deleteDeck.mockResolvedValue(undefined);

        render(
            <SavedDecks
                onSelectDeck={mockOnSelectDeck}
                onNotification={mockOnNotification}
            />
        );

        await waitFor(() => {
            expect(screen.getByText('Local Test Deck')).toBeInTheDocument();
        });

        // Click delete button
        const deleteButton = screen.getByText('Delete');
        fireEvent.click(deleteButton);

        // Confirm deletion - get the confirmation dialog delete button (not the disabled one)
        const confirmButtons = screen.getAllByRole('button', { name: 'Delete' });
        const confirmButton = confirmButtons.find(button => !(button as HTMLButtonElement).disabled);
        fireEvent.click(confirmButton!);

        await waitFor(() => {
            expect(mockDeckStorageService.deleteDeck).toHaveBeenCalledWith('local_123456789_abc');
        });

        expect(mockOnNotification).toHaveBeenCalledWith(
            'Deck deleted successfully',
            'success'
        );
    });

    it('should display appropriate empty state for mixed storage', async () => {
        mockDeckStorageService.getAllDecks.mockResolvedValue({
            localDecks: [],
            serverDecks: [],
            totalCount: 0,
            storageType: 'mixed',
        });

        render(
            <SavedDecks
                onSelectDeck={mockOnSelectDeck}
                onNotification={mockOnNotification}
            />
        );

        await waitFor(() => {
            expect(screen.getByText('No saved decks yet')).toBeInTheDocument();
        });

        // Check for mixed storage info in empty state
        expect(screen.getByText(/Local decks are saved in your browser/)).toBeInTheDocument();
        expect(screen.getByText(/Server decks are saved to your account/)).toBeInTheDocument();
    });

    it('should handle storage errors gracefully', async () => {
        const mockError = new (require('../services/deckStorageService').DeckStorageError)(
            'Local storage is not available',
            'LOCAL_STORAGE_UNAVAILABLE'
        );

        mockDeckStorageService.getAllDecks.mockRejectedValue(mockError);

        render(
            <SavedDecks
                onSelectDeck={mockOnSelectDeck}
                onNotification={mockOnNotification}
            />
        );

        await waitFor(() => {
            expect(screen.getByText(/Local storage is not available/)).toBeInTheDocument();
        });

        expect(mockOnNotification).toHaveBeenCalledWith(
            'Local storage is not available. Please enable cookies and local storage in your browser.',
            'error'
        );
    });
});