import { test } from '@playwright/test';

test('comprehensive sticky deck debugging', async ({ page, context }) => {
  // Clear cache
  await context.clearCookies();

  // Navigate with no-cache headers
  await page.goto('http://localhost:3000', {
    waitUntil: 'networkidle'
  });

  // Wait for page to fully load
  await page.waitForSelector('.deck-builder', { timeout: 10000 });
  await page.waitForTimeout(2000);

  console.log('=== PAGE LOADED ===\n');

  // Check what CSS is actually loaded
  const cssCheck = await page.evaluate(() => {
    const styleSheets = Array.from(document.styleSheets);
    const deckBuilderRules: any[] = [];

    styleSheets.forEach(sheet => {
      try {
        const rules = Array.from(sheet.cssRules || []);
        rules.forEach((rule: any) => {
          if (rule.selectorText?.includes('deck-builder__deck-section--sticky')) {
            deckBuilderRules.push({
              selector: rule.selectorText,
              cssText: rule.cssText,
              top: rule.style.top,
              position: rule.style.position,
              zIndex: rule.style.zIndex
            });
          }
        });
      } catch (e) {
        // Skip cross-origin stylesheets
      }
    });

    return deckBuilderRules;
  });

  console.log('=== LOADED CSS RULES FOR STICKY DECK ===');
  console.log(JSON.stringify(cssCheck, null, 2));

  // Check computed styles
  const computedStyles = await page.evaluate(() => {
    const element = document.querySelector('.deck-builder__deck-section--sticky');
    if (!element) return null;

    const computed = window.getComputedStyle(element);
    return {
      position: computed.position,
      top: computed.top,
      zIndex: computed.zIndex,
      maxHeight: computed.maxHeight
    };
  });

  console.log('\n=== COMPUTED STYLES ===');
  console.log(JSON.stringify(computedStyles, null, 2));

  // Take screenshot before scroll
  await page.screenshot({ path: 'screenshots/debug-before-scroll.png', fullPage: true });

  // Get initial positions
  const beforeScroll = await page.evaluate(() => {
    const nav = document.querySelector('.app__nav');
    const deckSection = document.querySelector('.deck-builder__deck-section--sticky');
    const deckHeader = document.querySelector('.deck-builder__deck-header');
    const title = document.querySelector('.deck-builder__title');
    const stats = document.querySelector('.deck-builder__stats');

    return {
      scrollY: window.scrollY,
      nav: nav ? {
        bounds: nav.getBoundingClientRect().toJSON(),
        text: nav.textContent?.substring(0, 50)
      } : null,
      deckSection: deckSection ? {
        bounds: deckSection.getBoundingClientRect().toJSON(),
        classList: Array.from(deckSection.classList)
      } : null,
      deckHeader: deckHeader ? {
        bounds: deckHeader.getBoundingClientRect().toJSON(),
        visible: deckHeader.getBoundingClientRect().height > 0
      } : null,
      title: title ? {
        bounds: title.getBoundingClientRect().toJSON(),
        text: title.textContent
      } : null,
      stats: stats ? {
        bounds: stats.getBoundingClientRect().toJSON(),
        text: stats.textContent
      } : null
    };
  });

  console.log('\n=== BEFORE SCROLL ===');
  console.log(JSON.stringify(beforeScroll, null, 2));

  // Scroll down
  await page.evaluate(() => window.scrollTo(0, 400));
  await page.waitForTimeout(1000);

  // Take screenshot after scroll
  await page.screenshot({ path: 'screenshots/debug-after-scroll.png', fullPage: false });

  const afterScroll = await page.evaluate(() => {
    const nav = document.querySelector('.app__nav');
    const deckSection = document.querySelector('.deck-builder__deck-section--sticky');
    const deckHeader = document.querySelector('.deck-builder__deck-header');
    const title = document.querySelector('.deck-builder__title');
    const stats = document.querySelector('.deck-builder__stats');

    const navBounds = nav ? nav.getBoundingClientRect() : null;
    const headerBounds = deckHeader ? deckHeader.getBoundingClientRect() : null;

    return {
      scrollY: window.scrollY,
      nav: navBounds ? navBounds.toJSON() : null,
      deckSection: deckSection ? deckSection.getBoundingClientRect().toJSON() : null,
      deckHeader: headerBounds ? headerBounds.toJSON() : null,
      title: title ? {
        bounds: title.getBoundingClientRect().toJSON(),
        text: title.textContent,
        visible: title.getBoundingClientRect().top >= 0
      } : null,
      stats: stats ? {
        bounds: stats.getBoundingClientRect().toJSON(),
        text: stats.textContent,
        visible: stats.getBoundingClientRect().top >= (navBounds?.bottom || 0)
      } : null,
      analysis: {
        navBottom: navBounds?.bottom || 0,
        headerTop: headerBounds?.top || 0,
        isHeaderBelowNav: headerBounds ? headerBounds.top >= (navBounds?.bottom || 0) : false,
        overlap: navBounds && headerBounds ? (navBounds.bottom - headerBounds.top) : 0
      }
    };
  });

  console.log('\n=== AFTER SCROLL (400px) ===');
  console.log(JSON.stringify(afterScroll, null, 2));

  console.log('\n=== ANALYSIS ===');
  if (afterScroll.analysis.overlap > 0) {
    console.log(`⚠️  OVERLAP DETECTED: Nav overlaps header by ${afterScroll.analysis.overlap}px`);
  } else {
    console.log(`✅ NO OVERLAP: Header is ${Math.abs(afterScroll.analysis.overlap)}px below nav`);
  }

  if (afterScroll.title && !afterScroll.title.visible) {
    console.log(`⚠️  TITLE NOT VISIBLE: Top at ${afterScroll.title.bounds.top}px`);
  }

  if (afterScroll.stats && !afterScroll.stats.visible) {
    console.log(`⚠️  STATS NOT VISIBLE: Top at ${afterScroll.stats.bounds.top}px (nav bottom at ${afterScroll.analysis.navBottom}px)`);
  }
});
