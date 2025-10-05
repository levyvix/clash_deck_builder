import { test } from '@playwright/test';

test('check nav bar actual height', async ({ page }) => {
  await page.goto('http://localhost:3000');
  await page.waitForSelector('.app__nav', { timeout: 10000 });

  const navHeight = await page.evaluate(() => {
    const nav = document.querySelector('.app__nav');
    if (!nav) return null;
    const bounds = nav.getBoundingClientRect();
    const styles = window.getComputedStyle(nav);
    return {
      bounds: bounds.toJSON(),
      computedHeight: styles.height,
      position: styles.position,
      top: styles.top,
      zIndex: styles.zIndex
    };
  });

  console.log('=== NAV BAR INFO ===');
  console.log(JSON.stringify(navHeight, null, 2));

  // Check deck section positioning
  const deckSection = await page.evaluate(() => {
    const deck = document.querySelector('.deck-builder__deck-section--sticky');
    if (!deck) return null;
    const bounds = deck.getBoundingClientRect();
    const styles = window.getComputedStyle(deck);
    return {
      bounds: bounds.toJSON(),
      computedTop: styles.top,
      computedMaxHeight: styles.maxHeight,
      position: styles.position,
      zIndex: styles.zIndex
    };
  });

  console.log('\n=== DECK SECTION INFO ===');
  console.log(JSON.stringify(deckSection, null, 2));

  // Check deck header positioning
  const deckHeader = await page.evaluate(() => {
    const header = document.querySelector('.deck-builder__deck-header');
    if (!header) return null;
    const bounds = header.getBoundingClientRect();
    return {
      bounds: bounds.toJSON(),
      text: header.textContent?.substring(0, 100)
    };
  });

  console.log('\n=== DECK HEADER INFO ===');
  console.log(JSON.stringify(deckHeader, null, 2));

  // Scroll and check again
  await page.evaluate(() => window.scrollBy(0, 300));
  await page.waitForTimeout(500);

  const afterScroll = await page.evaluate(() => {
    const nav = document.querySelector('.app__nav');
    const deck = document.querySelector('.deck-builder__deck-section--sticky');
    const header = document.querySelector('.deck-builder__deck-header');

    return {
      nav: nav ? nav.getBoundingClientRect().toJSON() : null,
      deck: deck ? deck.getBoundingClientRect().toJSON() : null,
      header: header ? header.getBoundingClientRect().toJSON() : null,
      scrollY: window.scrollY
    };
  });

  console.log('\n=== AFTER SCROLL (300px) ===');
  console.log(JSON.stringify(afterScroll, null, 2));

  await page.screenshot({ path: 'screenshots/nav-height-debug.png', fullPage: false });
});
