# Iconography

> **Document Owner:** Frontend Architecture
> **Status:** Living Document
> **Last Updated:** 2026-07-27

---

## Icon Library

**Lucide React** is the exclusive icon library for Legacy2Next.

### Rationale

- Consistent stroke-based design language (2px stroke, rounded caps, rounded joins)
- Tree-shakeable — only imported icons are bundled
- 1,400+ icons covering all use cases
- Active maintenance, frequent updates
- First-class React support via `lucide-react` package
- MIT license

### What Is Not Allowed

- Emoji as icons
- Font Awesome, Material Icons, or other icon sets
- Custom SVG icons (except for the product logo and brand mark)
- Inline SVG paths in components

---

## Icon Sizing

| Size | Pixel Value | Usage |
|---|---|---|
| `xs` | 14px | Inline with small text, table cell indicators |
| `sm` | 16px | Inline with body text, button icons |
| `md` | 20px | Standard icon size, navigation items |
| `lg` | 24px | Page headers, empty state icons |
| `xl` | 32px | Feature illustrations, large indicators |
| `2xl` | 48px | Empty state hero icons, error state icons |

### Icon Size Selection Rules

- **Navigation icons**: `md` (20px)
- **Button icons**: `sm` (16px) for standard buttons, `md` (20px) for icon-only buttons
- **Inline with text**: `xs` (14px) or `sm` (16px), matched to text size
- **Empty/error states**: `2xl` (48px)
- **Status indicators**: `sm` (16px) for inline dots, `md` (20px) for standalone
- **Table sort indicators**: `xs` (14px)

---

## Icon Colouring

Icons inherit their colour from the parent text colour by default. When an icon needs explicit colouring, use these rules:

| Context | Colour | Example |
|---|---|---|
| Navigation | `neutral-700` | Sidebar and header icons |
| Active navigation | `primary-500` | Currently selected sidebar item |
| Button | Button text colour | Delete (`error`), Create (`primary`) |
| Status indicator | Semantic colour | Success (`success`), Warning (`warning`) |
| Empty state | `neutral-400` | Large hero icons |
| Interactive (hover) | `neutral-800` | Clickable icon buttons |

---

## Icon Selection Guide

### Navigation Icons

| Route | Lucide Icon |
|---|---|
| Dashboard / Overview | `LayoutDashboard` |
| Projects | `FolderKanban` |
| Settings | `Settings` |
| User menu | `UserCircle` |
| Logout | `LogOut` |

### Action Icons

| Action | Lucide Icon |
|---|---|
| Create / Add | `Plus` |
| Edit | `Pencil` |
| Delete / Remove | `Trash2` |
| Close / Dismiss | `X` |
| Back / Go back | `ArrowLeft` |
| Forward / Next | `ArrowRight` |
| Save | `Save` |
| Upload | `Upload` |
| Download | `Download` |
| Search | `Search` |
| Filter | `Filter` |
| Sort | `ArrowUpDown` |
| Refresh / Retry | `RefreshCw` |
| Copy | `Copy` |
| External link | `ExternalLink` |
| Menu / Hamburger | `Menu` |
| More options | `MoreHorizontal` or `MoreVertical` |

### Status Icons

| Status | Lucide Icon |
|---|---|
| Success / Completed | `CheckCircle2` |
| Warning | `AlertTriangle` |
| Error / Failed | `XCircle` |
| Info | `Info` |
| Pending / In progress | `Loader2` (with spin animation) |
| Disabled | `Ban` |
| Empty / No data | `Inbox` |

### Content Icons

| Content | Lucide Icon |
|---|---|
| File | `File` |
| Directory / Folder | `Folder` |
| Code | `Code2` |
| Language | `FileCode` |
| Dependency | `Package` |
| Technology | `Cpu` |
| Metric | `BarChart3` |
| Warning / Alert | `AlertTriangle` |
| AI / Intelligence | `Brain` |
| Architecture | `Building2` |
| Modernisation | `Rocket` |
| Technical debt | `CreditCard` |
| User | `User` |
| Calendar / Date | `Calendar` |
| Tag | `Tag` |

---

## Icon Placement

### Icons in Buttons

| Button Type | Icon Position | Margin |
|---|---|---|
| Icon + label | Left of label | 8px (`mr-2`) |
| Icon only | Centered | None |
| Loading state | Spinner replaces icon | Same position |

### Icons in Navigation

- Navigation items: icon on the left, 12px from edge, 8px gap to label
- Collapsed sidebar: icon only, centered (16px from each side)

### Icons in Empty/Error States

- Centered above text
- 16px bottom margin to title
- Not wrapped in decorative backgrounds or circles

---

## Accessibility

### Decorative Icons

Icons that do not convey meaning independently (they accompany visible text) use `aria-hidden`:

```tsx
<Button>
  <Plus className="mr-2" aria-hidden="true" />
  Create Project
</Button>
```

### Informative Icons

Icons that convey meaning without accompanying text require an `aria-label`:

```tsx
<button aria-label="Delete project">
  <Trash2 aria-hidden="true" />
</button>
```

The `aria-label` is on the interactive element, not the icon itself. The icon remains `aria-hidden`.

---

## Prohibited Icon Usage

- Do not animate icons that are not explicitly loading indicators (only `Loader2` and `RefreshCw` may spin).
- Do not use filled icon variants (Lucide icons are stroke-based by design).
- Do not stack icons inside decorative containers (circles, squares, coloured backgrounds).
- Do not resize icons smaller than 14px or larger than 48px.
- Do not use different icon sizes for the same context within a single page.
