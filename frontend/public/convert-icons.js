#!/usr/bin/env node

/**
 * Icon conversion script for Clash Royale Deck Builder
 * 
 * This script converts SVG icons to PNG and ICO formats.
 * 
 * Usage:
 * npm install sharp (for PNG conversion)
 * npm install to-ico (for ICO conversion)
 * node convert-icons.js
 * 
 * Or use online converters:
 * - https://convertio.co/svg-png/
 * - https://convertio.co/svg-ico/
 * - https://favicon.io/favicon-converter/
 */

const fs = require('fs');
const path = require('path');

console.log('🎮 Clash Royale Favicon Conversion Script');
console.log('=========================================');

const svgFiles = [
  'clash-royale-favicon-16.svg',
  'clash-royale-favicon-32.svg', 
  'clash-royale-favicon.svg',
  'clash-royale-logo192.svg',
  'clash-royale-logo512.svg'
];

console.log('📁 SVG files to convert:');
svgFiles.forEach(file => {
  if (fs.existsSync(file)) {
    console.log(`  ✅ ${file}`);
  } else {
    console.log(`  ❌ ${file} (missing)`);
  }
});

console.log('\n🔧 To convert these files to PNG/ICO:');
console.log('1. Install dependencies: npm install sharp to-ico');
console.log('2. Use online converters like favicon.io');
console.log('3. Or use ImageMagick: convert file.svg file.png');

console.log('\n📋 Required conversions:');
console.log('  • clash-royale-favicon-16.svg → favicon-16x16.png');
console.log('  • clash-royale-favicon-32.svg → favicon-32x32.png');
console.log('  • clash-royale-favicon.svg → favicon.ico (16x16, 32x32, 48x48)');
console.log('  • clash-royale-logo192.svg → apple-touch-icon.png (192x192)');
console.log('  • clash-royale-logo512.svg → android-chrome-512x512.png');

// Example conversion code (requires sharp package)
/*
const sharp = require('sharp');

async function convertSvgToPng(svgPath, pngPath, size) {
  try {
    await sharp(svgPath)
      .resize(size, size)
      .png()
      .toFile(pngPath);
    console.log(`✅ Converted ${svgPath} to ${pngPath}`);
  } catch (error) {
    console.error(`❌ Error converting ${svgPath}:`, error.message);
  }
}

// Uncomment to run conversions:
// convertSvgToPng('clash-royale-logo192.svg', 'apple-touch-icon.png', 192);
// convertSvgToPng('clash-royale-logo512.svg', 'android-chrome-512x512.png', 512);
*/