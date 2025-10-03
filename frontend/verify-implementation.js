/**
 * Implementation Verification Script
 * Checks that all required files and components exist for Task 15
 */

const fs = require('fs');
const path = require('path');

const REQUIRED_FILES = [
  // Components
  'src/components/DeckBuilder.tsx',
  'src/components/CardDisplay.tsx',
  'src/components/CardGallery.tsx',
  'src/components/CardFilters.tsx',
  'src/components/DeckSlot.tsx',
  'src/components/SavedDecks.tsx',
  'src/components/Notification.tsx',
  'src/components/ErrorBoundary.tsx',
  
  // Services
  'src/services/api.ts',
  'src/services/deckCalculations.ts',
  
  // Types
  'src/types/index.ts',
  
  // Styles
  'src/styles/variables.css',
  'src/App.css',
  'src/styles/CardDisplay.css',
  'src/styles/CardGallery.css',
  'src/styles/CardFilters.css',
  'src/styles/DeckSlot.css',
  'src/styles/DeckBuilder.css',
  'src/styles/SavedDecks.css',
  'src/styles/Notification.css',
  
  // Main files
  'src/App.tsx',
  'src/index.tsx',
  
  // Config
  'package.json',
  'tsconfig.json',
  '.env',
  
  // Documentation
  'INTEGRATION_TEST_REPORT.md',
  'MANUAL_TEST_CHECKLIST.md',
  'TESTING_GUIDE.md',
  'ERROR_HANDLING.md'
];

const REQUIRED_FUNCTIONS = {
  'src/services/deckCalculations.ts': [
    'calculateAverageElixir',
    'canAddEvolution',
    'isDeckComplete',
    'getEmptySlotIndex'
  ],
  'src/services/api.ts': [
    'fetchCards',
    'fetchDecks',
    'createDeck',
    'updateDeck',
    'deleteDeck',
    'ApiError'
  ]
};

const REQUIRED_TYPES = {
  'src/types/index.ts': [
    'Card',
    'DeckSlot',
    'Deck',
    'FilterState',
    'Notification',
    'NotificationType'
  ]
};

console.log('🔍 Verifying Implementation for Task 15...\n');

let allPassed = true;
let filesChecked = 0;
let filesPassed = 0;
let filesFailed = 0;

// Check required files
console.log('📁 Checking Required Files:');
console.log('─'.repeat(50));

REQUIRED_FILES.forEach(file => {
  filesChecked++;
  const filePath = path.join(__dirname, file);
  const exists = fs.existsSync(filePath);
  
  if (exists) {
    console.log(`✅ ${file}`);
    filesPassed++;
  } else {
    console.log(`❌ ${file} - MISSING`);
    filesFailed++;
    allPassed = false;
  }
});

console.log('\n');

// Check required functions
console.log('🔧 Checking Required Functions:');
console.log('─'.repeat(50));

Object.entries(REQUIRED_FUNCTIONS).forEach(([file, functions]) => {
  const filePath = path.join(__dirname, file);
  
  if (fs.existsSync(filePath)) {
    const content = fs.readFileSync(filePath, 'utf8');
    
    functions.forEach(func => {
      // Check for function declaration or export
      const hasFunction = content.includes(`function ${func}`) || 
                         content.includes(`const ${func}`) ||
                         content.includes(`export const ${func}`) ||
                         content.includes(`export function ${func}`) ||
                         content.includes(`class ${func}`);
      
      if (hasFunction) {
        console.log(`✅ ${file}: ${func}()`);
      } else {
        console.log(`❌ ${file}: ${func}() - NOT FOUND`);
        allPassed = false;
      }
    });
  } else {
    console.log(`⚠️  ${file} - File not found, skipping function checks`);
  }
});

console.log('\n');

// Check required types
console.log('📝 Checking Required Types:');
console.log('─'.repeat(50));

Object.entries(REQUIRED_TYPES).forEach(([file, types]) => {
  const filePath = path.join(__dirname, file);
  
  if (fs.existsSync(filePath)) {
    const content = fs.readFileSync(filePath, 'utf8');
    
    types.forEach(type => {
      const hasType = content.includes(`interface ${type}`) || 
                     content.includes(`type ${type}`) ||
                     content.includes(`export interface ${type}`) ||
                     content.includes(`export type ${type}`);
      
      if (hasType) {
        console.log(`✅ ${file}: ${type}`);
      } else {
        console.log(`❌ ${file}: ${type} - NOT FOUND`);
        allPassed = false;
      }
    });
  } else {
    console.log(`⚠️  ${file} - File not found, skipping type checks`);
  }
});

console.log('\n');

// Check package.json dependencies
console.log('📦 Checking Dependencies:');
console.log('─'.repeat(50));

const packageJsonPath = path.join(__dirname, 'package.json');
if (fs.existsSync(packageJsonPath)) {
  const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
  const requiredDeps = [
    'react',
    'react-dom',
    'react-router-dom',
    'typescript',
    '@testing-library/react',
    '@testing-library/jest-dom'
  ];
  
  requiredDeps.forEach(dep => {
    const hasDepency = packageJson.dependencies?.[dep] || packageJson.devDependencies?.[dep];
    
    if (hasDepency) {
      console.log(`✅ ${dep}: ${hasDepency}`);
    } else {
      console.log(`❌ ${dep} - NOT INSTALLED`);
      allPassed = false;
    }
  });
} else {
  console.log('❌ package.json not found');
  allPassed = false;
}

console.log('\n');

// Summary
console.log('═'.repeat(50));
console.log('📊 VERIFICATION SUMMARY');
console.log('═'.repeat(50));
console.log(`Files Checked: ${filesChecked}`);
console.log(`Files Passed: ${filesPassed}`);
console.log(`Files Failed: ${filesFailed}`);
console.log(`Pass Rate: ${Math.round((filesPassed / filesChecked) * 100)}%`);
console.log('');

if (allPassed) {
  console.log('✅ ALL CHECKS PASSED!');
  console.log('');
  console.log('🎉 Implementation is complete and ready for testing!');
  console.log('');
  console.log('Next steps:');
  console.log('1. Start the backend: cd backend && uv run uvicorn src.main:app --reload');
  console.log('2. Start the frontend: npm start');
  console.log('3. Follow TESTING_GUIDE.md for comprehensive testing');
  console.log('4. Use MANUAL_TEST_CHECKLIST.md to track progress');
  process.exit(0);
} else {
  console.log('❌ SOME CHECKS FAILED');
  console.log('');
  console.log('Please review the failures above and ensure all required');
  console.log('files, functions, and types are properly implemented.');
  process.exit(1);
}
