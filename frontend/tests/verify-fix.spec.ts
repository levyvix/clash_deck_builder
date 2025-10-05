import { test, expect } from '@playwright/test';

test('verify sticky deck header fix', async ({ page }) => {
  // Force a hard reload by adding cache busting
  await page.goto(`http://localhost:3000?t=${Date.now()}`);
  await page.waitForSelector('.deck-builder__deck-section--sticky', { timeout: 10000 });

  // Get initial positions
  const initial = await page.evaluate(() => {
    const nav = document.querySelector('.app__nav');
    const deck = document.querySelector('.deck-builder__deck-section--sticky');
    const header = document.querySelector('.deck-builder__deck-header');
    const styles = deck ? window.getComputedStyle(deck) : null;

    return {
      nav: nav ? nav.getBoundingClientRect().toJSON() : null,
      deck: deck ? deck.getBoundingClientRect().toJSON() : null,
      header: header ? header.getBoundingClientRect().toJSON() : null,
      deckComputedTop: styles?.top,
      scrollY: window.scrollY
    };
  });

  console.log('=== INITIAL STATE ===');
  console.log(JSON.stringify(initial, null, 2));

  // Scroll down significantly
  await page.evaluate(() => window.scrollTo(0, 500));
  await page.waitForTimeout(500);

  const afterScroll = await page.evaluate(() => {
    const nav = document.querySelector('.app__nav');
    const deck = document.querySelector('.deck-builder__deck-section--sticky');
    const header = document.querySelector('.deck-builder__deck-header');

    return {
      scrollY: window.scrollY,
      nav: nav ? nav.getBoundingClientRect().toJSON() : null,
      deck: deck ? deck.getBoundingClientRect().toJSON() : null,
      header: header ? header.getBoundingClientRect().toJSON() : null,
      navBottom: nav ? nav.getBoundingClientRect().bottom : 0,
      headerTop: header ? header.getBoundingClientRect().top : 0,
      isHeaderVisible: header ? header.getBoundingClientRect().top >= 120 : false
    };
  });

  console.log('\n=== AFTER SCROLL (500px) ===');
  console.log(JSON.stringify(afterScroll, null, 2));

  if (afterScroll.navBottom && afterScroll.headerTop) {
    const gap = afterScroll.headerTop - afterScroll.navBottom;
    console.log(`\nGap between nav bottom and header top: ${gap}px`);
    console.log(`Header should be visible: ${afterScroll.isHeaderVisible}`);
  }

  await page.screenshot({ path: 'screenshots/verify-fix.png', fullPage: false });
});
