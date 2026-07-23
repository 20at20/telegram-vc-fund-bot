# Deals Carousel Widget — Design

## Purpose
Add a widget to the front page (`AgentSelectPage`, the post-login landing screen) that showcases deals from the "Deals on the Table" feature in a rotating 3-card carousel — a dominant center card flanked by two smaller, faded side cards — so users get a glance at active deals without opening the full Deals table.

## Placement
New component: `web/src/components/DealsCarousel.tsx`.
Rendered inside `AgentSelectPage.tsx`'s right panel, which currently is an empty placeholder:

```tsx
{/* Right panel — placeholder for future content */}
<div className="flex-1 overflow-y-auto bg-gray-50 flex items-center justify-center p-10">
</div>
```

This div's children are replaced with `<DealsCarousel token={token} onLogout={onLogout} />`. `AgentSelectPage` needs `token` and `onLogout` added to its `Props` (currently only `onSelect` and `onLogout` — token isn't passed today since the page has no data needs of its own). `App.tsx`'s render call for `AgentSelectPage` is updated to pass `token`.

## Data flow
On mount, `DealsCarousel` calls `GET /api/deals` with `Authorization: Bearer <token>` — identical request to `DealsPage.tsx`. Response shape:
```json
{ "columns": string[], "rows": Record<string,string>[], "links": Record<string,string> }
```

Column detection follows the same convention already used in `DealsPage.tsx` (`columns.find(c => c.toLowerCase().includes(...))`):
- Company: `c.toLowerCase().includes('company')`
- Industry: `c.toLowerCase().includes('industry')`
- Round stage: `c.toLowerCase().includes('round') && !c.toLowerCase().includes('size')`
- Description: `c.toLowerCase().includes('descri')`

`links[companyName]` supplies the click-through URL for the center card.

If the fetch fails (non-200, network error) or returns zero rows, the component renders `null` — the right panel silently stays empty, matching today's placeholder behavior. No error banner is shown on the landing page for this non-critical widget.

## Card content & visual style
Each card shows:
- Company name — bold, larger text
- Industry tag + round-stage tag — small, uppercase, bold, tracking-widest labels in the app's blue (`#1400FF`), square corners (no `rounded-full` pills — matches the sharp, no-rounded-corners style used throughout the app, e.g. filter dropdowns, buttons)
- Description — clamped to 2–3 lines (`line-clamp-3`), consistent with the `line-clamp-2` pattern already used for tool descriptions in `AgentSelectPage`

Card container styling matches existing conventions: white background, 2px border (`border-gray-200`, no rounded corners), consistent with dropdowns/buttons elsewhere in the app.

## Carousel mechanics
- `currentIndex: number` state selects the centered deal.
- Three slots rendered per tick: `deals[(currentIndex - 1 + n) % n]`, `deals[currentIndex]`, `deals[(currentIndex + 1) % n]` where `n = deals.length`. Modulo wrap makes the carousel loop infinitely in both directions.
- Center slot: full scale (`scale-100`), full opacity, higher `z-index`.
- Side slots: reduced scale (`scale-90`ish), reduced opacity (~50%), positioned left/right of center.
- All position/scale/opacity changes animate via CSS `transition` (transform + opacity) — no animation library.
- **Manual navigation:** left/right chevron buttons move `currentIndex` ±1 (mod `n`). Clicking a visible side card also moves `currentIndex` to that card's index (same effect as clicking the corresponding arrow, since only immediate neighbors are visible).
- **Auto-scroll:** a `setInterval` advances `currentIndex` by +1 every 10,000ms. On mouse-enter of the carousel container, the interval is cleared; on mouse-leave, it's restarted (with a fresh 10s window) — so hovering to read a card doesn't cause it to jump away.
- **Center card click:** if `links[companyName]` exists, `window.open(url, '_blank', 'noopener,noreferrer')`. If no link, click does nothing and the cursor is `default` rather than `pointer` (no dead-click affordance).

## Edge cases
| Deals count | Behavior |
|---|---|
| 0 | Component renders `null` |
| 1 | Only center card renders; no arrows, no auto-scroll interval (nothing to rotate to) |
| 2 | Left and right slots both resolve to the same "other" deal (mod-2 wrap) — visually two identical side cards, still functions correctly |
| 3+ | Normal operation as described above |

## Out of scope
- No changes to the `/api/deals` backend endpoint — reuses it as-is.
- No changes to `DealsPage.tsx` itself.
- No drag/swipe gesture support (arrows + side-card clicks only, per approved design).
- No new npm dependencies.
