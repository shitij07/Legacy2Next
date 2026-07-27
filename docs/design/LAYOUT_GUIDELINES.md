# Layout Guidelines

> **Document Owner:** Frontend Architecture
> **Status:** Living Document
> **Last Updated:** 2026-07-27

---

## Global Layout Structure

```
┌─────────────────────────────────────────────────┐
│  Header                                         │
│  ┌──────┬──────────────────────────────────────┐│
│  │ Menu │ Breadcrumbs              User Menu   ││
│  └──────┴──────────────────────────────────────┘│
├──────┬──────────────────────────────────────────┤
│      │                                          │
│      │  Page Header                             │
│ Side │  ┌────────────────────────────────────┐  │
│ bar  │  │ Title              Action Buttons  │  │
│      │  └────────────────────────────────────┘  │
│      │                                          │
│      │  Tab Navigation                          │
│      │  ┌──┬──┬──┬──┬──┐                        │
│      │  │T1│T2│T3│T4│T5│                        │
│      │  └──┴──┴──┴──┴──┘                        │
│      │                                          │
│      │  Content Area                            │
│      │  ┌────────────────────────────────────┐  │
│      │  │                                    │  │
│      │  │  (component content)               │  │
│      │  │                                    │  │
│      │  └────────────────────────────────────┘  │
│      │                                          │
└──────┴──────────────────────────────────────────┘
```

### Height Measurements

| Element | Height | Notes |
|---|---|---|
| Header | 56px (14) | Fixed top bar |
| Sidebar | 100vh - 56px | Full viewport below header |
| Page header | variable | Includes title + actions |
| Tab bar | 40px (10) | Includes bottom border |

---

## Sidebar

### Desktop (>=1024px)

- Fixed width: 240px (60)
- Position: fixed left, below header
- Contains: navigation links, project list, user info
- Always visible
- Background: `neutral-100`

### Mobile/Tablet (<1024px)

- Hidden by default
- Opens as overlay drawer (300px width)
- Backdrop: `neutral-950` at 60% opacity
- Toggle button in header
- Closes on navigation click

### Sidebar Navigation Items

```
┌──────────────────────┐
│ 🏠  Overview         │  ← Navigation link
│ ──────────────────── │
│ 📁  Projects         │
│ │  Project Alpha     │  ← Nested project list
│ │  Project Beta      │
│ └  3 more...         │
│ ──────────────────── │
│ ⚙️  Settings         │
│                      │
│ ──────────────────── │
│ 👤  user@email.com   │  ← User info + logout
└──────────────────────┘
```

Each nav item is 40px (10) tall, with 8px horizontal padding. Active item uses `primary-500` text colour with a 2px left border indicator.

---

## Header

- Height: 56px (14)
- Background: `neutral-100` with 1px bottom border
- Contains (left to right):
  - Mobile hamburger menu button
  - Breadcrumb trail (page hierarchy)
  - Theme toggle (dark/light)
  - User dropdown menu

### Breadcrumb Format

```
Projects > My App > Analysis #42 > Files
```

Each segment is a link (`neutral-700`, hover `neutral-800`). The final segment is plain text (`neutral-800`). Segments are separated by `>` with 8px horizontal margin.

---

## Grid System

### Page Layout Grid

Pages use CSS Grid with the following template:

```css
.page-layout {
  display: grid;
  grid-template-columns: 240px 1fr;
  grid-template-rows: 56px 1fr;
  grid-template-areas:
    "sidebar header"
    "sidebar content";
}
```

### Content Area Grid

The content area uses a 12-column grid:

```css
.content-area {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 16px;
}
```

### Common Column Spans

| Content Type | Columns | Breakpoint Behaviour |
|---|---|---|
| Full-width content | 12 / 12 | Stays full width on all screens |
| Two-column stats | 6 / 12 each | Stacks to full width below `md` |
| Three-column cards | 4 / 12 each | 2-col at `md`, 1-col at `sm` |
| Four-column metrics | 3 / 12 each | 2-col at `md`, 1-col at `sm` |
| Sidebar + content panel | 3 + 9 / 12 | Stacks below `lg` |
| Form | 6 / 12 centered | Full width below `md` |

---

## Page Types

### Dashboard Page (Analysis Dashboard)

```
┌──────────────────────────────────────────────┐
│  Project Name  >  Analysis #42     COMPLETED │  ← Page header
├──────────────────────────────────────────────┤
│  42 files │ 5 tech │ 20 deps │ 3 warnings    │  ← Stat cards row
├──────────────────────────────────────────────┤
│  Overview │ Files │ Tech │ Deps │ ...         │  ← Tab bar
├──────────────────────────────────────────────┤
│                                              │
│  ┌──────────────────┐  ┌──────────────────┐  │
│  │ Language Dist.   │  │ Primary Metrics  │  │  ← Two-column
│  │ [bar chart]      │  │ · LOC: 12,000    │  │
│  │                  │  │ · Files: 42      │  │
│  └──────────────────┘  └──────────────────┘  │
│                                              │
│  ┌──────────────────────────────────────────┐│
│  │ Technologies                             ││  ← Full width
│  │ [Python] [Django] [PostgreSQL] ...       ││
│  └──────────────────────────────────────────┘│
└──────────────────────────────────────────────┘
```

### List Page (Projects, Uploads)

```
┌──────────────────────────────────────────────┐
│  Projects                    [+ New Project] │  ← Page header
├──────────────────────────────────────────────┤
│                                              │
│  ┌──────────────────────────────────────────┐│
│  │ Project Card (name, desc, lang, status)  ││
│  ├──────────────────────────────────────────┤│
│  │ Project Card                             ││
│  ├──────────────────────────────────────────┤│
│  │ Project Card                             ││
│  └──────────────────────────────────────────┘│
│                                              │
│  Page 1 of 3  [<] [1] [2] [3] [>]           │  ← Pagination
└──────────────────────────────────────────────┘
```

### Detail Page (Project, Analysis)

```
┌──────────────────────────────────────────────┐
│  Project Name              [Edit] [Delete]   │  ← Page header
├──────────────────────────────────────────────┤
│  Uploads │ Analyses                          │  ← Tabs
├──────────────────────────────────────────────┤
│                                              │
│  Tab content area                            │
│                                              │
└──────────────────────────────────────────────┘
```

---

## Content Density Rules

### When to Use Compact Layout

- Tables with many columns (files, dependencies, warnings)
- Stat card rows (4+ metrics)
- Sidebar navigation items
- Filter bars with multiple controls

### When to Use Generous Spacing

- Empty states (no data messages)
- Error states (error messages with retry)
- AI insight content (markdown-rendered text)
- First-run onboarding prompts

### Stat Card Density

```
Compact:                    Generous:
┌──────────┐                ┌──────────────────┐
│ 42 files │                │ Total Files      │
│          │                │                  │
│          │                │       42         │
└──────────┘                │                  │
                            │ Up from last run │
                            └──────────────────┘
```

Use compact stat cards for dashboard metric rows (default). Use generous stat cards for landing pages or empty states.

---

## Empty States

Every list page must handle the empty state:

```
┌──────────────────────────────────────────────┐
│                                              │
│              📂 No projects yet               │
│                                              │
│    Create your first project to get started  │
│                                              │
│          [+ Create Project]                  │
│                                              │
└──────────────────────────────────────────────┘
```

Empty states include:
- Relevant icon (from Lucide)
- Primary message (what's missing)
- Secondary message (what to do)
- Call-to-action button (if applicable)

---

## Error States

Error states follow the same layout as empty states but communicate failure instead of absence:

```
┌──────────────────────────────────────────────┐
│                                              │
│              ⚠️ Failed to load projects       │
│                                              │
│    This could be a network issue. Try again. │
│                                              │
│              [Try Again]                     │
│                                              │
└──────────────────────────────────────────────┘
```

---

## Loading States

Loading states use skeleton placeholders that match the page layout:

```
┌──────────────────────────────────────────────┐
│  ┌──────────┐ ┌──────────┐ ┌──────────┐     │
│  │ ░░░░░░░░ │ │ ░░░░░░░░ │ │ ░░░░░░░░ │     │  ← Skeleton cards
│  │ ░░░░░░░░ │ │ ░░░░░░░░ │ │ ░░░░░░░░ │     │
│  └──────────┘ └──────────┘ └──────────┘     │
│                                              │
│  ┌──────────────────────────────────────────┐│
│  │ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  ││  ← Skeleton table
│  │ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  ││
│  │ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  ││
│  └──────────────────────────────────────────┘│
└──────────────────────────────────────────────┘
```

---

## Responsive Behaviour

### Breakpoint Summary

| Viewport | Sidebar | Layout | Cards | Tables |
|---|---|---|---|---|
| <768px | Drawer (hidden) | Single column | Stacked | Horizontal scroll |
| 768-1024px | Collapsed (icon only) | 2-column grid | 2 per row | Scrollable |
| 1024-1280px | Expanded | 12-col grid | 3-4 per row | Full width |
| >1280px | Expanded | 12-col grid | 4 per row | Full width + optional columns |

### Navigation Responsiveness

- Below 768px: bottom tab bar with primary actions (optional future enhancement)
- Below 1024px: sidebar collapses to icon-only rail (40px width)
- Above 1024px: full sidebar with labels

### Content Responsiveness

- Tables: horizontal scroll container on small screens
- Charts: responsive SVG (Recharts handles this natively)
- Forms: full-width below `md`, max-width 480px centered above
- Stat cards: wrap to next row when container width is exceeded
