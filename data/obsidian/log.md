# Wiki Log

Append-only record of all wiki activity. Most recent entries at top.
Format: `## [YYYY-MM-DD] <type> | <title>`
Types: `ingest`, `query`, `lint`, `update`, `create`

Parse recent entries: `grep "^## \[" wiki/log.md | head -10`

---

## [2026-04-05] ingest | Offering Memorandum (June 2024) + M&A Agreement (Nov 2023)

Legal docs only — short source pages created, no entity pages touched.
OM confirms: Cyprus RAIF entity (HE453103), CySEC RAIF170, AIFM SCSS Fund Management, EUR-denominated, min €125K for well-informed investors.
M&A doc: scanned PDF, text not extractable — content unknown, flagged for manual review.

## [2026-04-05] ingest | Roosh Ventures Fund II Fundraising Deck (Mar 2025)

Source: `raw/assets/Roosh Ventures_Fundraising Deck_Mar.pdf` (37 slides). Primary fund document.
Pages created: source summary, 4 people pages (Tokarev, Ukho, Hashchyshyn, Tymovskyi), 6 company pages (ElevenLabs, Alter, Rollstack, Kobalt Labs, Tower.dev, Movable Voice), 2 concept pages (Application AI thesis, Investment thesis), 2 fund pages (Sequoia, a16z). Overview and index fully populated.
Key facts locked in: Fund II €50M, 25%+ IRR target, GP €15M commit; Fund I 1.75x TVPI / 20% IRR; ElevenLabs 836.4x unrealized; Alter exited to Google $100M.
2 more PDFs pending (M&A doc 2023, Offering Memorandum 2024) — awaiting poppler install.

## [2026-04-05] create | Wiki initialized

Roosh Ventures wiki created from scratch. Directory structure established. CLAUDE.md schema written. index.md and log.md initialized. overview.md stub created. No sources ingested yet. Ready for first ingest.
