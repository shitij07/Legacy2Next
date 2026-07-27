# Frontend Principles

> **Document Owner:** Frontend Architecture
> **Status:** Living Document
> **Last Updated:** 2026-07-27

---

## Decision-Making Framework

Every frontend decision — from choosing a library to laying out a page — is evaluated against the principles below. A decision must satisfy at least the first two principles; the remaining three strengthen the case.

1. **Serve the Analysis**
2. **Respect the User's Attention**
3. **Be Predictable**
4. **Prefer Conventions Over Configuration**
5. **Ship Less Code**

---

### 1. Serve the Analysis

The frontend exists to present analysis results and AI insights. Every component, every route, every interaction either helps the user understand an analysis or gets them to one faster.

**Rules of thumb:**
- The analysis dashboard is the primary page. All other pages support it.
- If a feature does not help a user understand their legacy codebase, question whether it belongs in MVP.
- AI insights must be contextual — shown alongside the data they reference, not in a separate section or page.
- Loading states, empty states, and error states must provide analysis-specific information, not generic messages.

**Example:** The AI Summary tab sits inside the analysis dashboard, not on its own page. The user sees the analysis data and the AI-generated summary in the same context.

### 2. Respect the User's Attention

Every pixel, every animation, every interaction cost is weighed against the user's cognitive load. The UI communicates information with minimal friction.

**Rules of thumb:**
- Information density is a feature. Whitespace should separate logical groups, not pad layouts.
- Reduce chrome: borders, shadows, and backgrounds that do not convey information should be removed.
- Colour is reserved for status, categories, and data visualisation — never for decoration.
- Motion must serve comprehension (direction, hierarchy, state change) — never delight.
- Default to showing summary data; let users drill down through interaction.

**Example:** A stat card shows `42 files` in large type, not a card with an icon, a label, a shadow, and a border. The number is the information; everything else is chrome.

### 3. Be Predictable

Users should be able to predict where to find controls and how they behave. The application follows platform conventions and consistent internal patterns.

**Rules of thumb:**
- Every page follows the same structure: header → tabs → content.
- Every table looks and behaves the same way (sorting, pagination, empty state).
- Navigation state is reflected in the URL. The browser back button works as expected.
- Keyboard shortcuts are documented and consistent.
- Similar actions produce similar results. Deleting a project works the same way as deleting an upload.

**Example:** All paginated lists (projects, uploads, files, dependencies, warnings) use the same `<DataTable>` component with the same pagination controls, the same page size selector, and the same column sorting behaviour.

### 4. Prefer Conventions Over Configuration

Standardise early. A shared component should require minimal per-instance configuration. When a pattern repeats, extract it into a reusable abstraction.

**Rules of thumb:**
- Three occurrences of similar code → extract into a shared component or hook.
- Component APIs should have sensible defaults. Optional props should be the exception, not the rule.
- File organisation follows a documented convention (see `DESIGN_SYSTEM.md`). Do not create exceptions without discussion.
- State management follows a documented pattern: React Query for server state, Zustand for client state. Do not introduce new state solutions without team consensus.

**Example:** The `<DataTable>` component accepts columns, data, and pagination props. Sorting, filtering, and row rendering are built-in. Individual pages do not configure table behaviour — they just pass data.

### 5. Ship Less Code

Smaller bundles, fewer dependencies, less complexity. Every dependency must justify its weight.

**Rules of thumb:**
- Before adding a dependency, ask: can we achieve this with 50 lines of our own code? If yes, write it.
- Prefer built-in browser APIs over library abstractions (e.g., CSS Grid over a layout library, native dialog over a modal library).
- Remove dead code aggressively. Unused components, hooks, and utilities must be deleted.
- Tree-shakeable imports only. Never import from a library's barrel file if deep imports are supported.

**Example:** We use Radix UI primitives (unstyled, accessible) + Tailwind instead of MUI. This saves ~80KB from the bundle and gives full control over styling.

---

## Technology Principles

### TypeScript

- Strict mode enabled. No `any` unless absolutely necessary and justified with a comment.
- Share types between API layer and components. The API client returns typed responses; components receive typed props.
- Prefer `interface` for public API shapes (props, state) and `type` for unions, intersections, and mapped types.

### React

- Functional components with hooks. No class components.
- Custom hooks encapsulate reusable stateful logic. Hooks that call React Query go in `hooks/`. Hooks that wrap component logic stay co-located with the component.
- Server state belongs in React Query, not in `useState` or `useReducer`.
- Props are typed with `interface ComponentNameProps`. Destructure props in the function signature.

### State Management

| State Category | Tool | Location |
|---|---|---|
| Server data (API responses) | React Query | `hooks/*.ts` |
| Auth tokens and user | Zustand | `stores/authStore.ts` |
| UI state (sidebar, theme) | Zustand | `stores/uiStore.ts` |
| Form state | React Hook Form | Co-located with form component |
| URL state | React Router | `routes/index.tsx` |

### Styling

- TailwindCSS utility classes for all styling. No CSS modules, no styled-components.
- Extract repeated utility combinations into component classes using `cn()` helper.
- Dark mode via `class="dark"` on `<html>`. All components must render correctly in both modes.
- Custom CSS only for keyframe animations and Tailwind `@apply` in extreme cases of repetition.

---

## Code Review Checklist

Every pull request is evaluated against these questions:

1. Does this change serve the analysis workflow?
2. Does it respect the user's attention (no decorative elements, appropriate information density)?
3. Is it predictable (follows established patterns, matches user expectations)?
4. Does it follow conventions (component structure, naming, file organisation)?
5. Could it be implemented with less code (fewer dependencies, more reuse)?
6. Are all states handled (loading, empty, error, success)?
7. Is it accessible (keyboard navigation, screen reader labels, colour contrast)?
8. Does it work in both dark and light mode?
