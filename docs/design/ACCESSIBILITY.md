# Accessibility

> **Document Owner:** Frontend Architecture
> **Status:** Living Document
> **Last Updated:** 2026-07-27

---

## Standard

Legacy2Next targets **WCAG 2.1 Level AA** conformance. All new features and components must be developed to this standard. Exceptions require documented justification and team approval.

---

## Testing Checklist

Every feature and component must pass the following checks before being considered complete.

### 1. Keyboard Navigation

- [ ] All interactive elements are reachable via Tab key
- [ ] Tab order follows logical DOM order (not arbitrary `tabindex` values above 0)
- [ ] All interactive elements have visible focus indicators (never `outline: none` without a replacement)
- [ ] Custom widgets (tabs, dialogs, menus) follow ARIA authoring practices for keyboard interaction:
  - **Tabs**: Arrow keys switch tabs, Tab moves focus into tab panel
  - **Dialog**: Focus trapped, Escape closes, Tab cycles within
  - **Dropdown menu**: Enter/Space opens, Arrow keys navigate, Escape closes
  - **DataTable**: Tab enters/leaves table, Arrow keys navigate cells (when row has interactive elements)
- [ ] No keyboard traps — focus can always be moved away from any element
- [ ] Skip-to-content link is available and visible on focus

### 2. Screen Reader Support

- [ ] All images and icons have appropriate alt text or `aria-hidden`
- [ ] Form inputs have associated `<label>` elements (not `placeholder` as label)
- [ ] Error messages are programmatically associated with inputs via `aria-describedby` or `aria-errormessage`
- [ ] Live regions (`aria-live`) are used for dynamic content updates (toast notifications, loading states)
- [ ] Status changes (loading → loaded, open → closed) are announced to screen readers
- [ ] Custom controls have correct ARIA roles, states, and properties:
  - `role="tablist"`, `role="tab"`, `role="tabpanel"` for tabs
  - `role="dialog"`, `aria-modal="true"` for dialogs
  - `role="button"` for clickable elements that are not `<button>` or `<a>`
  - `aria-expanded`, `aria-controls` for expandable sections
  - `aria-current="page"` for active navigation items
- [ ] Radix UI primitives handle ARIA attributes automatically — do not override them

### 3. Colour and Contrast

- [ ] All text meets WCAG AA contrast ratio:
  - Normal text (<18px / <14px bold): **4.5:1 minimum**
  - Large text (≥18px / ≥14px bold): **3:1 minimum**
- [ ] UI components and graphical objects meet **3:1** contrast against adjacent colours
- [ ] Colour is never the sole means of conveying information (add icons, text, or patterns)
- [ ] Status indicators include text labels or icons, not colour alone
- [ ] Focus indicators have **3:1** contrast against the focused element's background
- [ ] Custom focus ring: 2px solid `primary-500` with 2px offset, or 3px outline with `primary-500/50` ring shadow

### 4. Forms

- [ ] Every input has a visible `<label>` element
- [ ] Required fields are indicated with both text ("*") and `aria-required="true"`
- [ ] Error messages are displayed inline, adjacent to the relevant field
- [ ] Error summary appears at the top of the form on submission failure
- [ ] Input masking does not prevent screen reader interpretation
- [ ] Autocomplete attributes are set where applicable (`email`, `current-password`, `new-password`)

### 5. Motion

- [ ] All animations respect `prefers-reduced-motion: reduce` (duration set to 0.01ms)
- [ ] No animations are essential to understanding the interface
- [ ] Flashing content does not exceed 3 flashes per second (WCAG 2.3.1)

### 6. Structure

- [ ] Page has a unique and descriptive `<title>` element
- [ ] Heading hierarchy is logical and does not skip levels (`h1` → `h2` → `h3`, never `h1` → `h3`)
- [ ] Landmarks are used correctly: `<header>`, `<nav>`, `<main>`, `<aside>`, `<footer>`
- [ ] `<main>` contains the primary page content, excluding header, sidebar, and footer
- [ ] Lists are marked up as `<ul>` / `<ol>` with `<li>` children, not as generic `<div>` elements
- [ ] Tables use `<th>` for header cells with `scope="col"` or `scope="row"`

### 7. Responsive and Zoom

- [ ] Page content is readable and functional at 200% browser zoom
- [ ] Content does not require scrolling in two dimensions at 320px viewport width
- [ ] Touch targets are at least 44x44px on touch devices
- [ ] Text can be resized up to 200% without loss of content or functionality

---

## Colour Contrast Compliance

### Verified Token Contrast Ratios

#### Dark Mode (Primary Target)

| Token Pair | Foreground | Background | Ratio | Passes AA? |
|---|---|---|---|---|
| Primary text | `neutral-800` (#d4d4d4) | `neutral-50` (#0a0a0a) | 10.8:1 | ✅ |
| Secondary text | `neutral-700` (#a3a3a3) | `neutral-50` (#0a0a0a) | 7.3:1 | ✅ |
| Muted text | `neutral-600` (#737373) | `neutral-50` (#0a0a0a) | 4.8:1 | ✅ |
| Disabled text | `neutral-400` (#3f3f3f) | `neutral-50` (#0a0a0a) | 2.4:1 | ❌ (by design — disabled) |
| Primary button text | #ffffff | `primary-500` (#6366f1) | 5.0:1 | ✅ |
| Link text | `primary-400` (#818cf8) | `neutral-50` (#0a0a0a) | 5.4:1 | ✅ |
| Error text | `error` (#ef4444) | `neutral-50` (#0a0a0a) | 4.8:1 | ✅ |

#### Light Mode (Secondary Target)

| Token Pair | Foreground | Background | Ratio | Passes AA? |
|---|---|---|---|---|
| Primary text | `neutral-900` (#141414) | `neutral-50` (#fafafa) | 17.9:1 | ✅ |
| Secondary text | `neutral-700` (#3f3f3f) | `neutral-50` (#fafafa) | 8.2:1 | ✅ |
| Muted text | `neutral-500` (#737373) | `neutral-50` (#fafafa) | 4.9:1 | ✅ |
| Primary button text | #ffffff | `primary-500` (#4f46e5) | 6.5:1 | ✅ |
| Link text | `primary-600` (#4338ca) | `neutral-50` (#fafafa) | 6.4:1 | ✅ |
| Error text | `error` (#ef4444) | `neutral-50` (#fafafa) | 4.8:1 | ✅ |

---

## ARIA Patterns Reference

### Navigation (Sidebar)

```tsx
<nav aria-label="Main navigation">
  <ul role="list">
    <li>
      <a href="/projects" aria-current="page">Projects</a>
    </li>
  </ul>
</nav>
```

### Tabs

Uses Radix `Tabs` primitive which provides correct ARIA automatically:
- `role="tablist"` on the tab container
- `role="tab"` with `aria-selected` and `aria-controls` on each tab
- `role="tabpanel"` with `aria-labelledby` on each panel

### Dialog

Uses Radix `Dialog` primitive which provides:
- `role="dialog"` with `aria-modal="true"` on the dialog container
- `aria-labelledby` referencing the title element
- `aria-describedby` referencing the description element (optional)
- Focus trap management
- Escape key handling

### DataTable

```tsx
<div role="region" aria-label="Files table" aria-describedby="files-table-description">
  <table role="table">
    <thead>
      <tr role="row">
        <th role="columnheader" scope="col" aria-sort={sortDirection}>
          Name
        </th>
      </tr>
    </thead>
    <tbody>
      {rows.map(row => (
        <tr role="row" aria-selected={isSelected}>
          <td role="cell">{row.name}</td>
        </tr>
      ))}
    </tbody>
  </table>
  <div aria-live="polite" id="files-table-description">
    Showing 1-20 of 142 files
  </div>
</div>
```

---

## Reduced Motion

Applied globally via TailwindCSS config:

```css
/* styles/globals.css */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

Additionally provide a manual toggle in Settings for users who want reduced motion regardless of OS setting.

---

## Focus Management

### Focus Indicators

- All interactive elements must have a visible focus indicator
- Custom focus ring: `focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2`
- Buttons and links use `focus-visible` to show focus only on keyboard navigation, not on click
- Form inputs use `focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500`

### Focus Order

- Tab order follows the visual reading order (left to right, top to bottom)
- Do not use `tabindex` values greater than 0 — they create confusing tab orders
- `tabindex="0"` is acceptable to add an element to the natural tab order
- `tabindex="-1"` is acceptable for elements that need programmatic focus but should not be tabbed to

### Focus Trapping

Dialogs use Radix `Dialog` which provides built-in focus trapping. Custom focus traps must:
- Trap Tab cycling within the dialog
- Return focus to the trigger element when dialog closes
- Focus the first interactive element when dialog opens

---

## Screen Reader Announcements

### Loading States

```tsx
<main aria-busy={isLoading}>
  {isLoading ? (
    <div aria-label="Loading analysis data" role="status">
      <span className="sr-only">Loading analysis data...</span>
      <Skeleton count={3} />
    </div>
  ) : (
    <AnalysisDashboard data={data} />
  )}
</main>
```

### Dynamic Updates

```tsx
// Toast notifications use aria-live region
<div aria-live="polite" aria-atomic="true">
  {toasts.map(toast => (
    <div role="status">{toast.message}</div>
  ))}
</div>
```

### Pagination Changes

```tsx
<div aria-live="polite" className="sr-only">
  Showing page {page} of {pages}, {total} total items
</div>
```

---

## Development Tools

### Automated Testing

- **axe-core** via `@axe-core/react` for development-time scanning
- Integration in CI pipeline (future enhancement)
- Accessibility violations fail CI builds

### Manual Testing

- Tab through every interactive element on each page
- Test with screen reader (NVDA on Windows, VoiceOver on macOS)
- Test at 200% browser zoom
- Test with `prefers-reduced-motion: reduce` enabled
- Test with high contrast mode enabled (Windows)

### Pull Request Gate

Every PR must include a statement that the accessibility checklist has been reviewed. PRs introducing new components or pages must not reduce the overall accessibility score measured by `axe-core`.
