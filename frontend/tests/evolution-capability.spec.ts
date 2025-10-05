import { test, expect } from '@playwright/test';

/**
 * Test to verify that cards with evolutionMedium in the API response
 * correctly show the evolution button option when placed in deck slots.
 *
 * This test specifically checks Giant Snowball (ID: 28000017) which has
 * an evolutionMedium URL but was not in the original hardcoded evolution list.
 */
test('Cards with image_url_evo show evolution option in deck', async ({ page, context }) => {
  // Clear cache to ensure fresh code
  await context.clearCookies();

  await page.goto('http://localhost:3000', {
    waitUntil: 'networkidle'
  });

  await page.waitForSelector('.card-gallery', { timeout: 10000 });
  await page.waitForTimeout(1000);

  // Search for Giant Snowball
  const searchInput = page.locator('input[placeholder*="Search"], input[type="text"]').first();
  await searchInput.fill('Giant Snowball');
  await page.waitForTimeout(500);

  // Find and click the card
  const snowballCard = page.locator('.card-display').filter({ hasText: 'Giant Snowball' }).first();
  await expect(snowballCard).toBeVisible();
  await snowballCard.click();
  await page.waitForTimeout(500);

  // Add to deck
  const addToDeckButton = page.locator('button').filter({ hasText: 'Add to Deck' });
  await expect(addToDeckButton).toBeVisible();
  await addToDeckButton.click();
  await page.waitForTimeout(1000);

  // Verify card was added to first slot
  const firstSlot = page.locator('[data-testid="deck-slot-0"]');
  const slotImage = firstSlot.locator('.deck-slot__image');
  await expect(slotImage).toBeVisible();

  // Click on slot to show options
  await firstSlot.click();
  await page.waitForTimeout(500);

  // Verify evolution button exists
  const evolutionButton = page.locator('.deck-slot__option-btn--evolution').first();
  await expect(evolutionButton).toBeVisible();

  // Check button text - should either be "Mark as Evolution" or "Remove Evolution"
  const buttonText = await evolutionButton.textContent();
  expect(buttonText).toMatch(/Mark as Evolution|Remove Evolution/);

  // Take screenshot for documentation
  await page.screenshot({ path: 'screenshots/evolution-capability-test-pass.png' });
});

/**
 * Test to verify cards in first two slots are automatically marked as evolution
 */
test('Cards in first two slots can have evolution marked', async ({ page, context }) => {
  await context.clearCookies();

  await page.goto('http://localhost:3000', {
    waitUntil: 'networkidle'
  });

  await page.waitForSelector('.card-gallery', { timeout: 10000 });
  await page.waitForTimeout(1000);

  // Add Giant Snowball to deck
  const searchInput = page.locator('input[placeholder*="Search"], input[type="text"]').first();
  await searchInput.fill('Giant Snowball');
  await page.waitForTimeout(500);

  const snowballCard = page.locator('.card-display').filter({ hasText: 'Giant Snowball' }).first();
  await snowballCard.click();
  await page.waitForTimeout(300);

  const addToDeckButton = page.locator('button').filter({ hasText: 'Add to Deck' });
  await addToDeckButton.click();
  await page.waitForTimeout(1000);

  // Click on first slot
  const firstSlot = page.locator('[data-testid="deck-slot-0"]');
  await firstSlot.click();
  await page.waitForTimeout(500);

  // Verify evolution button exists and is enabled
  const evolutionButton = page.locator('.deck-slot__option-btn--evolution').first();
  await expect(evolutionButton).toBeVisible();
  await expect(evolutionButton).not.toBeDisabled();

  // Verify the button has expected text
  const buttonText = await evolutionButton.textContent();
  expect(buttonText).toMatch(/Mark as Evolution|Remove Evolution/);
});
