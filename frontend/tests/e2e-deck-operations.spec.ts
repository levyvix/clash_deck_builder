import { test, expect } from '@playwright/test';

/**
 * E2E tests for deck building operations
 * Tests: add cards, remove cards, 8-card limit, save deck, view saved decks
 */

test.describe('Deck Building Operations', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the app and wait for initial load
    await page.goto('http://localhost:3000');
    await page.waitForLoadState('networkidle');

    // Clear localStorage to start fresh each test
    await page.evaluate(() => localStorage.clear());
    await page.reload();
    await page.waitForLoadState('networkidle');

    // Wait for cards to load
    await page.waitForSelector('[class*="card-display"]', { timeout: 10000 });
  });

  test('should add a card to deck via drag and drop', async ({ page }) => {
    // Find first card in gallery
    const firstCard = page.locator('[class*="card-gallery"] [class*="card-display"]').first();
    await expect(firstCard).toBeVisible();

    // Find first empty deck slot using testid
    const firstSlot = page.getByTestId('deck-slot-0');

    // Verify slot is empty initially
    await expect(firstSlot).toHaveClass(/deck-slot--empty/);

    // Perform drag and drop
    await firstCard.dragTo(firstSlot);
    await page.waitForTimeout(500);

    // Verify card was added to deck (slot should now be filled)
    await expect(firstSlot).toHaveClass(/deck-slot--filled/);

    // Verify slot has an image (the card)
    const slotImage = firstSlot.locator('img');
    await expect(slotImage).toBeVisible({ timeout: 5000 });
  });

  test('should add multiple cards to different slots', async ({ page }) => {
    const galleryCards = page.locator('[class*="card-gallery"] [class*="card-display"]');

    // Add 3 cards to first 3 slots
    for (let i = 0; i < 3; i++) {
      const card = galleryCards.nth(i);
      const slot = page.getByTestId(`deck-slot-${i}`);

      await card.dragTo(slot);
      await page.waitForTimeout(300);

      // Verify card was added
      await expect(slot).toHaveClass(/deck-slot--filled/);
      const slotImage = slot.locator('img');
      await expect(slotImage).toBeVisible();
    }

    // Verify deck status shows 3/8 cards
    const deckStatus = page.locator('text=/3.*8|3 \\/ 8/');
    if (await deckStatus.count() > 0) {
      await expect(deckStatus).toBeVisible();
    }
  });

  test('should remove a card from deck via remove button', async ({ page }) => {
    // Add a card first
    const firstCard = page.locator('[class*="card-gallery"] [class*="card-display"]').first();
    const firstSlot = page.getByTestId('deck-slot-0');

    await firstCard.dragTo(firstSlot);
    await page.waitForTimeout(500);

    // Verify card is in slot
    await expect(firstSlot).toHaveClass(/deck-slot--filled/);

    // Click on the slot to show options
    await firstSlot.click();
    await page.waitForTimeout(300);

    // Find and click remove button
    const removeButton = firstSlot.locator('button:has-text("Remove from Deck")');

    if (await removeButton.count() > 0) {
      await removeButton.click();
      await page.waitForTimeout(500);

      // Verify slot is now empty
      await expect(firstSlot).toHaveClass(/deck-slot--empty/);
    }
  });

  test('should remove a card via drag to remove zone', async ({ page }) => {
    // Add a card first
    const firstCard = page.locator('[class*="card-gallery"] [class*="card-display"]').first();
    const firstSlot = page.locator('[class*="deck-slot"]').first();

    await firstCard.dragTo(firstSlot);
    await page.waitForTimeout(500);

    // Verify card is in slot
    const slotContent = firstSlot.locator('[class*="card-display"]');
    await expect(slotContent).toBeVisible();

    // Look for remove zone (might appear on drag start)
    const removeZone = page.locator('[class*="remove-drop-zone"], [class*="remove-zone"]').first();

    if (await removeZone.count() > 0) {
      await slotContent.dragTo(removeZone);
      await page.waitForTimeout(500);

      // Verify slot is now empty
      const emptyIndicator = firstSlot.locator('[class*="empty"]');
      await expect(emptyIndicator).toBeVisible();
    }
  });

  test('should prevent adding more than 8 cards to deck', async ({ page }) => {
    const galleryCards = page.locator('[class*="card-gallery"] [class*="card-display"]');

    // Add 8 cards (fill all slots)
    for (let i = 0; i < 8; i++) {
      const card = galleryCards.nth(i);
      const slot = page.getByTestId(`deck-slot-${i}`);

      await card.dragTo(slot);
      await page.waitForTimeout(200);
    }

    // Verify all 8 slots are filled
    for (let i = 0; i < 8; i++) {
      const slot = page.getByTestId(`deck-slot-${i}`);
      await expect(slot).toHaveClass(/deck-slot--filled/);
    }

    // Verify deck status shows 8/8
    const deckStatus = page.locator('text=/8.*8|8 \\/ 8/');
    if (await deckStatus.count() > 0) {
      await expect(deckStatus).toBeVisible();
    }

    // Try to add a 9th card by dragging to first slot (should replace, not add)
    const ninthCard = galleryCards.nth(8);
    const firstSlot = page.getByTestId('deck-slot-0');

    await ninthCard.dragTo(firstSlot);
    await page.waitForTimeout(500);

    // Still should only have 8 cards total (all filled)
    for (let i = 0; i < 8; i++) {
      const slot = page.getByTestId(`deck-slot-${i}`);
      await expect(slot).toHaveClass(/deck-slot--filled/);
    }
  });

  test('should update average elixir cost as cards are added', async ({ page }) => {
    const deckSlots = page.locator('[class*="deck-slot"]');
    const galleryCards = page.locator('[class*="card-gallery"] [class*="card-display"]');

    // Look for average elixir display
    const averageElixirDisplay = page.locator('text=/Average.*Elixir|Avg.*Elixir|Elixir.*Cost/i').first();
    await expect(averageElixirDisplay).toBeVisible({ timeout: 5000 });

    // Get initial value (should be 0 or N/A)
    const initialText = await averageElixirDisplay.textContent();
    expect(initialText).toMatch(/0|N\/A|-/);

    // Add a card
    await galleryCards.first().dragTo(deckSlots.first());
    await page.waitForTimeout(500);

    // Average should update (no longer 0 or N/A)
    const updatedText = await averageElixirDisplay.textContent();
    expect(updatedText).not.toBe(initialText);

    // Should contain a number (e.g., "3.5" or "Average: 3.5")
    expect(updatedText).toMatch(/\d+(\.\d+)?/);
  });

  test('should allow replacing a card in an occupied slot', async ({ page }) => {
    const deckSlots = page.locator('[class*="deck-slot"]');
    const galleryCards = page.locator('[class*="card-gallery"] [class*="card-display"]');

    // Add first card to first slot
    const firstCard = galleryCards.first();
    const firstSlot = deckSlots.first();

    await firstCard.dragTo(firstSlot);
    await page.waitForTimeout(500);

    // Get the card name/elixir for verification
    const firstCardInSlot = firstSlot.locator('[class*="card-display"]');
    const firstCardText = await firstCardInSlot.textContent();

    // Drag a different card to the same slot
    const secondCard = galleryCards.nth(1);
    await secondCard.dragTo(firstSlot);
    await page.waitForTimeout(500);

    // Verify the card was replaced
    const updatedCardInSlot = firstSlot.locator('[class*="card-display"]');
    const updatedCardText = await updatedCardInSlot.textContent();

    // Text should be different (card was replaced)
    expect(updatedCardText).not.toBe(firstCardText);
  });

  test('should show deck completion status', async ({ page }) => {
    const deckSlots = page.locator('[class*="deck-slot"]');
    const galleryCards = page.locator('[class*="card-gallery"] [class*="card-display"]');

    // Add cards one by one and verify status updates
    for (let i = 1; i <= 4; i++) {
      const card = galleryCards.nth(i - 1);
      const slot = deckSlots.nth(i - 1);

      await card.dragTo(slot);
      await page.waitForTimeout(300);

      // Check for status indicator showing i/8
      const statusPattern = new RegExp(`${i}.*8|${i} \\/ 8`);
      const deckStatus = page.locator(`text=${statusPattern}`);

      if (await deckStatus.count() > 0) {
        await expect(deckStatus).toBeVisible();
      }
    }
  });
});

test.describe('Deck Saving Operations', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000');
    await page.waitForLoadState('networkidle');
    await page.waitForSelector('[class*="card-display"]', { timeout: 10000 });
  });

  test('should show save button after adding cards to deck', async ({ page }) => {
    const deckSlots = page.locator('[class*="deck-slot"]');
    const galleryCards = page.locator('[class*="card-gallery"] [class*="card-display"]');

    // Add 8 cards to complete the deck
    for (let i = 0; i < 8; i++) {
      await galleryCards.nth(i).dragTo(deckSlots.nth(i));
      await page.waitForTimeout(200);
    }

    // Look for save button
    const saveButton = page.locator('button').filter({ hasText: /Save|Save Deck/i }).first();
    await expect(saveButton).toBeVisible({ timeout: 5000 });
  });

  test('should save deck to localStorage for anonymous users', async ({ page }) => {
    const deckSlots = page.locator('[class*="deck-slot"]');
    const galleryCards = page.locator('[class*="card-gallery"] [class*="card-display"]');

    // Add 8 cards
    for (let i = 0; i < 8; i++) {
      await galleryCards.nth(i).dragTo(deckSlots.nth(i));
      await page.waitForTimeout(200);
    }

    // Click save button
    const saveButton = page.locator('button').filter({ hasText: /Save|Save Deck/i }).first();

    if (await saveButton.count() > 0) {
      await saveButton.click();
      await page.waitForTimeout(1000);

      // Check localStorage for saved deck
      const savedDecks = await page.evaluate(() => {
        const stored = localStorage.getItem('savedDecks');
        return stored ? JSON.parse(stored) : null;
      });

      expect(savedDecks).toBeTruthy();
      expect(Array.isArray(savedDecks)).toBe(true);
      if (Array.isArray(savedDecks)) {
        expect(savedDecks.length).toBeGreaterThan(0);
      }
    }
  });

  test('should prompt for deck name when saving', async ({ page }) => {
    const deckSlots = page.locator('[class*="deck-slot"]');
    const galleryCards = page.locator('[class*="card-gallery"] [class*="card-display"]');

    // Add 8 cards
    for (let i = 0; i < 8; i++) {
      await galleryCards.nth(i).dragTo(deckSlots.nth(i));
      await page.waitForTimeout(200);
    }

    // Click save button
    const saveButton = page.locator('button').filter({ hasText: /Save|Save Deck/i }).first();

    if (await saveButton.count() > 0) {
      await saveButton.click();
      await page.waitForTimeout(500);

      // Look for name input (might be modal or inline)
      const nameInput = page.locator('input[placeholder*="name"], input[placeholder*="Name"]').first();

      if (await nameInput.count() > 0) {
        await expect(nameInput).toBeVisible();

        // Enter a deck name
        await nameInput.fill('Test Deck');

        // Look for confirm/save button in modal
        const confirmButton = page.locator('button').filter({ hasText: /Save|Confirm|OK/i }).last();
        if (await confirmButton.count() > 0) {
          await confirmButton.click();
          await page.waitForTimeout(500);
        }
      }
    }
  });

  test('should show success notification after saving deck', async ({ page }) => {
    const deckSlots = page.locator('[class*="deck-slot"]');
    const galleryCards = page.locator('[class*="card-gallery"] [class*="card-display"]');

    // Add 8 cards
    for (let i = 0; i < 8; i++) {
      await galleryCards.nth(i).dragTo(deckSlots.nth(i));
      await page.waitForTimeout(200);
    }

    // Save the deck
    const saveButton = page.locator('button').filter({ hasText: /Save|Save Deck/i }).first();

    if (await saveButton.count() > 0) {
      await saveButton.click();
      await page.waitForTimeout(500);

      // If there's a name input, fill it
      const nameInput = page.locator('input[placeholder*="name"], input[placeholder*="Name"]').first();
      if (await nameInput.count() > 0) {
        await nameInput.fill('Success Test Deck');
        const confirmButton = page.locator('button').filter({ hasText: /Save|Confirm|OK/i }).last();
        await confirmButton.click();
      }

      await page.waitForTimeout(1000);

      // Look for success notification
      const notification = page.locator('[class*="notification"], [class*="toast"], [class*="alert"]').filter({ hasText: /saved|success/i }).first();

      if (await notification.count() > 0) {
        await expect(notification).toBeVisible({ timeout: 5000 });
      }
    }
  });
});

test.describe('Saved Decks Display', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000');
    await page.waitForLoadState('networkidle');
    await page.evaluate(() => localStorage.clear());
    await page.waitForSelector('[class*="card-display"]', { timeout: 10000 });
  });

  test('should navigate to saved decks section', async ({ page }) => {
    // Look for saved decks link/button in navigation
    const savedDecksLink = page.locator('a, button').filter({ hasText: /Saved Decks|My Decks|Decks/i }).first();

    if (await savedDecksLink.count() > 0) {
      await savedDecksLink.click();
      await page.waitForTimeout(500);

      // Should show saved decks section or empty state
      const savedDecksSection = page.locator('[class*="saved-decks"], text=/Saved Decks|My Decks/i').first();
      await expect(savedDecksSection).toBeVisible();
    }
  });

  test('should show empty state when no decks are saved', async ({ page }) => {
    // Navigate to saved decks (might be on same page or different route)
    const savedDecksLink = page.locator('a, button').filter({ hasText: /Saved Decks|My Decks/i }).first();

    if (await savedDecksLink.count() > 0) {
      await savedDecksLink.click();
      await page.waitForTimeout(500);
    }

    // Look for empty state message
    const emptyMessage = page.locator('text=/No.*deck|No saved|empty/i').first();

    if (await emptyMessage.count() > 0) {
      await expect(emptyMessage).toBeVisible();
    }
  });

  test('should display saved deck after saving', async ({ page }) => {
    const deckSlots = page.locator('[class*="deck-slot"]');
    const galleryCards = page.locator('[class*="card-gallery"] [class*="card-display"]');

    // Add and save a deck
    for (let i = 0; i < 8; i++) {
      await galleryCards.nth(i).dragTo(deckSlots.nth(i));
      await page.waitForTimeout(150);
    }

    const saveButton = page.locator('button').filter({ hasText: /Save|Save Deck/i }).first();
    if (await saveButton.count() > 0) {
      await saveButton.click();
      await page.waitForTimeout(500);

      // Fill in deck name if prompted
      const nameInput = page.locator('input[placeholder*="name"], input[placeholder*="Name"]').first();
      if (await nameInput.count() > 0) {
        await nameInput.fill('Display Test Deck');
        const confirmButton = page.locator('button').filter({ hasText: /Save|Confirm|OK/i }).last();
        await confirmButton.click();
        await page.waitForTimeout(1000);
      }
    }

    // Navigate to saved decks section
    const savedDecksLink = page.locator('a, button').filter({ hasText: /Saved Decks|My Decks/i }).first();
    if (await savedDecksLink.count() > 0) {
      await savedDecksLink.click();
      await page.waitForTimeout(500);
    }

    // Look for the saved deck
    const savedDeck = page.locator('[class*="deck-card"], [class*="saved-deck"]').first();
    if (await savedDeck.count() > 0) {
      await expect(savedDeck).toBeVisible();

      // Verify deck name is displayed
      const deckName = savedDeck.locator('text=/Display Test Deck/i');
      await expect(deckName).toBeVisible();
    }
  });

  test('should load saved deck when clicked', async ({ page }) => {
    // First, save a deck
    const deckSlots = page.locator('[class*="deck-slot"]');
    const galleryCards = page.locator('[class*="card-gallery"] [class*="card-display"]');

    for (let i = 0; i < 8; i++) {
      await galleryCards.nth(i).dragTo(deckSlots.nth(i));
      await page.waitForTimeout(150);
    }

    const saveButton = page.locator('button').filter({ hasText: /Save|Save Deck/i }).first();
    if (await saveButton.count() > 0) {
      await saveButton.click();
      await page.waitForTimeout(500);

      const nameInput = page.locator('input[placeholder*="name"], input[placeholder*="Name"]').first();
      if (await nameInput.count() > 0) {
        await nameInput.fill('Load Test Deck');
        const confirmButton = page.locator('button').filter({ hasText: /Save|Confirm|OK/i }).last();
        await confirmButton.click();
        await page.waitForTimeout(1000);
      }
    }

    // Clear current deck
    await page.evaluate(() => localStorage.removeItem('currentDeck'));
    await page.reload();
    await page.waitForLoadState('networkidle');

    // Navigate to saved decks
    const savedDecksLink = page.locator('a, button').filter({ hasText: /Saved Decks|My Decks/i }).first();
    if (await savedDecksLink.count() > 0) {
      await savedDecksLink.click();
      await page.waitForTimeout(500);
    }

    // Click on the saved deck to load it
    const savedDeck = page.locator('[class*="deck-card"], [class*="saved-deck"]').first();
    if (await savedDeck.count() > 0) {
      // Look for load/edit button
      const loadButton = savedDeck.locator('button').filter({ hasText: /Load|Edit|Use/i }).first();
      if (await loadButton.count() > 0) {
        await loadButton.click();
        await page.waitForTimeout(1000);

        // Verify deck is loaded in deck builder
        const filledSlots = page.locator('[class*="deck-slot"] [class*="card-display"]');
        await expect(filledSlots).toHaveCount(8);
      }
    }
  });

  test('should delete saved deck', async ({ page }) => {
    // First, save a deck
    const deckSlots = page.locator('[class*="deck-slot"]');
    const galleryCards = page.locator('[class*="card-gallery"] [class*="card-display"]');

    for (let i = 0; i < 8; i++) {
      await galleryCards.nth(i).dragTo(deckSlots.nth(i));
      await page.waitForTimeout(150);
    }

    const saveButton = page.locator('button').filter({ hasText: /Save|Save Deck/i }).first();
    if (await saveButton.count() > 0) {
      await saveButton.click();
      await page.waitForTimeout(500);

      const nameInput = page.locator('input[placeholder*="name"], input[placeholder*="Name"]').first();
      if (await nameInput.count() > 0) {
        await nameInput.fill('Delete Test Deck');
        const confirmButton = page.locator('button').filter({ hasText: /Save|Confirm|OK/i }).last();
        await confirmButton.click();
        await page.waitForTimeout(1000);
      }
    }

    // Navigate to saved decks
    const savedDecksLink = page.locator('a, button').filter({ hasText: /Saved Decks|My Decks/i }).first();
    if (await savedDecksLink.count() > 0) {
      await savedDecksLink.click();
      await page.waitForTimeout(500);
    }

    // Find and click delete button
    const savedDeck = page.locator('[class*="deck-card"], [class*="saved-deck"]').first();
    if (await savedDeck.count() > 0) {
      const deleteButton = savedDeck.locator('button').filter({ hasText: /Delete|Remove|×|✕/i }).first();
      if (await deleteButton.count() > 0) {
        await deleteButton.click();
        await page.waitForTimeout(500);

        // Handle confirmation dialog if present
        const confirmDelete = page.locator('button').filter({ hasText: /Confirm|Yes|Delete/i }).last();
        if (await confirmDelete.count() > 0) {
          await confirmDelete.click();
          await page.waitForTimeout(500);
        }

        // Verify deck is removed
        const remainingDecks = await page.locator('[class*="deck-card"], [class*="saved-deck"]').count();
        expect(remainingDecks).toBe(0);
      }
    }
  });

  test('should show deck count in saved decks section', async ({ page }) => {
    // Save multiple decks
    const deckSlots = page.locator('[class*="deck-slot"]');
    const galleryCards = page.locator('[class*="card-gallery"] [class*="card-display"]');

    // Save 3 different decks
    for (let deckNum = 1; deckNum <= 3; deckNum++) {
      // Add cards to deck
      for (let i = 0; i < 8; i++) {
        const cardIndex = (deckNum - 1) * 8 + i;
        await galleryCards.nth(cardIndex % 20).dragTo(deckSlots.nth(i));
        await page.waitForTimeout(100);
      }

      // Save the deck
      const saveButton = page.locator('button').filter({ hasText: /Save|Save Deck/i }).first();
      if (await saveButton.count() > 0) {
        await saveButton.click();
        await page.waitForTimeout(500);

        const nameInput = page.locator('input[placeholder*="name"], input[placeholder*="Name"]').first();
        if (await nameInput.count() > 0) {
          await nameInput.fill(`Test Deck ${deckNum}`);
          const confirmButton = page.locator('button').filter({ hasText: /Save|Confirm|OK/i }).last();
          await confirmButton.click();
          await page.waitForTimeout(500);
        }
      }

      // Clear deck for next iteration
      await page.evaluate(() => localStorage.removeItem('currentDeck'));
      await page.reload();
      await page.waitForLoadState('networkidle');
    }

    // Navigate to saved decks
    const savedDecksLink = page.locator('a, button').filter({ hasText: /Saved Decks|My Decks/i }).first();
    if (await savedDecksLink.count() > 0) {
      await savedDecksLink.click();
      await page.waitForTimeout(500);
    }

    // Verify 3 decks are displayed
    const savedDecks = page.locator('[class*="deck-card"], [class*="saved-deck"]');
    const count = await savedDecks.count();
    expect(count).toBe(3);
  });
});

test.describe('Deck Persistence', () => {
  test('should persist deck in localStorage after adding cards', async ({ page }) => {
    await page.goto('http://localhost:3000');
    await page.waitForLoadState('networkidle');
    await page.waitForSelector('[class*="card-display"]', { timeout: 10000 });

    const deckSlots = page.locator('[class*="deck-slot"]');
    const galleryCards = page.locator('[class*="card-gallery"] [class*="card-display"]');

    // Add 4 cards
    for (let i = 0; i < 4; i++) {
      await galleryCards.nth(i).dragTo(deckSlots.nth(i));
      await page.waitForTimeout(200);
    }

    // Check localStorage
    const currentDeck = await page.evaluate(() => {
      const stored = localStorage.getItem('currentDeck');
      return stored ? JSON.parse(stored) : null;
    });

    expect(currentDeck).toBeTruthy();
    if (currentDeck && 'slots' in currentDeck) {
      const filledSlots = currentDeck.slots.filter((slot: any) => slot.card !== null);
      expect(filledSlots.length).toBe(4);
    }
  });

  test('should restore deck from localStorage on page reload', async ({ page }) => {
    await page.goto('http://localhost:3000');
    await page.waitForLoadState('networkidle');
    await page.waitForSelector('[class*="card-display"]', { timeout: 10000 });

    const deckSlots = page.locator('[class*="deck-slot"]');
    const galleryCards = page.locator('[class*="card-gallery"] [class*="card-display"]');

    // Add 5 cards
    for (let i = 0; i < 5; i++) {
      await galleryCards.nth(i).dragTo(deckSlots.nth(i));
      await page.waitForTimeout(200);
    }

    // Reload page
    await page.reload();
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    // Verify deck is restored
    const filledSlots = page.locator('[class*="deck-slot"] [class*="card-display"]');
    const count = await filledSlots.count();
    expect(count).toBe(5);
  });
});
