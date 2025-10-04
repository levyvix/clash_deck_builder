# Storage Type Indicators

This document describes the CSS classes and styling for storage type indicators used throughout the Clash Royale Deck Builder application.

## Overview

Storage type indicators help users distinguish between decks stored locally in their browser versus decks stored on the server (when authenticated). The styling provides clear visual differentiation while maintaining consistency with the overall design system.

## CSS Classes

### Base Classes

- `.storage-indicator-base` - Base styles for all storage indicators
- `.storage-indicator--local` - Styles for local storage indicators (green theme)
- `.storage-indicator--server` - Styles for server storage indicators (blue theme)

### Size Variants

- `.storage-indicator--small` - Compact size for tight spaces
- `.storage-indicator--medium` - Standard size for most use cases
- `.storage-indicator--large` - Larger size for emphasis

### Badge Variants

- `.storage-badge` - Special badge styling for deck cards
- `.storage-badge--local` - Local storage badge with gradient background
- `.storage-badge--server` - Server storage badge with gradient background

### Summary Components

- `.storage-summary` - Container for mixed storage summaries
- `.storage-summary__count` - Styling for count numbers in summaries

## Usage Examples

### Basic Indicators
```jsx
<span className="storage-indicator storage-indicator--medium storage-indicator--local">
  Local Storage
</span>

<span className="storage-indicator storage-indicator--medium storage-indicator--server">
  Server Storage
</span>
```

### Deck Card Badges
```jsx
<span className="storage-badge storage-badge--local">
  💾 Local
</span>

<span className="storage-badge storage-badge--server">
  ☁️ Server
</span>
```

### Storage Summary
```jsx
<div className="storage-summary">
  <span className="storage-indicator storage-indicator--medium storage-indicator--local">
    Local <span className="storage-summary__count">5</span>
  </span>
  <span className="storage-indicator storage-indicator--medium storage-indicator--server">
    Server <span className="storage-summary__count">3</span>
  </span>
</div>
```

## Color Scheme

### Local Storage (Green Theme)
- Background: `rgba(76, 175, 80, 0.12)`
- Text: `#1b5e20`
- Border: `rgba(76, 175, 80, 0.4)`
- Gradient (badges): `linear-gradient(135deg, rgba(76, 175, 80, 0.9), rgba(56, 142, 60, 0.9))`

### Server Storage (Blue Theme)
- Background: `rgba(33, 150, 243, 0.12)`
- Text: `#0d47a1`
- Border: `rgba(33, 150, 243, 0.4)`
- Gradient (badges): `linear-gradient(135deg, rgba(33, 150, 243, 0.9), rgba(25, 118, 210, 0.9))`

## Responsive Design

The indicators automatically adapt to different screen sizes:

- **Desktop**: Full size with hover effects
- **Tablet**: Slightly reduced padding and font sizes
- **Mobile**: Compact sizing with adjusted spacing

## Accessibility Features

- High contrast mode support
- Reduced motion support for users with motion sensitivity
- Focus indicators for keyboard navigation
- Print-friendly styles
- Semantic color choices with sufficient contrast ratios

## Browser Support

The styling uses modern CSS features but includes fallbacks:
- CSS Grid and Flexbox for layout
- CSS Custom Properties (variables) with fallback values
- Modern color functions with hex fallbacks
- Backdrop-filter with graceful degradation

## Integration

The storage indicators are automatically imported via `index.css` and available throughout the application. No additional imports are required in individual components.