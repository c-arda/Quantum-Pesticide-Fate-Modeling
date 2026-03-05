---
description: Frontend design guidelines for QP-FATE dashboard — avoid generic AI aesthetics, create distinctive scientific UI
---

# Frontend Design Skill — QP-FATE

Source: [Anthropic frontend-design skill](https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md)

## Design Direction: Scientific Data Observatory

**Tone**: Refined scientific + dark observatory — like a control room for molecular simulations.
Not playful, not brutalist. Think: CERN dashboard meets Bloomberg terminal meets astronomical observatory.

**Differentiation**: The quantum circuit visualization and molecular structure overlays make this UNFORGETTABLE.

## Anti-Slop Checklist

### ❌ NEVER use these (generic AI aesthetics):
- Inter, Roboto, Arial, system fonts as primary
- Purple gradients on white backgrounds
- Predictable Bootstrap-style card layouts
- Cookie-cutter rounded-corner cards with uniform spacing
- `linear-gradient(135deg, #667eea, #764ba2)` or similar cliché gradients
- Generic emoji as section headers
- Uniform grid layouts with no hierarchy

### ✅ ALWAYS do these:

#### Typography
- **Display font**: JetBrains Mono (data/code) or IBM Plex Mono (headings)
- **Body font**: IBM Plex Sans or DM Sans (clean, scientific)
- **Accent font**: Space Mono for quantum-related labels
- Font sizes with clear hierarchy: 11px labels → 14px body → 18px subheads → 28px hero
- Letter-spacing on uppercase labels (0.08em+)

#### Color & Theme
- **Background**: Deep navy/charcoal `#0a0e1a` with subtle blue undertone
- **Surface**: Glassmorphic panels with `backdrop-filter: blur(12px)` and `rgba(255,255,255,0.04)` bg
- **Primary accent**: Cyan-teal `#00d2ff` → `#0affef` (quantum/energy)
- **Secondary accent**: Amber `#ffaa00` for warnings/important
- **Success/positive**: Emerald `#10b981`
- **Error/negative**: Coral `#f43f5e`
- **Text hierarchy**: `rgba(255,255,255,0.95)` → `0.70` → `0.45`
- **Data visualization**: Use a curated 6-color palette, not random CSS colors

#### Motion & Animation
- Page load: Staggered reveal with `animation-delay` (0, 50ms, 100ms, ...)
- Cards: `transform: translateY(20px); opacity: 0` → animate in
- Hover: Subtle glow (`box-shadow: 0 0 20px rgba(0,210,255,0.15)`)
- Numbers: Count-up animation for key metrics
- Transitions: `cubic-bezier(0.4, 0, 0.2, 1)` not linear
- Status indicators: Pulsing dot animation for live data

#### Spatial Composition
- **Asymmetric layouts**: Hero metrics large, supporting data smaller
- **Generous whitespace**: 24-32px gaps between sections
- **Visual hierarchy**: One BIG number per section, rest supports it
- **Overlap elements**: Floating badges, overlapping stat cards
- **Section dividers**: Subtle gradient lines, not `border: 1px solid`

#### Backgrounds & Visual Details
- Noise texture overlay: `background-image` with SVG noise at 2-5% opacity
- Grid pattern: Faint dot grid or line grid behind content (like graph paper)
- Glow effects: Radial gradients behind key elements
- Depth: Multiple layered shadows (`box-shadow` with 2-3 layers)
- Border: `1px solid rgba(255,255,255,0.06)` not solid colors

#### Data Visualization
- R² values: Large, color-coded (>0.5 cyan, >0.2 green, >0 amber, <0 red)
- Bar charts: Horizontal gradient bars, not plain rectangles
- Feature importance: Sorted descending with proportional bars
- Error tables: Heat-mapped cells (red→amber→green)
- Tooltips: Dark floating panels with arrow, not browser default

## Component Patterns

### Metric Card
```css
.metric-card {
  background: rgba(255,255,255,0.03);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 16px;
  padding: 24px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(0,0,0,0.3), 0 0 20px rgba(0,210,255,0.08);
  border-color: rgba(0,210,255,0.2);
}
.metric-value {
  font-family: 'JetBrains Mono', monospace;
  font-size: 32px;
  font-weight: 700;
  background: linear-gradient(135deg, #00d2ff, #0affef);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.metric-label {
  font-family: 'IBM Plex Sans', sans-serif;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: rgba(255,255,255,0.45);
  margin-top: 8px;
}
```

### Section Header
```css
.section-header {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 13px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: rgba(255,255,255,0.5);
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(255,255,255,0.06);
  display: flex;
  align-items: center;
  gap: 10px;
}
.section-header::before {
  content: '';
  width: 3px;
  height: 16px;
  background: linear-gradient(180deg, #00d2ff, transparent);
  border-radius: 2px;
}
```

### Animated Status Dot
```css
.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #10b981;
  animation: pulse 2s ease-in-out infinite;
}
@keyframes pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(16,185,129,0.4); }
  50% { box-shadow: 0 0 0 6px rgba(16,185,129,0); }
}
```
