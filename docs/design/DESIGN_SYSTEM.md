# Design System

> **Document Owner:** Frontend Architecture
> **Status:** Living Document
> **Last Updated:** 2026-07-27

---

## Component Architecture

The UI is built from three layers of components:

```
┌─────────────────────────────────────┐
│  Feature Components                 │
│  (features/*/components/)           │
│                                     │
│  ProjectCard, FileUploader,         │
│  AiSummaryCard, LanguageBarChart    │
├─────────────────────────────────────┤
│  Shared Components                  │
│  (components/)                      │
│                                     │
│  DataTable, PageHeader,             │
│  ConfirmDialog, StatCard            │
├─────────────────────────────────────┤
│  UI Primitives                      │
│  (components/ui/)                   │
│                                     │
│  Button, Input, Card, Badge,        │
│  Dialog, Tabs, Select, Pagination   │
└─────────────────────────────────────┘
```

### Layer Rules

- **UI Primitives** may import only Radix UI, TailwindCSS utilities, and `lib/utils.ts`.
- **Shared Components** may import UI Primitives and `lib/`. They must not import from features.
- **Feature Components** may import Shared Components, UI Primitives, hooks, stores, and API modules. They must not import from other features.

---

## File Naming Conventions

| Asset | Convention | Example |
|---|---|---|
| React component | PascalCase | `Button.tsx`, `ProjectCard.tsx` |
| Component test | `ComponentName.test.tsx` | `Button.test.tsx` |
| Hook | camelCase with `use` prefix | `useAuth.ts`, `useProjects.ts` |
| Store | camelCase with `Store` suffix | `authStore.ts`, `uiStore.ts` |
| API module | camelCase | `projects.ts`, `analysis.ts` |
| Utility | camelCase | `utils.ts`, `constants.ts` |
| Type definition | PascalCase | `User.ts`, `ProjectResponse.ts` |
| CSS file | kebab-case | `globals.css` |

### Component File Structure

```
Button/
├── Button.tsx          ← Component implementation
├── Button.test.tsx     ← Tests
└── index.ts            ← Re-export
```

For simple components with no sub-components or tests, a single file is acceptable:

```
components/ui/Button.tsx
```

---

## Component Naming Conventions

| Pattern | Example | When to Use |
|---|---|---|
| `Noun` | `Card`, `Badge`, `Table` | Generic UI primitives |
| `NounNoun` | `ProjectCard`, `MetricGrid` | Feature-specific compositions |
| `VerbNoun` | `ConfirmDialog`, `GenerateButton` | Action-oriented components |
| `NounVerb` | `FileUploader`, `TechnologyBadge` | Feature + presentation |
| `useNounVerb` | `useProjectsList`, `useAnalysisDashboard` | Custom hooks |

### Prop Naming

- Use `onEventName` for callbacks: `onClick`, `onSubmit`, `onPageChange`
- Use `is` prefix for boolean props: `isLoading`, `isDisabled`, `isSelected`
- Use `render` prefix for render props: `renderEmpty`, `renderError`
- Avoid abbreviations: use `maximum` not `max`, `minimum` not `min`

---

## Folder Organisation

```
src/
├── api/                  # API client and per-domain API functions
├── routes/               # Route configuration
├── layouts/              # Page layouts
├── features/             # Domain modules
│   ├── auth/
│   ├── projects/
│   ├── uploads/
│   ├── analysis/
│   ├── ai/
│   └── settings/
├── hooks/                # Shared custom hooks (React Query wrappers)
├── stores/               # Zustand stores
├── components/           # Shared components
│   └── ui/               # Design system primitives
├── lib/                  # Utilities, constants, types
└── styles/               # Global styles
```

### Feature Module Layout

```
features/projects/
├── components/
│   ├── ProjectCard.tsx
│   ├── ProjectList.tsx
│   └── ProjectForm.tsx
├── pages/
│   ├── ProjectsPage.tsx
│   ├── NewProjectPage.tsx
│   └── ProjectDetailPage.tsx
└── index.ts              ← Barrel export of public components
```

Feature modules may also contain:
- `hooks/` — if the hooks are specific to this feature and not shared
- `types.ts` — if the types are specific to this feature

---

## Import Order

Within a file, imports are grouped and ordered as follows, separated by blank lines:

1. **External dependencies** — React, React Router, Radix UI, TanStack libraries
2. **Internal modules** — `@/api/`, `@/hooks/`, `@/stores/`, `@/lib/`
3. **Components** — `@/components/`, `@/components/ui/`
4. **Relative imports** — `./Component`, `../hooks/`
5. **Styles** — CSS imports (rare)

```typescript
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'

import { getProjects } from '@/api/projects'
import { useAuth } from '@/hooks/useAuth'

import { PageHeader } from '@/components/PageHeader'
import { Button } from '@/components/ui/Button'

import { ProjectCard } from './ProjectCard'
```

---

## Path Aliases

TypeScript path aliases are configured in `tsconfig.json`:

```json
{
  "paths": {
    "@/*": ["src/*"]
  }
}
```

All imports within `src/` use the `@/` alias. Avoid deep relative imports (`../../../`).

---

## Barrel Exports

Each `components/ui/` component and each feature module exports a barrel `index.ts`:

```typescript
// components/ui/index.ts
export { Button } from './Button'
export { Card } from './Card'
export { Badge } from './Badge'
```

Feature components import from the barrel:

```typescript
import { Button, Card, Badge } from '@/components/ui'
```

**Exception:** Components with heavy dependencies (charts, diagrams) should be imported directly to preserve tree-shaking:

```typescript
import { LanguageBarChart } from '@/features/analysis/components/LanguageBarChart'
```

---

## Component API Patterns

### Standard Component Props

```typescript
interface ButtonProps {
  children: ReactNode
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  isDisabled?: boolean
  isLoading?: boolean
  onClick?: () => void
  type?: 'button' | 'submit' | 'reset'
}
```

### Polymorphic Components

Use `asChild` pattern from Radix for components that need to render as a different element:

```typescript
// Button renders as <button> by default, but can be an <a> or <Link>
<Button asChild>
  <Link to="/projects">View Projects</Link>
</Button>
```

### Data Display Components

```typescript
interface DataTableProps<T> {
  columns: ColumnDef<T>[]
  data: T[]
  isLoading?: boolean
  isError?: boolean
  emptyMessage?: string
  pagination?: PaginationState
  onPaginationChange?: (state: PaginationState) => void
  sortBy?: string
  sortDir?: 'asc' | 'desc'
  onSortChange?: (column: string, dir: 'asc' | 'desc') => void
}
```

---

## State Management Conventions

### React Query Key Convention

```typescript
// Query keys follow [domain, ...identifiers, ...params]
export const queryKeys = {
  projects: {
    all: ['projects'] as const,
    list: (page: number, size: number) => ['projects', 'list', { page, size }] as const,
    detail: (id: number) => ['projects', id] as const,
  },
  uploads: {
    byProject: (projectId: number, page: number, size: number) =>
      ['projects', projectId, 'uploads', { page, size }] as const,
    detail: (id: number) => ['uploads', id] as const,
  },
  analysis: {
    detail: (id: number) => ['analysis', id] as const,
    dashboard: (id: number) => ['analysis', id, 'dashboard'] as const,
    files: (id: number, filters: FileFilters) => ['analysis', id, 'files', filters] as const,
    technologies: (id: number) => ['analysis', id, 'technologies'] as const,
    dependencies: (id: number, filters: DependencyFilters) =>
      ['analysis', id, 'dependencies', filters] as const,
    metrics: (id: number) => ['analysis', id, 'metrics'] as const,
    warnings: (id: number, filters: WarningFilters) =>
      ['analysis', id, 'warnings', filters] as const,
  },
  ai: {
    summary: (id: number) => ['ai', id, 'summary'] as const,
    architecture: (id: number) => ['ai', id, 'architecture'] as const,
    techDebt: (id: number) => ['ai', id, 'techDebt'] as const,
    modernization: (id: number) => ['ai', id, 'modernization'] as const,
    explanation: (analysisId: number, fileId: number) =>
      ['ai', analysisId, 'file', fileId, 'explain'] as const,
  },
}
```

### Query Configuration Defaults

```typescript
const defaultQueryOptions = {
  staleTime: 30_000,        // 30s — data considered fresh
  gcTime: 300_000,          // 5min — keep in cache after unmount
  retry: 1,                 // retry once on failure
  refetchOnWindowFocus: false, // disable for data that rarely changes
}
```

AI queries use `staleTime: 0` to always fetch fresh content.

### Mutation Invalidation Pattern

```typescript
const { mutate: deleteProject } = useMutation({
  mutationFn: (id: number) => deleteProjectApi(id),
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: queryKeys.projects.all })
  },
})
```

---

## Accessibility Requirements

Refer to `ACCESSIBILITY.md` for complete details. Key conventions:

- All interactive elements must be keyboard accessible
- All form inputs must have associated `<label>` elements
- All icons must have `aria-hidden="true"` (decorative) or `aria-label` (informative)
- Colour is never the sole indicator of state
- Focus indicators must be visible (not `outline: none` without a replacement)
- Components using Radix UI primitives inherit built-in ARIA attributes
