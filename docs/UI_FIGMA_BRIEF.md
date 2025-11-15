# QuillMusic UI Design Brief for Figma

## Overview

QuillMusic is an AI-powered music creation platform with a professional, modern interface that balances simplicity for beginners with power for advanced users. The design should feel like a premium music production tool while being approachable and inspiring.

**Core Brand Values:**
- Professional yet accessible
- Creative and inspiring
- Cutting-edge but not overwhelming
- Dark-themed for reduced eye strain during long sessions

## Color Palette

### Primary Colors
- **Background Dark**: `#0a0a0f` (Deep charcoal, almost black)
- **Surface Dark**: `#121218` (Slightly lighter for cards/panels)
- **Surface Light**: `#1a1a24` (Elevated surfaces, modals)

### Accent Colors
- **Primary Purple**: `#8b5cf6` (Main CTA buttons, highlights)
- **Purple Hover**: `#7c3aed` (Button hover states)
- **Purple Light**: `#a78bfa` (Secondary accents)

### Functional Colors
- **Success Green**: `#10b981` (Ready states, success messages)
- **Warning Yellow**: `#f59e0b` (Warnings, queued states)
- **Error Red**: `#ef4444` (Errors, failed states)
- **Info Blue**: `#3b82f6` (Information, processing states)

### Text Colors
- **Primary Text**: `#f9fafb` (High contrast white for headers)
- **Secondary Text**: `#d1d5db` (Body text, descriptions)
- **Muted Text**: `#9ca3af` (Labels, metadata)
- **Disabled Text**: `#6b7280` (Disabled states)

### Border Colors
- **Border Primary**: `#27272a` (Default borders)
- **Border Accent**: `#3f3f46` (Hover borders)
- **Border Bright**: `#52525b` (Active/focus borders)

## Typography

### Font Family
- **Primary**: Inter or DM Sans
- **Monospace**: JetBrains Mono or Fira Code (for job IDs, technical data)

### Font Sizes & Hierarchy
- **H1 (Page Title)**: 36px, Bold (2.25rem)
- **H2 (Section Title)**: 24px, Semibold (1.5rem)
- **H3 (Card Title)**: 18px, Semibold (1.125rem)
- **Body Large**: 16px, Regular (1rem)
- **Body**: 14px, Regular (0.875rem)
- **Small**: 12px, Regular (0.75rem)
- **Tiny**: 10px, Medium (0.625rem)

## Layout Structure

### Sidebar Navigation (256px wide)

```
┌────────────────────────┐
│  [Logo] QuillMusic     │ ← Logo + App Name
│  AI Music Studio       │ ← Tagline
├────────────────────────┤
│                        │
│  🏠 Dashboard          │ ← Nav Items
│  ✨ AI Song Builder    │   (with icons)
│  📋 Render Queue       │
│  🎹 Manual Creator     │
│                        │
├────────────────────────┤
│  ⚙️  Settings          │ ← Footer
└────────────────────────┘
```

**Sidebar Specs:**
- Background: Surface Dark (`#121218`)
- Active item: Purple gradient background
- Hover item: Subtle gray background (`#1a1a24`)
- Icons: 20px, left-aligned with 16px padding
- Border right: 1px solid Border Primary

### Main Content Area

```
┌────────────────────────────────────────┐
│  Page Title                            │ ← 32px top padding
│  Description text                      │
├────────────────────────────────────────┤
│                                        │
│  [Content Cards and Components]        │ ← 8-column grid on large screens
│                                        │    4-column on medium
│                                        │    1-column on mobile
│                                        │
└────────────────────────────────────────┘
```

**Content Area Specs:**
- Padding: 32px all sides (2rem)
- Max width: 1400px (centered)
- Grid gap: 24px (1.5rem)

## Component Library

### 1. Cards

**Standard Card:**
- Background: Surface Dark (`#121218`)
- Border: 1px solid Border Primary
- Border radius: 12px (0.75rem)
- Padding: 24px (1.5rem)
- Shadow: Subtle glow on hover

**Gradient Card (CTA):**
- Background: Linear gradient from Purple to Purple Dark with 50% opacity
- Border: 1px solid Purple (50% opacity)
- Animated gradient on hover

### 2. Buttons

**Primary Button (CTA):**
- Background: Primary Purple (`#8b5cf6`)
- Text: White
- Padding: 10px 16px
- Border radius: 8px
- Hover: Slight scale (1.02) + brightness increase

**Secondary Button:**
- Background: Transparent
- Border: 1px solid Border Accent
- Text: Secondary Text color
- Hover: Border becomes Border Bright

**Icon Button:**
- 40x40px square
- Centered icon (20px)
- Hover: Background Surface Light

### 3. Form Inputs

**Text Input / Textarea:**
- Background: Background Dark (`#0a0a0f`)
- Border: 1px solid Border Primary
- Border radius: 6px
- Padding: 10px 12px
- Focus: Border becomes Purple, 2px ring

**Select Dropdown:**
- Same as text input
- Chevron icon on right (12px)
- Dropdown menu: Surface Light background with border

### 4. Badges

**Status Badges:**
- Padding: 4px 12px
- Border radius: 12px (pill shape)
- Font: 12px, Medium

Colors:
- **Ready**: Green background (20% opacity), green text
- **Processing**: Blue background (20% opacity), blue text
- **Queued**: Yellow background (20% opacity), yellow text
- **Failed**: Red background (20% opacity), red text

**Genre/Type Badges:**
- Padding: 4px 8px
- Border radius: 6px
- Border: 1px solid
- Background: Transparent
- Various accent colors based on type

### 5. Progress & Loading

**Loading Spinner:**
- Purple color (`#8b5cf6`)
- 20px diameter (small), 32px (medium), 48px (large)
- Smooth rotation animation

**Progress Bar:**
- Height: 8px
- Background: Surface Dark
- Fill: Purple gradient
- Border radius: 4px

## Page-Specific Designs

### Dashboard Page

**Hero Section:**
- Two large CTA cards in a 2-column grid
- Left card: "Start AI Song Builder" (Purple gradient)
- Right card: "Manual Creator - Coming Soon" (Blue gradient, dimmed)

**Stats Row:**
- Three cards showing:
  - Total Projects
  - Renders Complete
  - Time Saved
- Icon + number + description layout
- Minimal design, focus on numbers

**Recent Activity:**
- Card with scrollable list of recent songs
- Each item shows: thumbnail, title, date, status badge
- Empty state: Centered icon + text

### AI Song Builder Page

**Two-Column Layout:**

**Left Column - Song Setup:**
- Form card with:
  - Large textarea for prompt
  - Dropdowns for Genre and Mood
  - Number inputs for BPM
  - Text input for Key
  - Duration selector
  - Optional reference textarea
  - Large "Generate Blueprint" button (Purple)

**Right Column - Blueprint Display:**
- Conditionally shown after generation
- Song title card with metadata (Genre, Mood, BPM, Key)
- Sections list with:
  - Badge for section type
  - Section name and description
  - Bar count and instruments
- Vocal style card with badges
- Production notes (expandable)
- "Send to Render Engine" button (Green)
- Separate lyrics card below with formatted sections

**Empty State:**
- Large music note icon (64px, gray, 30% opacity)
- Text: "Generate a blueprint to see results"

### Render Queue Page

**Job Input Card:**
- Single-line input + button
- Placeholder: "job_abc123..."
- Button: "Check Status"

**Jobs List:**
- Cards showing:
  - Job ID (monospace font)
  - Status badge
  - Song ID
  - Render type badge
  - Audio URL (if ready)
  - Play button (if ready)
  - Error message (if failed)

**Empty State:**
- Clock icon (64px)
- Text: "No jobs yet..."

### Manual Creator (Coming Soon)

**Hero Card:**
- Gradient background (Blue)
- Large title: "Coming Soon: DAW Lite"
- Description paragraph
- Tag: "In Development"

**Feature Cards Grid:**
- 2x2 grid of cards, each with:
  - Icon (colored background circle)
  - Feature title
  - Short description

**Mockup Preview:**
- Large card containing wireframe of DAW interface:
  - Top toolbar (transport, tempo, etc.)
  - Left track list (colored track indicators)
  - Right timeline grid (with mock audio clips)
  - Bottom mixer section

## Animations & Interactions

### Micro-interactions
- **Button Hover**: Scale 1.02, brightness +10%
- **Card Hover**: Subtle border glow, slight scale 1.01
- **Loading**: Fade in/out, spinner rotation
- **Toast Notifications**: Slide in from top-right

### Transitions
- Default: 150ms ease-in-out
- Page transitions: 250ms ease-in-out
- Modals: 200ms with slight scale

### Hover States
- All interactive elements should have visible hover states
- Use combination of: color change, scale, border glow
- Cursor changes to pointer on interactive elements

## Responsive Breakpoints

- **Mobile**: < 640px (1 column)
- **Tablet**: 640px - 1024px (2-3 columns, collapsible sidebar)
- **Desktop**: > 1024px (Full layout)

**Mobile Adjustments:**
- Sidebar becomes bottom nav or hamburger menu
- Cards stack vertically
- Reduce padding (16px instead of 32px)
- Smaller font sizes
- Collapsible sections in forms

## Accessibility

- **Contrast Ratios**: All text meets WCAG AA standards
- **Focus States**: 2px purple ring on all interactive elements
- **Keyboard Navigation**: Tab through all controls
- **ARIA Labels**: All icons have descriptive labels
- **Screen Reader**: Semantic HTML with proper headings

## Figma AI Prompt

*Use this prompt to generate the design in Figma AI:*

"Create a dark-themed music production web app UI called 'QuillMusic'. Use a deep charcoal background (#0a0a0f) with slightly lighter cards (#121218). Accent color is purple (#8b5cf6).

The layout has a left sidebar (256px wide) with logo at top, navigation items (Dashboard, AI Song Builder, Render Queue, Manual Creator), and Settings at bottom. Active items have purple background.

Main content area has:
1. Dashboard with two large CTA cards, stats row (3 cards), and recent activity list
2. AI Song Builder with two columns: left has form inputs for prompt, genre, mood, BPM; right shows generated song blueprint with sections, lyrics, and render button
3. Render Queue with job status cards and play buttons

Use Inter font, 12px border radius on cards, subtle shadows, and smooth hover animations. Include empty states with centered icons and text. Modern, professional, minimalist design for a creative tool."

## Design Principles

1. **Clarity Over Complexity**: Every element should have a clear purpose
2. **Consistency**: Reuse components, maintain spacing rhythm
3. **Feedback**: Always show loading, success, and error states
4. **Hierarchy**: Use size, color, and spacing to create clear visual hierarchy
5. **Delight**: Subtle animations and interactions that feel smooth and responsive

## File Organization in Figma

```
QuillMusic Design System
├── 🎨 Colors
│   ├── Background
│   ├── Surface
│   ├── Accents
│   └── Functional
├── 📝 Typography
│   ├── Headings
│   ├── Body
│   └── Labels
├── 🧩 Components
│   ├── Buttons
│   ├── Cards
│   ├── Forms
│   ├── Badges
│   └── Navigation
└── 📄 Pages
    ├── Dashboard
    ├── AI Song Builder
    ├── Render Queue
    └── Manual Creator
```

## Next Steps

1. Create design system with all colors, typography, and base components
2. Design each page in desktop view
3. Create responsive variants for tablet and mobile
4. Add interaction prototypes for key flows
5. Export assets and CSS variables for development
6. Handoff to development with Figma Dev Mode

---

**Note**: This design system can evolve as QuillMusic grows. Start with these foundations and iterate based on user feedback and feature additions.
