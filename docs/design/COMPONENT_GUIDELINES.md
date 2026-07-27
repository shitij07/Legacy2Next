# Component Guidelines

> **Document Owner:** Frontend Architecture
> **Status:** Living Document
> **Last Updated:** 2026-07-27

---

## Component Reference

This document defines the API contracts, usage rules, and behaviour of every shared UI component. Feature components are defined within their respective feature modules.

---

## Button

### Props

```typescript
interface ButtonProps {
  children: ReactNode
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  isDisabled?: boolean
  isLoading?: boolean
  onClick?: () => void
  type?: 'button' | 'submit' | 'reset'
  asChild?: boolean      // Radix slot — renders as child element
  className?: string
}
```

### Variants

| Variant | Background | Text | Border | Usage |
|---|---|---|---|---|
| `primary` | `primary-500` | `white` | None | Primary actions (Create, Save, Submit) |
| `secondary` | `neutral-200` | `neutral-800` | `neutral-300` | Secondary actions (Cancel, Back) |
| `ghost` | Transparent | `neutral-700` | None | Tertiary actions, icon buttons |
| `danger` | `error` | `white` | None | Destructive actions (Delete, Remove) |

### States

- **Default**: As defined above
- **Hover**: Darken background by 10% (primary: `primary-600`, danger: darker red)
- **Active**: Darken further by 5%
- **Disabled**: 40% opacity, no hover effects, `cursor: not-allowed`
- **Loading**: Show spinner before text, disable interaction. Width preserved to prevent layout shift.

### Sizing

| Size | Height | Padding X | Font Size |
|---|---|---|---|
| `sm` | 32px | 12px | 14px |
| `md` | 40px | 16px | 14px |
| `lg` | 48px | 20px | 16px |

### Usage Rules

- One primary button per section. Other actions use `secondary` or `ghost`.
- Danger variant requires confirmation dialog for destructive actions.
- Loading state must be used for all async actions (API calls).
- `asChild` enables rendering as `<a>` or `<Link>` for navigation buttons.

---

## Input

### Props

```typescript
interface InputProps {
  label: string
  name: string
  type?: 'text' | 'email' | 'password' | 'number' | 'search'
  placeholder?: string
  value?: string
  onChange?: (value: string) => void
  error?: string
  isDisabled?: boolean
  isRequired?: boolean
  helperText?: string
  className?: string
}
```

### Layout

```
┌──────────────────────────────────────────────┐
│ Label *                                       │  ← 14px, neutral-700
│ ┌──────────────────────────────────────────┐  │
│ │ Placeholder text                    👁️   │  │  ← 36px height, 12px padding
│ └──────────────────────────────────────────┘  │
│ Helper text or error message                  │  ← 12px, neutral-500 or error
└──────────────────────────────────────────────┘
```

### States

- **Default**: Border `neutral-300`, background `neutral-50`
- **Focus**: Border `primary-500`, ring `primary-500/20` (3px)
- **Error**: Border `error`, ring `error/20`, error message below
- **Disabled**: 40% opacity, no interaction
- **Filled**: Border `neutral-400`

### Usage Rules

- Every input must have an associated `<label>` (visible, not visually hidden).
- Error state must include both the red border and an error message below the input.
- Helper text is for context (password requirements, format hints). Do not use it for error messages.
- Search inputs use `type="search"` with an optional clear button.

---

## Card

### Props

```typescript
interface CardProps {
  children: ReactNode
  variant?: 'default' | 'elevated' | 'bordered'
  isInteractive?: boolean  // hover/focus styles for clickable cards
  onClick?: () => void
  padding?: 'sm' | 'md' | 'lg'
  className?: string
}
```

### Variants

| Variant | Background | Shadow | Border |
|---|---|---|---|
| `default` | `neutral-100` | None | `neutral-200` |
| `elevated` | `neutral-100` | `shadow-sm` | None |
| `bordered` | Transparent | None | `neutral-200` |

### Usage Rules

- Use `default` for most cards (stat cards, analysis cards).
- Use `elevated` for floating panels (dropdowns, popovers, dialogs).
- Use `bordered` when the card needs to sit on a coloured background.
- Interactive cards (`isInteractive`) get hover: 1px border highlight + subtle background shift.
- Cards in a grid must have equal height. Use `flex flex-col` and `mt-auto` on the last child if needed.

---

## Badge

### Props

```typescript
interface BadgeProps {
  children: ReactNode
  variant?: 'default' | 'success' | 'warning' | 'error' | 'info'
  size?: 'sm' | 'md'
  isDot?: boolean   // Show dot indicator only, no text
  className?: string
}
```

### Variants

| Variant | Background | Text | Border | When to Use |
|---|---|---|---|---|
| `default` | `neutral-200` | `neutral-700` | None | Generic tag, file extension |
| `success` | `success` at 15% opacity | `success` | None | Completed, passed |
| `warning` | `warning` at 15% opacity | `warning` | None | Pending, needs review |
| `error` | `error` at 15% opacity | `error` | None | Failed, critical |
| `info` | `info` at 15% opacity | `info` | None | Informational |

### Usage Rules

- Use `size="sm"` for inline tags (technology names, file extensions).
- Use `size="md"` for status indicators (analysis status, upload status).
- Dot variant is for compact status indicators in tables.
- Badges are not interactive. For interactive tags, use buttons styled as badges.

---

## DataTable

### Props

```typescript
interface DataTableProps<T extends Record<string, unknown>> {
  columns: ColumnDef<T>[]
  data: T[]
  isLoading?: boolean
  isError?: boolean
  errorMessage?: string
  emptyMessage?: string
  emptyAction?: { label: string; onClick: () => void }
  pagination?: {
    page: number
    size: number
    total: number
    pages: number
    onPageChange: (page: number) => void
    onSizeChange: (size: number) => void
  }
  sortBy?: string
  sortDir?: 'asc' | 'desc'
  onSortChange?: (column: string, direction: 'asc' | 'desc') => void
  onRowClick?: (row: T) => void
  className?: string
}
```

### Column Definition

```typescript
interface ColumnDef<T> {
  id: string
  header: string
  accessorKey?: keyof T
  accessorFn?: (row: T) => string | number | ReactNode
  cell?: (value: unknown, row: T) => ReactNode
  isSortable?: boolean
  width?: string       // CSS width value
  isVisible?: boolean  // Responsive visibility
  hideBelow?: 'sm' | 'md' | 'lg'  // Hide on small screens
  align?: 'left' | 'center' | 'right'
}
```

### States

| State | Display |
|---|---|
| Loading | Skeleton rows (5 rows, matching column widths) |
| Empty | `<EmptyState>` with message and optional action |
| Error | `<ErrorState>` with message and retry button |
| Data | Standard table rendering |
| Single row click | Row highlight (`neutral-200`), cursor pointer |

### Responsive Column Visibility

```typescript
// Example: columns that hide on small screens
const columns = [
  { id: 'name', header: 'Name', ... },
  { id: 'extension', header: 'Ext', hideBelow: 'sm' },
  { id: 'size', header: 'Size', hideBelow: 'md' },
  { id: 'language', header: 'Language', hideBelow: 'md' },
  { id: 'status', header: 'Status', hideBelow: 'lg' },
]
```

### Usage Rules

- Use DataTable for all tabular data (files, dependencies, warnings, projects).
- Provide `pagination` prop for lists that return paginated API responses.
- Always include `emptyMessage` for the empty state.
- Always include `isLoading` — never handle loading state externally.
- Column widths should be proportional to content. Use `width` sparingly (for columns that need fixed width like status badges).

---

## Dialog (Modal)

### Props

```typescript
interface DialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  title: string
  description?: string
  children: ReactNode
  footer?: ReactNode
  size?: 'sm' | 'md' | 'lg'
}
```

### Behaviour

- **Backdrop**: `neutral-950` at 60% opacity, click to close
- **Escape**: Closes dialog
- **Focus trap**: Tab cycles within dialog
- **Scroll**: Body scroll is locked when dialog is open
- **Enter**: Submits form if present
- **Animation**: See `MOTION_GUIDELINES.md` — §Component-Specific Animations for timing and easing

### Usage Rules

- Use for confirmations (`ConfirmDialog` wrapper), forms, and detail views.
- Do not use for transient notifications (use Sonner toast instead).
- Title should be a concise action phrase ("Delete Project", "Edit Name").
- Description provides context for the action.
- Footer typically contains Cancel + Confirm buttons.

---

## Tabs

### Props

```typescript
interface TabsProps {
  tabs: { id: string; label: string; count?: number; isDisabled?: boolean }[]
  activeTab: string
  onTabChange: (tabId: string) => void
  variant?: 'underline' | 'pills'
  className?: string
}
```

### Variants

| Variant | Active Indicator | Usage |
|---|---|---|
| `underline` | Bottom border on active tab | Page-level section navigation |
| `pills` | Filled background on active tab | Filter-style selection, sub-sections |

### Behaviour

- Active tab has `primary-500` text colour + bottom border (underline) or filled background (pills)
- Tab count badge shown when `count` is provided: small badge next to label
- Disabled tabs are visually dimmed (40% opacity) and non-interactive
- Tab content is loaded lazily — only the active tab renders its children
- Tab state is reflected in URL query parameter when used at page level

---

## Pagination

### Props

```typescript
interface PaginationProps {
  page: number
  size: number
  total: number
  pages: number
  onPageChange: (page: number) => void
  onSizeChange?: (size: number) => void
  pageSizeOptions?: number[]
}
```

### Layout

```
Showing 1-20 of 142    [<] [1] [2] [3] ... [8] [>]    20 per page ▼
```

### Behaviour

- Previous/Next buttons disabled at boundaries
- Show first, last, and ±2 pages around current
- Ellipsis (...) for gaps
- Page size selector defaults to `[20, 50, 100]`
- Total count and range shown on the left

---

## Skeleton

### Props

```typescript
interface SkeletonProps {
  variant?: 'text' | 'card' | 'table-row' | 'circle'
  width?: string | number
  height?: string | number
  count?: number        // Repeat n times
  className?: string
}
```

### Animation

CSS keyframe animation: `pulse` (opacity 0.3 → 0.7 → 0.3) over 1.5s.

### Usage Rules

- Use for all initial loading states.
- Match skeleton shape to the content it replaces.
- Do not use for mutation loading (use `Button.isLoading` instead).
- Do not nest skeletons inside other skeletons.

---

## EmptyState

### Props

```typescript
interface EmptyStateProps {
  icon?: LucideIcon
  title: string
  description?: string
  action?: { label: string; onClick: () => void }
  className?: string
}
```

### Layout

```
          ┌──────────────────────┐
          │      (icon)          │  ← 48px, neutral-400
          │                      │
          │  No projects yet     │  ← 16px, neutral-800, semibold
          │                      │
          │  Create your first   │  ← 14px, neutral-600
          │  project to get      │
          │  started.            │
          │                      │
          │  [+ Create Project]  │  ← Button component
          └──────────────────────┘
```

### Usage Rules

- Every list page must have an empty state.
- Title is a concise statement of what's missing.
- Description explains what the user should do.
- Action button is optional (present when the user can take action from this state).

---

## ErrorState

### Props

```typescript
interface ErrorStateProps {
  title?: string
  message?: string
  onRetry?: () => void
  className?: string
}
```

### Layout

```
          ┌──────────────────────┐
          │    ⚠️ (error icon)   │  ← 48px, error
          │                      │
          │  Failed to load      │  ← 16px, neutral-800, semibold
          │                      │
          │  This could be a     │  ← 14px, neutral-600
          │  network issue.      │
          │                      │
          │  [Try Again]         │  ← Button component
          └──────────────────────┘
```

### Usage Rules

- Default title: "Failed to load [resource]"
- Default message: "This could be a network issue. Please try again."
- Retry button calls the query/mutation refetch function.
- Error boundaries use this component as fallback UI.

---

## ConfirmDialog

### Props

```typescript
interface ConfirmDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  title: string
  description: string
  confirmLabel?: string
  cancelLabel?: string
  variant?: 'default' | 'danger'
  isLoading?: boolean
  onConfirm: () => void
}
```

### Behaviour

- Wraps `Dialog` with confirm/cancel buttons
- Danger variant: confirm button is `danger` variant
- Loading state: confirm button shows spinner, disables interaction
- Escape and Cancel both close the dialog without action

### Usage Rules

- Use for all destructive actions (delete, remove, reset).
- Use for actions that cannot be undone or have significant impact.
- Title should be a question: "Delete project?" not "Project deletion".
- Description explains the consequences: "This will permanently delete all uploads and analyses."

---

## PageHeader

### Props

```typescript
interface PageHeaderProps {
  title: string
  description?: string
  breadcrumbs?: { label: string; href?: string }[]
  actions?: ReactNode    // Buttons or other controls
  className?: string
}
```

### Layout

```
Projects > My App              [Edit] [Delete]  ← actions
──────────────────────────────────────────────
Analysis Dashboard                             ← title
Overview of your project's analysis results    ← description
```

### Usage Rules

- Every page uses PageHeader as the first child of its content area.
- Breadcrumbs are optional and used for nested pages (analysis, file detail).
- Actions slot contains primary action button(s) for the page.
- Title is a noun phrase ("Projects", "Analysis Dashboard"), not a verb.
