# Design Tokens

> **Document Owner:** Frontend Architecture
> **Status:** Living Document
> **Last Updated:** 2026-07-27

---

## Overview

Design tokens are the atomic values of the visual design system. They are defined as CSS custom properties and consumed throughout the application via TailwindCSS. All components reference tokens only — never hardcoded colour hexes, font sizes, or spacing values.

---

## Colour

### Primary Palette

Used for interactive elements, active states, and key UI accents.

| Token | Dark Mode | Light Mode | Usage |
|---|---|---|---|
| `--color-primary-50` | `#eef2ff` | `#eef2ff` | Background hover |
| `--color-primary-100` | `#e0e7ff` | `#e0e7ff` | Light background |
| `--color-primary-200` | `#c7d2fe` | `#c7d2fe` | Border hover |
| `--color-primary-400` | `#818cf8` | `#6366f1` | Selected state |
| `--color-primary-500` | `#6366f1` | `#4f46e5` | Default interactive |
| `--color-primary-600` | `#4f46e5` | `#4338ca` | Hover state |
| `--color-primary-700` | `#4338ca` | `#3730a3` | Active state |
| `--color-primary-900` | `#1e1b4b` | `#1e1b4b` | Text on light bg |

Primary is indigo-based. The dark mode palette is shifted slightly lighter to maintain contrast against dark backgrounds.

### Neutral Palette

Used for backgrounds, borders, text, and structural elements.

| Token | Dark Mode | Light Mode | Usage |
|---|---|---|---|
| `--color-neutral-50` | `#0a0a0a` | `#fafafa` | Page background |
| `--color-neutral-100` | `#141414` | `#f5f5f5` | Card/surface background |
| `--color-neutral-200` | `#1f1f1f` | `#e5e5e5` | Elevated surface |
| `--color-neutral-300` | `#2a2a2a` | `#d4d4d4` | Hovered surface |
| `--color-neutral-400` | `#3f3f3f` | `#a3a3a3` | Disabled text |
| `--color-neutral-500` | `#525252` | `#737373` | Placeholder text |
| `--color-neutral-600` | `#737373` | `#525252` | Muted text |
| `--color-neutral-700` | `#a3a3a3` | `#3f3f3f` | Secondary text |
| `--color-neutral-800` | `#d4d4d4` | `#2a2a2a` | Primary text |
| `--color-neutral-900` | `#fafafa` | `#141414` | Heading text |
| `--color-neutral-950` | `#ffffff` | `#0a0a0a` | Highest emphasis text |

Dark mode inverts the neutral scale: backgrounds are dark (low numbers), text is light (high numbers). Light mode uses the standard Tailwind scale.

### Semantic Palette

Used for status indicators, quality gates, and data visualisation.

| Token | Value | Usage |
|---|---|---|
| `--color-success` | `#22c55e` | Analysis passed, positive metric, success state |
| `--color-warning` | `#f59e0b` | Warning level, needs attention, pending state |
| `--color-error` | `#ef4444` | Error state, critical warning, failure |
| `--color-info` | `#3b82f6` | Informational, neutral notification |
| `--color-analysis-python` | `#3776ab` | Python in language distribution charts |
| `--color-analysis-javascript` | `#f7df1e` | JavaScript in language distribution charts |
| `--color-analysis-typescript` | `#3178c6` | TypeScript in language distribution charts |
| `--color-analysis-java` | `#ed8b00` | Java in language distribution charts |
| `--color-analysis-go` | `#00add8` | Go in language distribution charts |
| `--color-analysis-rust` | `#dea584` | Rust in language distribution charts |
| `--color-analysis-other` | `#737373` | Fallback for unrecognised languages |

Semantic colours remain consistent between dark and light modes. The analysis detection colours match industry-standard language colours for recognisability.

### Border Tokens

| Token | Dark Mode | Light Mode |
|---|---|---|
| `--color-border` | `#2a2a2a` | `#e5e5e5` |
| `--color-border-hover` | `#3f3f3f` | `#d4d4d4` |
| `--color-border-strong` | `#525252` | `#a3a3a3` |

---

## Typography

### Font Family

```css
--font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', Consolas, monospace;
```

- **Inter** — primary UI font. Optimised for screens, excellent legibility at small sizes.
- **JetBrains Mono** — code and data display. Used for file paths, dependency names, code snippets, and tabular data.

### Type Scale

| Token | Size | Line Height | Weight | Usage |
|---|---|---|---|---|
| `--text-xs` | 0.75rem (12px) | 1.5 | 400 | Metadata, timestamps, secondary labels |
| `--text-sm` | 0.875rem (14px) | 1.5 | 400 | Body text, table cells, descriptions |
| `--text-base` | 1rem (16px) | 1.5 | 400 | Default body text |
| `--text-lg` | 1.125rem (18px) | 1.5 | 500 | Section headings, card titles |
| `--text-xl` | 1.25rem (20px) | 1.4 | 600 | Page titles, stat values |
| `--text-2xl` | 1.5rem (24px) | 1.3 | 600 | Dashboard stat numbers |
| `--text-3xl` | 1.875rem (30px) | 1.2 | 700 | Page-level heading |

### Font Weights

| Token | Value | Usage |
|---|---|---|
| `--weight-normal` | 400 | Body text, labels |
| `--weight-medium` | 500 | Buttons, card titles, table headers |
| `--weight-semibold` | 600 | Page headings, stat values |
| `--weight-bold` | 700 | Dashboard primary number |

### Mono Type Scale

| Token | Size | Line Height | Usage |
|---|---|---|---|
| `--mono-xs` | 0.75rem (12px) | 1.4 | Dependency versions, file extensions |
| `--mono-sm` | 0.875rem (14px) | 1.4 | File paths, code snippets, table cells |
| `--mono-base` | 1rem (16px) | 1.5 | Code blocks, terminal output |

---

## Spacing

Based on a 4px grid. All spacing values are multiples of 4.

| Token | Value | Usage |
|---|---|---|
| `--space-0` | 0px | None |
| `--space-1` | 4px | Tight icon spacing, inline gaps |
| `--space-2` | 8px | Compact padding, element gaps |
| `--space-3` | 12px | Button padding, card inner padding |
| `--space-4` | 16px | Standard padding, form field gaps |
| `--space-5` | 20px | Section spacing, card margins |
| `--space-6` | 24px | Page section separation |
| `--space-8` | 32px | Card padding, modal padding |
| `--space-10` | 40px | Page content margin |
| `--space-12` | 48px | Large section breaks |
| `--space-16` | 64px | Page header bottom margin |
| `--space-20` | 80px | Maximum spacing before diminishing returns |

**Rule:** Use the smallest spacing value that achieves the desired visual separation. Prefer `--space-3` over `--space-4` where possible.

---

## Breakpoints

Responsive breakpoints follow TailwindCSS defaults.

| Name | Min Width | Target |
|---|---|---|
| `sm` | 640px | Large phones, small tablets |
| `md` | 768px | Tablets, small laptops |
| `lg` | 1024px | Desktop standard |
| `xl` | 1280px | Wide desktop |
| `2xl` | 1536px | Large monitors |

### Responsive Strategy

- **Mobile (<768px)**: Single column layout, collapsible sidebar, stacked cards
- **Tablet (768-1024px)**: Two-column dashboard, sidebar collapsed by default
- **Desktop (>1024px)**: Full sidebar, multi-column dashboard, side-by-side panels

---

## Shadows

| Token | Dark Mode | Light Mode | Usage |
|---|---|---|---|
| `--shadow-sm` | `0 1px 2px rgba(0,0,0,0.3)` | `0 1px 2px rgba(0,0,0,0.05)` | Card default |
| `--shadow-md` | `0 4px 6px rgba(0,0,0,0.4)` | `0 4px 6px rgba(0,0,0,0.07)` | Dropdown, popover |
| `--shadow-lg` | `0 10px 15px rgba(0,0,0,0.5)` | `0 10px 15px rgba(0,0,0,0.1)` | Modal, dialog |
| `--shadow-xl` | `0 20px 25px rgba(0,0,0,0.6)` | `0 20px 25px rgba(0,0,0,0.15)` | Toast, notification overlay |

Dark mode shadows are more pronounced due to deeper ambient darkness.

---

## Border Radius

| Token | Value | Usage |
|---|---|---|
| `--radius-sm` | 4px | Input fields, small badges |
| `--radius-md` | 6px | Buttons, cards, default |
| `--radius-lg` | 8px | Dialogs, modals, large cards |
| `--radius-xl` | 12px | Search bar, primary action button |
| `--radius-full` | 9999px | Badges, tags, avatars |

---

## Z-Index Scale

| Token | Value | Usage |
|---|---|---|
| `--z-base` | 0 | Page content |
| `--z-dropdown` | 10 | Dropdown menus, select options |
| `--z-sticky` | 20 | Sticky headers |
| `--z-overlay` | 30 | Modal backdrops |
| `--z-modal` | 40 | Modal dialogs |
| `--z-toast` | 50 | Toast notifications |
| `--z-tooltip` | 60 | Tooltips |

---

## Opacity Tokens

| Token | Value | Usage |
|---|---|---|
| `--opacity-disabled` | 0.4 | Disabled controls |
| `--opacity-hover` | 0.8 | Hover overlay on interactive rows |
| `--opacity-muted` | 0.6 | Muted text, secondary labels |
| `--opacity-overlay` | 0.6 | Modal backdrop |

---

## TailwindCSS Configuration Reference

```typescript
// tailwind.config.ts
export default {
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          50: 'var(--color-primary-50)',
          100: 'var(--color-primary-100)',
          200: 'var(--color-primary-200)',
          400: 'var(--color-primary-400)',
          500: 'var(--color-primary-500)',
          600: 'var(--color-primary-600)',
          700: 'var(--color-primary-700)',
          900: 'var(--color-primary-900)',
        },
        neutral: {
          50: 'var(--color-neutral-50)',
          100: 'var(--color-neutral-100)',
          200: 'var(--color-neutral-200)',
          300: 'var(--color-neutral-300)',
          400: 'var(--color-neutral-400)',
          500: 'var(--color-neutral-500)',
          600: 'var(--color-neutral-600)',
          700: 'var(--color-neutral-700)',
          800: 'var(--color-neutral-800)',
          900: 'var(--color-neutral-900)',
          950: 'var(--color-neutral-950)',
        },
        success: 'var(--color-success)',
        warning: 'var(--color-warning)',
        error: 'var(--color-error)',
        info: 'var(--color-info)',
        border: {
          DEFAULT: 'var(--color-border)',
          hover: 'var(--color-border-hover)',
          strong: 'var(--color-border-strong)',
        },
      },
      fontFamily: {
        sans: ['Inter', ...defaultFontSans],
        mono: ['JetBrains Mono', ...defaultFontMono],
      },
      fontSize: {
        xs: ['0.75rem', { lineHeight: '1.5' }],
        sm: ['0.875rem', { lineHeight: '1.5' }],
        base: ['1rem', { lineHeight: '1.5' }],
        lg: ['1.125rem', { lineHeight: '1.5', fontWeight: '500' }],
        xl: ['1.25rem', { lineHeight: '1.4', fontWeight: '600' }],
        '2xl': ['1.5rem', { lineHeight: '1.3', fontWeight: '600' }],
        '3xl': ['1.875rem', { lineHeight: '1.2', fontWeight: '700' }],
      },
      spacing: {
        18: '4.5rem',
        22: '5.5rem',
      },
      borderRadius: {
        sm: '4px',
        md: '6px',
        lg: '8px',
        xl: '12px',
      },
      boxShadow: {
        sm: 'var(--shadow-sm)',
        md: 'var(--shadow-md)',
        lg: 'var(--shadow-lg)',
        xl: 'var(--shadow-xl)',
      },
    },
  },
}
```

---

## CSS Custom Properties Setup

```css
/* styles/globals.css */
@layer base {
  :root {
    /* Light mode (default) */
    --color-neutral-50: #fafafa;
    --color-neutral-100: #f5f5f5;
    /* ... all light mode values ... */
    --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  }

  .dark {
    --color-neutral-50: #0a0a0a;
    --color-neutral-100: #141414;
    /* ... all dark mode values ... */
    --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3);
  }
}
```
