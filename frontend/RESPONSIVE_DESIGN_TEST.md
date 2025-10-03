# Responsive Design Testing Checklist

## Test Breakpoints
- **Desktop**: > 1200px
- **Tablet**: 768px - 1200px  
- **Mobile**: < 768px
- **Small Mobile**: < 480px

## 1. Card Gallery Grid Layout

### Desktop (> 1200px)
- [ ] Grid displays 6 columns
- [ ] Cards have proper spacing (16px gap)
- [ ] Cards maintain aspect ratio
- [ ] Hover effects work smoothly
- [ ] Images load with proper fallback

### Tablet (768px - 1200px)
- [ ] Grid adjusts to 4 columns
- [ ] Cards remain readable
- [ ] Touch interactions work (if touch device)
- [ ] Spacing adjusts appropriately

### Mobile (< 768px)
- [ ] Grid adjusts to 2 columns
- [ ] Cards are touch-friendly (min 44px touch targets)
- [ ] Text remains readable
- [ ] Images scale properly
- [ ] Gap reduces to 8px

### Small Mobile (< 480px)
- [ ] Grid maintains 2 columns
- [ ] Cards fit screen width
- [ ] All content visible without horizontal scroll
- [ ] Touch targets remain accessible

## 2. Deck Builder Layout

### Desktop (> 1200px)
- [ ] Deck section and gallery side-by-side
- [ ] Deck slots in 2 rows of 4
- [ ] Stats display horizontally
- [ ] Save button centered

### Tablet (768px - 1200px)
- [ ] Layout stacks vertically (deck on top, gallery below)
- [ ] Deck slots remain 2 rows of 4
- [ ] Stats wrap if needed
- [ ] All controls accessible

### Mobile (< 768px)
- [ ] Full vertical stack
- [ ] Deck slots adjust size (aspect ratio maintained)
- [ ] Stats display vertically
- [ ] Save button full width
- [ ] Dialog responsive

### Small Mobile (< 480px)
- [ ] Deck slots in 2 columns, 4 rows
- [ ] Stats stack vertically
- [ ] Dialog fits screen (with margins)
- [ ] All buttons full width

## 3. Card Filters

### Desktop (> 1200px)
- [ ] Filters in multi-column grid
- [ ] All filters visible without scrolling
- [ ] Clear button positioned correctly

### Tablet (768px - 1200px)
- [ ] Filters adjust to 2 columns
- [ ] Dropdowns remain usable

### Mobile (< 768px)
- [ ] Filters stack in single column
- [ ] Clear button full width
- [ ] Touch-friendly inputs (min 44px height)
- [ ] Dropdowns easy to tap

### Small Mobile (< 480px)
- [ ] Single column maintained
- [ ] Reduced padding
- [ ] Font sizes remain readable

## 4. Deck Slots

### All Breakpoints
- [ ] Empty slots show dashed border and "+" icon
- [ ] Filled slots show card image
- [ ] Evolution badge visible and positioned correctly
- [ ] Elixir cost badge readable
- [ ] Options menu accessible on click/tap
- [ ] Remove and evolution toggle buttons work

### Touch Devices
- [ ] Tap to open options menu
- [ ] Buttons min 44px height
- [ ] No hover effects (or adjusted for touch)
- [ ] Active states work on tap

## 5. Notifications

### Desktop
- [ ] Positioned top-right
- [ ] Stack vertically
- [ ] Auto-dismiss after 3 seconds
- [ ] Manual dismiss works

### Mobile (< 768px)
- [ ] Span full width (with margins)
- [ ] Positioned at top
- [ ] Dismiss button touch-friendly
- [ ] Text remains readable

### Small Mobile (< 480px)
- [ ] Reduced padding
- [ ] Smaller dismiss button
- [ ] Text size adjusted

## 6. Rarity Colors

Test each rarity displays correct colors:

### Common
- [ ] Border: Gray (#808080)
- [ ] Badge: Gray background, white text

### Rare
- [ ] Border: Orange (#ff8c00)
- [ ] Badge: Orange background, white text

### Epic
- [ ] Border: Purple (#9370db)
- [ ] Badge: Purple background, white text

### Legendary
- [ ] Border: Gold (#ffd700)
- [ ] Badge: Gold gradient (gold to orange), white text
- [ ] Card background: Light gold tint

### Champion
- [ ] Border: Gold (#ffd700)
- [ ] Badge: Gold background, dark text
- [ ] Card background: Light gold tint

## 7. Loading States

### Card Gallery Loading
- [ ] 12 skeleton cards display
- [ ] Shimmer animation works
- [ ] Skeleton matches card dimensions
- [ ] Responsive at all breakpoints

### Deck Builder Loading
- [ ] Spinner centered
- [ ] Loading message visible
- [ ] Spinner animates smoothly

## 8. Error States

### API Errors
- [ ] Error message centered
- [ ] Retry button accessible
- [ ] Error text readable
- [ ] Button touch-friendly on mobile

### Image Load Errors
- [ ] Placeholder shows card name
- [ ] Fallback styling applied
- [ ] No broken image icons

## 9. Touch Device Interactions

### General
- [ ] No hover effects on touch devices
- [ ] Active states work on tap
- [ ] All buttons min 44px touch target
- [ ] Scrolling smooth
- [ ] No accidental double-taps

### Specific Components
- [ ] Card tap opens options
- [ ] Deck slot tap opens menu
- [ ] Filter inputs easy to focus
- [ ] Buttons respond to touch
- [ ] Dialogs dismissible

## 10. Performance

### All Breakpoints
- [ ] Smooth animations (60fps)
- [ ] No layout shifts
- [ ] Images load progressively
- [ ] Transitions smooth
- [ ] No janky scrolling

## 11. Accessibility

### Keyboard Navigation
- [ ] Tab through all interactive elements
- [ ] Focus indicators visible
- [ ] Enter/Space activate buttons
- [ ] Escape closes dialogs

### Screen Readers
- [ ] Images have alt text
- [ ] Buttons have labels
- [ ] Form inputs labeled
- [ ] Status messages announced

## 12. Cross-Browser Testing

Test on:
- [ ] Chrome (desktop & mobile)
- [ ] Firefox (desktop & mobile)
- [ ] Safari (desktop & mobile)
- [ ] Edge (desktop)

## Testing Tools

### Browser DevTools
1. Open DevTools (F12)
2. Toggle device toolbar (Ctrl+Shift+M)
3. Test each breakpoint:
   - 1920x1080 (Desktop)
   - 1024x768 (Tablet)
   - 768x1024 (Tablet portrait)
   - 375x667 (iPhone)
   - 360x640 (Android)

### Responsive Design Mode
1. Use browser's responsive design mode
2. Drag to resize viewport
3. Verify smooth transitions between breakpoints
4. Check for layout breaks

### Touch Simulation
1. Enable touch simulation in DevTools
2. Test all tap interactions
3. Verify touch target sizes
4. Check for touch-specific styles

## Common Issues to Check

- [ ] No horizontal scrolling at any breakpoint
- [ ] Text doesn't overflow containers
- [ ] Images don't distort
- [ ] Buttons don't overlap
- [ ] Modals/dialogs fit screen
- [ ] Navigation accessible
- [ ] Content hierarchy maintained
- [ ] Spacing consistent
- [ ] Colors meet contrast requirements
- [ ] Animations don't cause motion sickness

## Sign-off

- [ ] All desktop tests passed
- [ ] All tablet tests passed
- [ ] All mobile tests passed
- [ ] All touch device tests passed
- [ ] All rarity colors verified
- [ ] All loading states verified
- [ ] All error states verified
- [ ] Cross-browser testing complete
- [ ] Accessibility checks passed
- [ ] Performance acceptable

**Tested by:** _________________
**Date:** _________________
**Notes:** _________________
