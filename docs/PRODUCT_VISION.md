# Product Vision

> **Document Owner:** Frontend Architecture
> **Status:** Living Document
> **Last Updated:** 2026-07-27

---

## Purpose

Legacy2Next is an AI-assisted legacy software intelligence and modernization platform. It helps development teams understand, analyse, and plan the migration of legacy codebases by combining static analysis with contextual AI insights.

This document defines what the product is, who it serves, and the principles that guide every design and engineering decision.

---

## Taxonomy

| Term | Definition |
|---|---|
| **Analysis** | A static examination of an uploaded codebase — detects files, languages, technologies, dependencies, metrics, and warnings. |
| **AI Insight** | A contextual, generative explanation of analysis results — summaries, architecture descriptions, technical debt assessments, and modernisation recommendations. |
| **Project** | A container for uploads and their resulting analyses. Represents a single legacy codebase under evaluation. |
| **Upload** | A batch of source files (typically a zip archive) submitted for analysis. |
| **User** | A developer or technical lead evaluating a legacy codebase. |

---

## Target Users

### Primary: The Technical Lead

A senior engineer evaluating a legacy system before a modernisation initiative. They need:

- A bird's-eye view of the codebase's composition (languages, size, structure)
- Automated detection of technologies and frameworks in use
- Dependency mapping to understand coupling and risk
- AI-generated summaries they can include in stakeholder reports

### Secondary: The Contributing Developer

A team member who needs to understand specific parts of the legacy system. They need:

- File-by-file exploration with language-aware context
- AI-powered explanations of unfamiliar code
- Warning and metric drill-down for focused areas

### Tertiary: The Engineering Manager

Oversees modernisation budgets and timelines. They need:

- High-level dashboards comparing multiple projects
- Technical debt quantification
- Modernisation effort estimates

---

## Product Identity

Legacy2Next occupies a specific intersection in the developer tools landscape:

| Inspiration | What We Take | What We Reject |
|---|---|---|
| **Linear** | Clean hierarchy, reduced chrome, keyboard-first navigation | Feature minimalism — our dashboards are data-dense by necessity |
| **GitHub** | Familiar developer UX, consistent patterns, predictable interactions | Visual complexity of legacy GitHub UI |
| **Vercel** | Polished typography, generous whitespace, refined component interactions | Marketing-heavy visual language |
| **SonarQube** | Information-dense dashboards, colour-coded quality gates, drill-down patterns | Dated visual design, cluttered layouts |

The resulting identity is: **a developer tool that respects your attention**. Information-dense but never overwhelming, polished but never decorative, AI-augmented but never magical.

### Visual Identity Statement

> Legacy2Next presents itself as a precision instrument: dark, focused, and responsive to expert use. Every visual element earns its place through utility. Colour communicates status, not decoration. Typography prioritises readability at small sizes. Motion serves comprehension, not delight.

---

## Core Experience Principles

### 1. Analysis First

The dashboard is the centre of the product. Every feature either feeds data into analysis results or helps users understand those results. The analysis dashboard is the default destination after any upload completes.

### 2. AI Is Contextual, Not a Destination

AI insights live alongside the data they explain — on the same page, in the same tab structure. There are no separate "AI" pages. The user triggers an AI insight from within the relevant analysis section, and the result appears in place.

### 3. Progressive Disclosure

Start with summary-level insight. Let users drill into details through interaction (clicks, expand, hover). Never show everything at once — reveal complexity on demand.

### 4. Predictable Navigation

Every page follows the same structural pattern: header → navigation tabs → content area. Users should never wonder where to find a feature. The sidebar shows current location; breadcrumbs show hierarchy.

### 5. Dark Mode Primary

The application is designed for dark-first usage — developers working in IDE-like environments. Light mode is a secondary consideration, supported for accessibility and preference but not the primary design target.

---

## Non-Goals

- Not a code editor — no syntax highlighting with editing capability
- Not a CI/CD pipeline — analysis is user-triggered, not automated
- Not a collaboration platform — no real-time multi-user features in MVP
- Not a general-purpose AI chat — AI is constrained to analysis context
- Not a mobile app — the interface is desktop-first, tablet-tolerant

---

## Future Evolution

As the product matures, additional modules will be introduced:

- **Reports** — exportable PDF/HTML summaries for stakeholders
- **Modernisation Planning** — phased migration roadmaps with effort estimates
- **Documentation Generation** — auto-generated technical documentation from analysis
- **Multi-Project Comparison** — side-by-side dashboards across projects

The architecture described in the design system documents is built to accommodate these additions without structural changes.

---

## Relationship to Design Documents

| Document | What It Defines |
|---|---|
| `design/FRONTEND_PRINCIPLES.md` | Engineering and design decision-making framework |
| `design/DESIGN_SYSTEM.md` | Component architecture, naming conventions, file organisation |
| `design/DESIGN_TOKENS.md` | Colour, typography, spacing, and breakpoint values |
| `design/LAYOUT_GUIDELINES.md` | Page structure, grid, sidebar, and responsive behaviour |
| `design/COMPONENT_GUIDELINES.md` | Shared UI component API contracts and usage rules |
| `design/MOTION_GUIDELINES.md` | Animation principles, duration, easing, and accessibility |
| `design/ICONOGRAPHY.md` | Icon usage, sizing, and selection rules |
| `design/ACCESSIBILITY.md` | WCAG 2.1 AA compliance requirements and testing |
