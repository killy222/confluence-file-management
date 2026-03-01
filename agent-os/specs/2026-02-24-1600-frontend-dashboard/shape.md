# Phase 3 Frontend Dashboard — Shaping Notes

## Scope

Phase 3 Dashboard: small frontend that consumes the backend API; show run history (success/failure), list of exported files, and trigger runs. Design reference: Workflow Pro–style (dark theme, overview cards, active pipelines, cloud files).

## Decisions

- Consume existing backend API; no backend changes except CORS if needed.
- Frontend stack: React (Vite) + Tailwind CSS for dark-theme dashboard.
- Visual reference: screen.png (Overview metrics, Active Pipelines as run history, Cloud Files as exported files list).

## Context

- **Visuals:** screen.png (Workflow Pro example).
- **References:** backend API (backend/routers/, backend/schemas.py).
- **Product alignment:** roadmap Phase 3, tech-stack frontend TBD (chosen: React).

## Standards Applied

- frontend/components — reusable components, clear props.
- frontend/css — Tailwind, design tokens.
- frontend/responsive — breakpoints, fluid layout.
- frontend/accessibility — semantic HTML, keyboard, contrast.
