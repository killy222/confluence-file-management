# Standards for Phase 3 Dashboard

## frontend/components

- Single Responsibility: Each component should have one clear purpose.
- Reusability: Design components to be reused with configurable props.
- Composability: Build complex UIs by combining smaller components.
- Clear Interface: Explicit, well-documented props with sensible defaults.
- Consistent Naming: Clear, descriptive names; minimal props.

## frontend/css

- Consistent Methodology: Tailwind (or chosen methodology) across the project.
- Maintain Design System: Design tokens (colors, spacing, typography).
- Minimize Custom CSS: Leverage framework utilities.

## frontend/responsive

- Mobile-First: Start with mobile layout, enhance for larger screens.
- Standard Breakpoints: Consistent breakpoints (mobile, tablet, desktop).
- Fluid Layouts: Flexible containers; relative units (rem/em).
- Touch-Friendly: Tap targets at least 44x44px.

## frontend/accessibility

- Semantic HTML: nav, main, button, etc.
- Keyboard Navigation: All interactive elements keyboard-accessible; visible focus.
- Color Contrast: Sufficient contrast; don’t rely on color alone.
- Logical Heading Structure: h1–h6 in order.
