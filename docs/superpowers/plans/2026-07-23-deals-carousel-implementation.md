# Deals Carousel Widget Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a rotating 3-card deals carousel (center dominant, side cards faded) to the empty right panel of the front-page `AgentSelectPage`, sourced from the existing `/api/deals` endpoint.

**Architecture:** A single new component `DealsCarousel.tsx` fetches deals data the same way `DealsPage.tsx` does, then renders a fixed set of visible "slots" (center + up to one on each side) computed from each deal's circular distance from the currently centered index. Position/scale/opacity are driven by inline styles with a CSS `transition`, so moving `currentIndex` (via arrows, side-card click, or the 10s auto-scroll timer) animates smoothly. No animation library — matches the hand-rolled CSS approach already used by `PortfolioTicker.tsx`.

**Tech Stack:** React 18 + TypeScript, Tailwind CSS, Vite. No new dependencies.

## Global Constraints

- No new npm dependencies — hand-rolled CSS/React only (per approved design).
- Reuse `GET /api/deals` exactly as-is; no backend changes; no changes to `DealsPage.tsx`.
- Visual language must match the existing app: brand blue `#1400FF`, 2px borders, sharp corners (no `rounded-full`), uppercase `tracking-widest` labels, `'Space Grotesk'` font for headings — same conventions used in `AgentSelectPage.tsx` and `DealsPage.tsx`.
- Widget renders `null` on fetch failure or zero deals — no error banner on the landing page.
- Auto-scroll advances one deal every 10,000ms; pauses on mouse-enter, resumes (fresh 10s window) on mouse-leave.
- Center card click opens `links[company]` in a new tab if present; otherwise no-op with a default (not pointer) cursor.
- Clicking a visible side card, or an arrow button, recenters the carousel to that neighbor.
- Edge cases: 0 deals → render nothing; 1 deal → center only, no arrows/timer; 2 deals → both side slots show the single "other" deal; 3+ deals → normal circular behavior.
- This project has no frontend test runner installed (`web/package.json` has no `vitest`/`jest`/testing-library, and there are zero `*.test.*` files anywhere in `web/`). Adding one would violate the "no new dependencies" constraint and deviate from how every other page in this app is verified. Each task below is verified with `npx tsc --noEmit` (type safety) plus a manual browser check via the Vite dev server, consistent with how the rest of this codebase is validated.

---

## Task 1: Data layer + plumbing

**Files:**
- Create: `web/src/components/DealsCarousel.tsx`
- Modify: `web/src/pages/AgentSelectPage.tsx`
- Modify: `web/src/App.tsx`

**Interfaces:**
- Produces: `DealsCarousel` component with props `{ token: string; onLogout: () => void }`, default export.
- Produces: internal `Deal` type `{ company: string; industry: string; round: string; description: string; link: string }` (not exported — later tasks add to this same file).

- [ ] **Step 1: Create `DealsCarousel.tsx` with data fetching and a plain (unstyled) render**

Create `web/src/components/DealsCarousel.tsx`:

```tsx
import { useEffect, useState } from 'react'

const API = import.meta.env.VITE_API_URL || ''

interface Props {
  token: string
  onLogout: () => void
}

interface Deal {
  company: string
  industry: string
  round: string
  description: string
  link: string
}

export default function DealsCarousel({ token, onLogout }: Props) {
  const [deals, setDeals] = useState<Deal[]>([])
  const [loading, setLoading] = useState(true)
  const [currentIndex, setCurrentIndex] = useState(0)

  useEffect(() => {
    const fetchDeals = async () => {
      try {
        const res = await fetch(`${API}/api/deals`, {
          headers: { Authorization: `Bearer ${token}` },
        })
        if (res.status === 401) {
          onLogout()
          return
        }
        const data = await res.json()
        const columns: string[] = data.columns || []
        const rows: Record<string, string>[] = data.rows || []
        const links: Record<string, string> = data.links || {}

        const companyCol = columns.find(c => c.toLowerCase().includes('company')) || ''
        const industryCol = columns.find(c => c.toLowerCase().includes('industry')) || ''
        const roundCol = columns.find(c => c.toLowerCase().includes('round') && !c.toLowerCase().includes('size')) || ''
        const descCol = columns.find(c => c.toLowerCase().includes('descri')) || ''

        const parsed: Deal[] = rows
          .map(row => {
            const company = (row[companyCol] || '').trim()
            return {
              company,
              industry: (row[industryCol] || '').trim(),
              round: (row[roundCol] || '').trim(),
              description: (row[descCol] || '').trim(),
              link: links[company] || '',
            }
          })
          .filter(d => d.company)

        setDeals(parsed)
      } catch {
        setDeals([])
      } finally {
        setLoading(false)
      }
    }
    fetchDeals()
  }, [token, onLogout])

  const n = deals.length

  if (loading || n === 0) return null

  // Temporary plain render — replaced with the real 3-slot carousel in Task 2.
  return (
    <div>
      <p>{deals[currentIndex]?.company}</p>
    </div>
  )
}
```

- [ ] **Step 2: Type-check**

Run from `web/`: `npx tsc --noEmit`
Expected: no errors.

- [ ] **Step 3: Plumb `token` into `AgentSelectPage` and render the carousel**

In `web/src/pages/AgentSelectPage.tsx`, update the import block and `Props`:

```tsx
import PortfolioTicker from '../components/PortfolioTicker'
import DealsCarousel from '../components/DealsCarousel'
```

```tsx
interface Props {
  token: string
  onSelect: (agentId: string) => void
  onLogout: () => void
}

export default function AgentSelectPage({ token, onSelect, onLogout }: Props) {
```

Replace the empty right panel:

```tsx
{/* Right panel — placeholder for future content */}
<div className="flex-1 overflow-y-auto bg-gray-50 flex items-center justify-center p-10">
</div>
```

with:

```tsx
{/* Right panel — deals carousel */}
<div className="flex-1 overflow-y-auto bg-gray-50 flex items-center justify-center p-10">
  <DealsCarousel token={token} onLogout={onLogout} />
</div>
```

- [ ] **Step 4: Pass `token` from `App.tsx`**

In `web/src/App.tsx`, update the `AgentSelectPage` render call:

```tsx
if (!selectedAgent) return <AgentSelectPage token={token} onSelect={handleSelectAgent} onLogout={handleLogout} />
```

- [ ] **Step 5: Type-check and manual verification**

Run from `web/`: `npx tsc --noEmit`
Expected: no errors.

Then start the dev server pointed at the deployed backend (no local backend needed):
```bash
cd web && VITE_API_URL=https://telegram-vc-fund-bot-production.up.railway.app npm run dev
```
Open the printed local URL, log in, and confirm the landing page's right panel now shows the first deal's company name as plain text (no styling yet). Stop the dev server (Ctrl+C) when confirmed.

- [ ] **Step 6: Commit**

```bash
git add web/src/components/DealsCarousel.tsx web/src/pages/AgentSelectPage.tsx web/src/App.tsx
git commit -m "feat: wire up deals data fetch into front-page carousel skeleton"
```

---

## Task 2: 3-slot carousel layout and card styling

**Files:**
- Modify: `web/src/components/DealsCarousel.tsx`

**Interfaces:**
- Consumes: `Deal` type and `deals`/`currentIndex` state from Task 1.
- Produces: a `slots: { idx: number; d: number; key: string }[]` array computed each render (used by Task 3's click handlers, which need `idx` and `d` to tell center from side slots).

- [ ] **Step 1: Replace the temporary render with the full 3-slot carousel**

Replace the entire return statement and add the slot-computation logic. The full updated `DealsCarousel.tsx`:

```tsx
import { useEffect, useState } from 'react'

const API = import.meta.env.VITE_API_URL || ''

interface Props {
  token: string
  onLogout: () => void
}

interface Deal {
  company: string
  industry: string
  round: string
  description: string
  link: string
}

const CARD_SPACING = 240 // px offset for side slots relative to center

export default function DealsCarousel({ token, onLogout }: Props) {
  const [deals, setDeals] = useState<Deal[]>([])
  const [loading, setLoading] = useState(true)
  const [currentIndex, setCurrentIndex] = useState(0)

  useEffect(() => {
    const fetchDeals = async () => {
      try {
        const res = await fetch(`${API}/api/deals`, {
          headers: { Authorization: `Bearer ${token}` },
        })
        if (res.status === 401) {
          onLogout()
          return
        }
        const data = await res.json()
        const columns: string[] = data.columns || []
        const rows: Record<string, string>[] = data.rows || []
        const links: Record<string, string> = data.links || {}

        const companyCol = columns.find(c => c.toLowerCase().includes('company')) || ''
        const industryCol = columns.find(c => c.toLowerCase().includes('industry')) || ''
        const roundCol = columns.find(c => c.toLowerCase().includes('round') && !c.toLowerCase().includes('size')) || ''
        const descCol = columns.find(c => c.toLowerCase().includes('descri')) || ''

        const parsed: Deal[] = rows
          .map(row => {
            const company = (row[companyCol] || '').trim()
            return {
              company,
              industry: (row[industryCol] || '').trim(),
              round: (row[roundCol] || '').trim(),
              description: (row[descCol] || '').trim(),
              link: links[company] || '',
            }
          })
          .filter(d => d.company)

        setDeals(parsed)
      } catch {
        setDeals([])
      } finally {
        setLoading(false)
      }
    }
    fetchDeals()
  }, [token, onLogout])

  const n = deals.length

  const circularDistance = (idx: number) => {
    let d = idx - currentIndex
    if (d > n / 2) d -= n
    if (d < -n / 2) d += n
    return d
  }

  if (loading || n === 0) return null

  // Which deals are visible this render, and at what offset from center (d).
  // n === 2 is special-cased: both side slots show the single "other" deal
  // (there's no well-defined left vs. right for a 2-item circular list).
  type Slot = { idx: number; d: number; key: string }
  const slots: Slot[] = []
  if (n === 1) {
    slots.push({ idx: 0, d: 0, key: 'center' })
  } else if (n === 2) {
    const otherIdx = (currentIndex + 1) % 2
    slots.push({ idx: otherIdx, d: -1, key: 'left' })
    slots.push({ idx: currentIndex, d: 0, key: 'center' })
    slots.push({ idx: otherIdx, d: 1, key: 'right' })
  } else {
    for (let idx = 0; idx < n; idx++) {
      const d = circularDistance(idx)
      if (Math.abs(d) <= 1) {
        slots.push({ idx, d, key: `slot-${idx}` })
      }
    }
  }

  return (
    <div className="relative w-full max-w-2xl mx-auto">
      <div className="relative h-64">
        {slots.map(({ idx, d, key }) => {
          const deal = deals[idx]
          const isCenter = d === 0
          return (
            <div
              key={key}
              style={{
                transform: `translate(calc(-50% + ${d * CARD_SPACING}px), -50%) scale(${isCenter ? 1 : 0.85})`,
                opacity: isCenter ? 1 : 0.5,
                zIndex: isCenter ? 20 : 10,
              }}
              className={`
                absolute top-1/2 left-1/2 w-64 border-2 border-gray-200 bg-white p-5
                transition-all duration-500 ease-out
              `}
            >
              <div className="flex flex-wrap gap-2 mb-3">
                {deal.industry && (
                  <span className="text-[10px] font-bold uppercase tracking-widest text-[#1400FF]">
                    {deal.industry}
                  </span>
                )}
                {deal.round && (
                  <span className="text-[10px] font-bold uppercase tracking-widest text-gray-400">
                    {deal.round}
                  </span>
                )}
              </div>
              <div
                style={{ fontFamily: "'Space Grotesk', sans-serif" }}
                className="font-black text-lg text-gray-900 mb-2"
              >
                {deal.company}
              </div>
              {deal.description && (
                <p className="text-xs text-gray-500 leading-snug line-clamp-3">
                  {deal.description}
                </p>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Type-check**

Run from `web/`: `npx tsc --noEmit`
Expected: no errors.

- [ ] **Step 3: Manual verification**

```bash
cd web && VITE_API_URL=https://telegram-vc-fund-bot-production.up.railway.app npm run dev
```
Log in, confirm the right panel shows a styled center card (industry/round tags, bold company name, clamped description) with two smaller, faded side cards peeking in from left/right. Stop the dev server when confirmed.

- [ ] **Step 4: Commit**

```bash
git add web/src/components/DealsCarousel.tsx
git commit -m "feat: render styled 3-slot deals carousel layout"
```

---

## Task 3: Manual navigation and center-card link click

**Files:**
- Modify: `web/src/components/DealsCarousel.tsx`

**Interfaces:**
- Consumes: `slots` array and `setCurrentIndex` from Task 2.
- Produces: `goPrev`, `goNext`, `handleCenterClick` handlers (referenced again in Task 4, which only adds the auto-scroll interval and does not change these).

- [ ] **Step 1: Add click handlers and wire them into the slot rendering + arrow buttons**

In `web/src/components/DealsCarousel.tsx`, add these handlers just after the `circularDistance` function (still inside the component, before the `if (loading || n === 0) return null` line):

```tsx
  const goPrev = () => setCurrentIndex(i => (i - 1 + n) % n)
  const goNext = () => setCurrentIndex(i => (i + 1) % n)

  const handleCenterClick = () => {
    const link = deals[currentIndex]?.link
    if (link) window.open(link, '_blank', 'noopener,noreferrer')
  }
```

Update the card `<div>` inside `slots.map` to add the click handler and cursor styling. Replace:

```tsx
            <div
              key={key}
              style={{
                transform: `translate(calc(-50% + ${d * CARD_SPACING}px), -50%) scale(${isCenter ? 1 : 0.85})`,
                opacity: isCenter ? 1 : 0.5,
                zIndex: isCenter ? 20 : 10,
              }}
              className={`
                absolute top-1/2 left-1/2 w-64 border-2 border-gray-200 bg-white p-5
                transition-all duration-500 ease-out
              `}
            >
```

with:

```tsx
            <div
              key={key}
              onClick={isCenter ? handleCenterClick : () => setCurrentIndex(idx)}
              style={{
                transform: `translate(calc(-50% + ${d * CARD_SPACING}px), -50%) scale(${isCenter ? 1 : 0.85})`,
                opacity: isCenter ? 1 : 0.5,
                zIndex: isCenter ? 20 : 10,
              }}
              className={`
                absolute top-1/2 left-1/2 w-64 border-2 border-gray-200 bg-white p-5
                transition-all duration-500 ease-out
                ${isCenter
                  ? deal.link ? 'cursor-pointer hover:border-[#1400FF]' : 'cursor-default'
                  : 'cursor-pointer'}
              `}
            >
```

Then add arrow buttons below the slots container. Replace the closing of the outer wrapper:

```tsx
      </div>
    </div>
  )
}
```

with:

```tsx
      </div>

      {n > 1 && (
        <div className="flex items-center justify-center gap-8 mt-4">
          <button
            onClick={goPrev}
            aria-label="Previous deal"
            className="text-gray-400 hover:text-[#1400FF] transition-colors"
          >
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <button
            onClick={goNext}
            aria-label="Next deal"
            className="text-gray-400 hover:text-[#1400FF] transition-colors"
          >
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 2: Type-check**

Run from `web/`: `npx tsc --noEmit`
Expected: no errors.

- [ ] **Step 3: Manual verification**

```bash
cd web && VITE_API_URL=https://telegram-vc-fund-bot-production.up.railway.app npm run dev
```
Log in and confirm:
- Clicking the right arrow moves the next deal to center; left arrow moves the previous one back.
- Clicking a visible side card recenters the carousel to that deal.
- Clicking the center card opens the company's link in a new tab (for a deal that has one); for a deal with no link, clicking does nothing and the cursor is the default arrow, not a pointer.

Stop the dev server when confirmed.

- [ ] **Step 4: Commit**

```bash
git add web/src/components/DealsCarousel.tsx
git commit -m "feat: add manual navigation and center-card link click to deals carousel"
```

---

## Task 4: Auto-scroll timer with hover pause, and final QA

**Files:**
- Modify: `web/src/components/DealsCarousel.tsx`

**Interfaces:**
- Consumes: `deals.length`, `setCurrentIndex` from earlier tasks.
- Produces: none consumed further — this is the last task.

- [ ] **Step 1: Add hover state and the auto-scroll interval**

In `web/src/components/DealsCarousel.tsx`, add a `hovered` state next to the existing `currentIndex` state:

```tsx
  const [currentIndex, setCurrentIndex] = useState(0)
  const [hovered, setHovered] = useState(false)
```

Add the auto-scroll effect directly below the data-fetching `useEffect` (after its closing `}, [token, onLogout])`):

```tsx
  useEffect(() => {
    if (deals.length < 2 || hovered) return
    const id = setInterval(() => {
      setCurrentIndex(i => (i + 1) % deals.length)
    }, 10000)
    return () => clearInterval(id)
  }, [deals.length, hovered])
```

Wire the hover handlers onto the outer container. Replace:

```tsx
  return (
    <div className="relative w-full max-w-2xl mx-auto">
```

with:

```tsx
  return (
    <div
      className="relative w-full max-w-2xl mx-auto"
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
```

- [ ] **Step 2: Type-check**

Run from `web/`: `npx tsc --noEmit`
Expected: no errors.

- [ ] **Step 3: Manual verification — full behavior + edge cases**

```bash
cd web && VITE_API_URL=https://telegram-vc-fund-bot-production.up.railway.app npm run dev
```
Log in and verify, with the real deals sheet data (3+ rows expected in production):
- Leaving the carousel untouched for ~10s advances it to the next deal automatically, looping back to the first deal after the last.
- Hovering the carousel pauses the auto-scroll; moving the mouse away resumes it (waits a fresh 10s, doesn't immediately jump).
- All Task 3 interactions (arrows, side-card click, center-card link click) still work.

If feasible, also drive this same check with the Playwright MCP browser tools (`browser_navigate` to the local dev URL, `browser_snapshot` to confirm the three cards render, `browser_click` on an arrow and a side card, then wait ~10s and re-snapshot to confirm auto-advance) as a second confirmation pass.

To confirm the edge cases from the design spec (0 / 1 / 2 deals), temporarily hardcode a shorter `parsed` array in the fetch handler (e.g. `.slice(0, 1)` or `.slice(0, 2)`) as a scratch change, reload the page, observe the behavior described below, then revert the scratch change before committing:
- 0 deals → right panel is empty (nothing rendered).
- 1 deal → only the center card shows, no arrows, no movement over time.
- 2 deals → both side slots show the same single "other" deal; arrows/side-clicks swap it with the center deal.

Stop the dev server when confirmed.

- [ ] **Step 4: Commit**

```bash
git add web/src/components/DealsCarousel.tsx
git commit -m "feat: add 10s auto-scroll with hover pause to deals carousel"
```
