# Legacy2Next Design System

> **Document Owner:** Frontend Architecture
> **Status:** Living Document
> **Last Updated:** 2026-07-27

This directory contains the complete design system documentation for the Legacy2Next frontend. Every document is a long-term architectural reference that governs how the UI looks, behaves, and is built.

---

## Document Map

```
docs/
├── PRODUCT_VISION.md              ← Product identity, users, and experience principles
└── design/
    ├── README.md                   ← This file — overview and cross-reference
    ├── FRONTEND_PRINCIPLES.md      ← Engineering and design decision-making framework
    ├── DESIGN_SYSTEM.md            ← Component architecture, naming, file organisation
    ├── DESIGN_TOKENS.md            ← Colour, typography, spacing, breakpoint values
    ├── LAYOUT_GUIDELINES.md        ← Page structure, grid, sidebar, responsive behaviour
    ├── COMPONENT_GUIDELINES.md     ← UI component API contracts and usage rules
    ├── MOTION_GUIDELINES.md        ← Animation principles, duration, easing, accessibility
    ├── ICONOGRAPHY.md              ← Icon usage, sizing, selection rules
    └── ACCESSIBILITY.md            ← WCAG 2.1 AA compliance requirements and testing
```

---

## How to Use These Documents

### When building a new feature

1. Read `FRONTEND_PRINCIPLES.md` — confirm the feature aligns with engineering values
2. Read `COMPONENT_GUIDELINES.md` — check if a shared component already exists
3. Reference `DESIGN_TOKENS.md` — use correct colour, spacing, and type tokens
4. Reference `LAYOUT_GUIDELINES.md` — follow page structure and grid conventions
5. Read `MOTION_GUIDELINES.md` — add transitions that respect the motion system
6. Read `ACCESSIBILITY.md` — verify the implementation meets WCAG AA

### When creating a new component

1. Read `DESIGN_SYSTEM.md` — understand component hierarchy and naming conventions
2. Read `COMPONENT_GUIDELINES.md` — follow the API contract patterns
3. Read `ICONOGRAPHY.md` — use icons correctly if needed
4. Check `DESIGN_TOKENS.md` — apply correct tokens

### When reviewing a pull request

1. Verify the implementation matches `DESIGN_TOKENS.md` values
2. Verify component API matches `COMPONENT_GUIDELINES.md` contracts
3. Verify motion follows `MOTION_GUIDELINES.md` durations and easings
4. Verify accessibility against `ACCESSIBILITY.md` checklist

---

## Design Influences

| Source | Influence |
|---|---|
| **Linear** | Clean hierarchy, reduced chrome, keyboard-first navigation |
| **GitHub** | Familiar developer UX, consistent patterns, predictable interactions |
| **Vercel** | Polished typography, generous whitespace, refined component interaction |
| **SonarQube** | Information-dense dashboards, colour-coded quality gates, drill-down patterns |

The complete identity is defined in `PRODUCT_VISION.md`.

---

## Key Design Decisions

| Decision | Rationale |
|---|---|
| Dark mode is primary | Developers work in IDE-like environments; dark UI reduces eye strain during extended sessions |
| AI lives in context panels, not separate pages | Users understand analysis results better when AI insight is presented alongside the relevant data |
| Information density over whitespace | The product is a data analysis tool; users need to see multiple metrics simultaneously |
| No external component library | Radix UI primitives + custom Tailwind components keep the bundle small (~80KB less than MUI) and give full design control |
| CSS variables for runtime theme switching | Users can toggle dark/light mode without a full page reload |

---

## Quick Reference

| Resource | Contents |
|---|---|
| Colour tokens | `DESIGN_TOKENS.md` — §Colour |
| Type scale | `DESIGN_TOKENS.md` — §Typography |
| Spacing scale | `DESIGN_TOKENS.md` — §Spacing |
| Breakpoints | `DESIGN_TOKENS.md` — §Breakpoints |
| Page grid | `LAYOUT_GUIDELINES.md` — §Grid System |
| Component API | `COMPONENT_GUIDELINES.md` — §Component Reference |
| Motion durations | `MOTION_GUIDELINES.md` — §Durations and Easing |
| Accessibility checklist | `ACCESSIBILITY.md` — §Testing Checklist |
