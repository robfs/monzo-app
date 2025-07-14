# Textual CSS Reference Guide

## Valid Textual CSS Properties

This reference guide lists the CSS properties that are valid in Textual applications.

### Layout Properties

#### Display & Positioning
- `display: block | none`
- `visibility: visible | hidden`
- `overflow: hidden | scroll | auto`
- `overflow-x: hidden | scroll | auto`
- `overflow-y: hidden | scroll | auto`

#### Grid Layout
- `layout: grid | horizontal | vertical`
- `grid-size: <columns> <rows>`
- `grid-columns: <size> [<size> ...]`
- `grid-rows: <size> [<size> ...]`
- `grid-gutter: <horizontal> [<vertical>]`
- `column-span: <number>`
- `row-span: <number>`

#### Dock Layout
- `dock: top | right | bottom | left`

#### Alignment
- `align: left | center | right | justify`
- `align-horizontal: left | center | right`
- `align-vertical: top | middle | bottom`
- `content-align: left | center | right`
- `content-align-horizontal: left | center | right`
- `content-align-vertical: top | middle | bottom`

### Dimensions

#### Size
- `width: <integer> | <percentage> | auto`
- `height: <integer> | <percentage> | auto`
- `min-width: <integer>`
- `max-width: <integer>`
- `min-height: <integer>`
- `max-height: <integer>`

#### Spacing
- `margin: <top> [<right>] [<bottom>] [<left>]`
- `margin-top: <integer>`
- `margin-right: <integer>`
- `margin-bottom: <integer>`
- `margin-left: <integer>`
- `padding: <top> [<right>] [<bottom>] [<left>]`
- `padding-top: <integer>`
- `padding-right: <integer>`
- `padding-bottom: <integer>`
- `padding-left: <integer>`

### Typography

#### Text Styling
- `text-align: left | center | right | justify | start | end`
- `text-style: bold | italic | underline | strike | reverse | blink | dim`
- `text-opacity: <0.0-1.0>`

#### Text Decoration
- `text-decoration: none | underline | line-through`

### Colors

#### Text Colors
- `color: <color>`

#### Background Colors
- `background: <color>`

#### Standard Color Variables
- `$primary` - Primary theme color
- `$secondary` - Secondary theme color
- `$accent` - Accent color
- `$error` - Error state color
- `$warning` - Warning state color
- `$success` - Success state color
- `$info` - Information color
- `$surface` - Surface background
- `$panel` - Panel background
- `$background` - Main background
- `$text` - Primary text color
- `$text-disabled` - Disabled text color

### Borders

#### Border Styles
- `border: <style> [<color>]`
- `border-top: <style> [<color>]`
- `border-right: <style> [<color>]`
- `border-bottom: <style> [<color>]`
- `border-left: <style> [<color>]`

#### Border Style Values
- `none` - No border
- `solid` - Solid line
- `dashed` - Dashed line
- `double` - Double line
- `thick` - Thick border
- `round` - Rounded corners
- `wide` - Wide border

#### Border Titles
- `border-title: "<text>"`
- `border-title-color: <color>`
- `border-title-background: <color>`
- `border-title-style: <style>`
- `border-subtitle: "<text>"`
- `border-subtitle-color: <color>`
- `border-subtitle-background: <color>`
- `border-subtitle-style: <style>`

### Opacity & Effects
- `opacity: <0.0-1.0>`

### Scrollbars
- `scrollbar-background: <color>`
- `scrollbar-color: <color>`
- `scrollbar-corner-color: <color>`
- `scrollbar-size: <integer> <integer>`
- `scrollbar-size-horizontal: <integer>`
- `scrollbar-size-vertical: <integer>`

## Selectors

### Basic Selectors
- `Widget` - Target widget type
- `.class-name` - Target by CSS class
- `#widget-id` - Target by widget ID
- `*` - Universal selector

### Pseudo-selectors
- `:hover` - Mouse hover state
- `:focus` - Focused state
- `:focus-within` - Contains focused element
- `:disabled` - Disabled state
- `:enabled` - Enabled state

### Combinators
- `A B` - Descendant selector
- `A > B` - Direct child selector

## Color Formats

### Supported Color Formats
- Named colors: `red`, `blue`, `green`, etc.
- Hex colors: `#FF0000`, `#F00`
- RGB: `rgb(255, 0, 0)`
- HSL: `hsl(0, 100%, 50%)`
- Color variables: `$primary`, `$accent`, etc.

## Invalid Properties (Do NOT Use)

### Typography (Not Supported)
- ❌ `font-family`
- ❌ `font-size`
- ❌ `text-size`
- ❌ `font-weight`
- ❌ `line-height`

### Advanced Layout (Not Supported)
- ❌ `position: absolute | relative | fixed`
- ❌ `top`, `right`, `bottom`, `left`
- ❌ `z-index`
- ❌ `float`
- ❌ `flex` properties

### Box Model (Limited Support)
- ❌ `box-sizing`
- ❌ `outline`

### Effects (Not Supported)
- ❌ `box-shadow`
- ❌ `text-shadow`
- ❌ `transform`
- ❌ `transition`
- ❌ `animation`

### Media Queries (Not Supported)
- ❌ `@media` queries

## Best Practices

### 1. Use Theme Variables
```css
/* Good */
color: $primary;
background: $surface;

/* Avoid */
color: #0066cc;
background: #1e1e1e;
```

### 2. Prefer Layout Over Positioning
```css
/* Good */
layout: grid;
grid-size: 3 2;

/* Not supported */
position: absolute;
top: 10px;
```

### 3. Use Semantic Class Names
```css
/* Good */
.balance-card { }
.settings-modal { }

/* Avoid */
.red-text { }
.big-box { }
```

### 4. Organize by Component
```css
/* Component styles */
.dashboard-grid {
    layout: grid;
    grid-size: 12 8;
}

.balance-card {
    border: round $primary;
    padding: 1;
}
```

### 5. Use Consistent Spacing
```css
/* Use consistent spacing units */
margin: 1;
padding: 1 2;
grid-gutter: 1;
```

## Common Patterns

### Modal Styling
```css
ModalScreen {
    align: center middle;
}

.modal-container {
    width: 80;
    height: 25;
    border: thick $primary;
    background: $surface;
    padding: 1;
}
```

### Grid Layout
```css
.dashboard-grid {
    layout: grid;
    grid-size: 12 6;
    grid-gutter: 1;
}

.widget-card {
    column-span: 3;
    row-span: 2;
    border: round $primary;
    padding: 1;
}
```

### Focus States
```css
Input:focus {
    border: thick $accent;
}

Button:focus {
    text-style: bold reverse;
}
```

### State-based Styling
```css
.loading {
    opacity: 0.7;
}

.hidden {
    display: none;
}

.error {
    color: $error;
    text-style: bold;
}
```

## Debugging CSS

### Common Issues
1. **Invalid properties** - Check this reference guide
2. **Typos in selectors** - Ensure widget names and classes match
3. **Missing colors** - Use standard color variables
4. **Layout conflicts** - Check grid sizing and spans

### Debugging Tips
1. Use simple selectors first
2. Test with basic properties (color, background)
3. Check the console for CSS parsing errors
4. Validate grid math (columns × rows)

## Resources

- [Textual Documentation](https://textual.textualize.io/)
- [Textual CSS Guide](https://textual.textualize.io/guide/CSS/)
- [Color Reference](https://textual.textualize.io/guide/design/#design-tokens)