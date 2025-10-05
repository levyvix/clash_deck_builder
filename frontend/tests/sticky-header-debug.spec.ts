import { test, expect } from '@playwright/test';

test('investigate sticky deck header blocking cards count and avg elixir', async ({ page }) => {
  // Navigate to the application
  await page.goto('http://localhost:3000');

  // Wait for the deck builder to load
  await page.waitForSelector('.deck-builder', { timeout: 10000 });

  // Take initial screenshot
  await page.screenshot({ path: 'screenshots/01-initial-load.png', fullPage: true });

  // Find the deck stats area (cards count and avg elixir)
  const deckStats = page.locator('.deck-stats, .deck-info, [class*="elixir"], [class*="card-count"]');
  const deckStatsCount = await deckStats.count();

  console.log(`Found ${deckStatsCount} deck stats elements`);

  // Get all elements that might contain stats
  const allDeckRelated = await page.locator('[class*="deck"]').all();
  for (let i = 0; i < allDeckRelated.length && i < 10; i++) {
    const classes = await allDeckRelated[i].getAttribute('class');
    const text = await allDeckRelated[i].textContent();
    console.log(`Deck element ${i}: classes="${classes}", text="${text?.substring(0, 50)}"`);
  }

  // Check for sticky elements
  const stickyElements = await page.evaluate(() => {
    const elements = document.querySelectorAll('*');
    const sticky: Array<{tag: string, classes: string, position: string, top: string, zIndex: string, bounds: DOMRect}> = [];

    elements.forEach(el => {
      const style = window.getComputedStyle(el);
      if (style.position === 'sticky' || style.position === 'fixed') {
        sticky.push({
          tag: el.tagName,
          classes: el.className,
          position: style.position,
          top: style.top,
          zIndex: style.zIndex,
          bounds: el.getBoundingClientRect().toJSON()
        });
      }
    });

    return sticky;
  });

  console.log('\n=== STICKY/FIXED ELEMENTS ===');
  stickyElements.forEach((el, i) => {
    console.log(`\nElement ${i}:`);
    console.log(`  Tag: ${el.tag}`);
    console.log(`  Classes: ${el.classes}`);
    console.log(`  Position: ${el.position}`);
    console.log(`  Top: ${el.top}`);
    console.log(`  Z-Index: ${el.zIndex}`);
    console.log(`  Bounds:`, el.bounds);
  });

  // Get bounding boxes of key elements
  const deckBuilderBox = await page.locator('.deck-builder').first().boundingBox();
  console.log('\n=== DECK BUILDER BOUNDS ===');
  console.log('Deck Builder:', deckBuilderBox);

  // Look for cards count and elixir elements
  const elixirElements = await page.locator('[class*="elixir"], [class*="average"]').all();
  console.log('\n=== ELIXIR/STATS ELEMENTS ===');
  for (let i = 0; i < elixirElements.length; i++) {
    const box = await elixirElements[i].boundingBox();
    const classes = await elixirElements[i].getAttribute('class');
    const text = await elixirElements[i].textContent();
    console.log(`Element ${i}: classes="${classes}", text="${text}", bounds:`, box);
  }

  // Scroll down to see if anything changes
  await page.evaluate(() => window.scrollBy(0, 200));
  await page.waitForTimeout(500);
  await page.screenshot({ path: 'screenshots/02-after-scroll.png', fullPage: true });

  // Check what's blocking the stats
  const blockingCheck = await page.evaluate(() => {
    // Find elements with text containing "Cards" or "Elixir"
    const walker = document.createTreeWalker(
      document.body,
      NodeFilter.SHOW_TEXT,
      null
    );

    const results: Array<{text: string, parentClass: string, visible: boolean, bounds: DOMRect}> = [];
    let node;

    while (node = walker.nextNode()) {
      const text = node.textContent?.trim() || '';
      if (text.match(/Cards|Elixir|Average|\/\s*8/i)) {
        const parent = node.parentElement;
        if (parent) {
          const style = window.getComputedStyle(parent);
          const bounds = parent.getBoundingClientRect();
          results.push({
            text,
            parentClass: parent.className,
            visible: style.display !== 'none' && style.visibility !== 'hidden',
            bounds: bounds.toJSON()
          });
        }
      }
    }

    return results;
  });

  console.log('\n=== STATS TEXT ELEMENTS ===');
  blockingCheck.forEach((el, i) => {
    console.log(`\nElement ${i}:`);
    console.log(`  Text: ${el.text}`);
    console.log(`  Parent Class: ${el.parentClass}`);
    console.log(`  Visible: ${el.visible}`);
    console.log(`  Bounds:`, el.bounds);
  });

  // Check z-index stacking
  const zIndexCheck = await page.evaluate(() => {
    const deckBuilder = document.querySelector('.deck-builder');
    if (!deckBuilder) return null;

    const allChildren = Array.from(deckBuilder.querySelectorAll('*'));
    const withZIndex = allChildren
      .map(el => {
        const style = window.getComputedStyle(el);
        return {
          tag: (el as HTMLElement).tagName,
          classes: (el as HTMLElement).className,
          zIndex: style.zIndex,
          position: style.position,
          bounds: el.getBoundingClientRect().toJSON()
        };
      })
      .filter(el => el.zIndex !== 'auto' && el.zIndex !== '0');

    return withZIndex;
  });

  console.log('\n=== ELEMENTS WITH Z-INDEX ===');
  console.log(JSON.stringify(zIndexCheck, null, 2));

  // Final screenshot highlighting the problem area
  await page.screenshot({ path: 'screenshots/03-final-state.png', fullPage: true });
});
