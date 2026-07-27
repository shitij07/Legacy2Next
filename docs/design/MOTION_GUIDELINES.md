# Motion Guidelines

> **Document Owner:** Frontend Architecture
> **Status:** Living Document
> **Last Updated:** 2026-07-27

---

## Motion Philosophy

> Motion serves comprehension, not delight.

Every animation in Legacy2Next must justify itself by answering one of these questions:

1. **Where did this come from?** — Elements animate from their origin (e.g., a modal scales up from the button that triggered it).
2. **Where did it go?** — Elements animate toward their destination (e.g., a deleted item fades and collapses out of a list).
3. **What changed?** — State transitions use motion to guide the eye (e.g., a stat card value animates to its new number).

If an animation does not answer one of these questions, remove it.

---

## Design Principles

### 1. Quick and Responsive

All animations complete within 150-300ms. Users should never wait for an animation to finish before interacting.

| Context | Duration | Justification |
|---|---|---|
| Micro-interactions (hover, click) | 100-150ms | Feels instantaneous |
| UI transitions (open/close, show/hide) | 150-200ms | Fast enough to feel responsive |
| Page transitions | 200-300ms | Provides continuity without delay |
| Loading animations | 1000-1500ms (loop) | Indicates progress without urgency |

### 2. Subtle and Purposeful

- Opacity and transform only. Avoid animating `width`, `height`, `top`, `left`, or `margin` — these trigger layout recalculations and cause jank.
- Use `opacity` for fades and `transform: scale/translateY` for movements.
- Maximum 2 properties animated simultaneously.

### 3. Consistent Easing

Use a single easing curve for all animations to create a cohesive feel.

```css
--ease-default: cubic-bezier(0.16, 1, 0.3, 1);
```

This is an **emphasized ease-out** curve. It starts quickly (decelerating) for responsive feel, then settles gently. It is inspired by Vercel's motion system and Linear's interaction design.

### 4. Respect Reduced Motion

Users who prefer reduced motion must have a fully functional experience with all animations disabled.

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

Apply this globally. No exceptions.

---

## Animation Patterns

### 1. Fade In

Use for elements that appear without a spatial origin (toasts, notifications, overlay text).

```css
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.fade-in {
  animation: fadeIn 150ms var(--ease-default);
}
```

### 2. Scale In

Use for elements that originate from a point (dialogs, popovers, menus).

```css
@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.scale-in {
  animation: scaleIn 200ms var(--ease-default);
}
```

### 3. Slide In (Up)

Use for elements that enter from below (drawers, sheets, bottom panels).

```css
@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.slide-up {
  animation: slideUp 200ms var(--ease-default);
}
```

### 4. Slide In (Right)

Use for sidebar drawer on mobile.

```css
@keyframes slideRight {
  from {
    transform: translateX(-100%);
  }
  to {
    transform: translateX(0);
  }
}
```

### 5. Stagger Children

Use for lists appearing on initial page load. Each child animates with a 30ms delay.

```css
.stagger-children > * {
  opacity: 0;
  animation: slideUp 200ms var(--ease-default) forwards;
}

.stagger-children > *:nth-child(1) { animation-delay: 0ms; }
.stagger-children > *:nth-child(2) { animation-delay: 30ms; }
.stagger-children > *:nth-child(3) { animation-delay: 60ms; }
/* ... continue with +30ms increments */
```

Stagger maximum: 5 children. Beyond that, groups should animate together.

### 6. Number Count-Up

Use for stat cards and metric values when they first mount.

```css
@keyframes countUp {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}

.stat-value {
  animation: countUp 300ms var(--ease-default);
}
```

The value transition itself should be a number animation (incrementing from 0 to final value over ~400ms).

### 7. Skeleton Pulse

Use for loading placeholders.

```css
@keyframes pulse {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 0.7; }
}

.skeleton {
  animation: pulse 1.5s ease-in-out infinite;
}
```

---

## Component-Specific Animations

| Component | Animation | Duration | Notes |
|---|---|---|---|
| Button hover | Background colour transition | 100ms | Use `transition-colors` |
| Button active (click) | Scale 0.97 → 1 | 100ms | Subtle press effect |
| Dialog open | Backdrop fade + content scale-in | 200ms | Backdrop fades first (100ms) |
| Dialog close | Scale-out + backdrop fade | 150ms | Reverse of open |
| Dropdown menu open | Scale-in from origin | 150ms | Originates from trigger |
| Dropdown menu close | Fade-out | 100ms | Quick dismissal |
| Tab underline | Translate X | 150ms | Smooth indicator movement |
| Toast appear | Slide-in from top-right | 200ms | Stacks downward |
| Toast dismiss | Slide-out to right + fade | 200ms | |
| Sidebar toggle (desktop) | Translate X | 200ms | Width change: 240px ↔ 0 |
| Sidebar drawer (mobile) | Slide right (overlay) | 250ms | With backdrop fade |
| Table row hover | Background colour | 100ms | `transition-colors` |
| Table sort indicator | Rotate 180° | 150ms | Sort arrow icon |
| Page transition | Fade in content | 200ms | Between tab changes |
| Row enter (list) | Slide-up + fade | 150ms | New items appearing |
| Row exit (list) | Slide-left + fade | 150ms | Deleted items |

---

## Transition Utility Classes

```css
/* TailwindCSS compatible transition classes */
.transition-fast {
  transition-duration: 100ms;
  transition-timing-function: var(--ease-default);
}

.transition-normal {
  transition-duration: 200ms;
  transition-timing-function: var(--ease-default);
}

.transition-slow {
  transition-duration: 300ms;
  transition-timing-function: var(--ease-default);
}
```

---

## Framer Motion Usage (If Adopted)

If Framer Motion is introduced for complex animations (drag, layout animations, shared element transitions):

```typescript
// Layout animation for tab content
<motion.div
  layout
  initial={{ opacity: 0, y: 8 }}
  animate={{ opacity: 1, y: 0 }}
  exit={{ opacity: 0, y: -8 }}
  transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
>
```

Keep Framer Motion usage limited. Most animations can be achieved with CSS transitions and keyframes. Reserve Framer Motion for:

- `AnimatePresence` for exit animations
- `layout` animations for list reordering
- Shared element transitions (future enhancement)

---

## Motion Checklist

Before adding an animation, verify:

- [ ] Does it answer "where did this come from / go / what changed?"
- [ ] Is the duration between 100-300ms?
- [ ] Does it use only `opacity` and `transform` properties?
- [ ] Does it use the standard easing curve?
- [ ] Does it work with `prefers-reduced-motion: reduce`?
- [ ] Does it affect usability if it fails to render? (If yes, reconsider.)
