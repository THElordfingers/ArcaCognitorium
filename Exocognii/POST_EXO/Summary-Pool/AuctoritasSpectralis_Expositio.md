# Auctoritas Spectralis — Expositio

> Bureau I · Auctoritas Spectralis
> Aesthetic Authoritarian Associative Alliance (A4)

---

## I. Identity

- **Name** The Spectral Compliance Authority
- **Latin:** Auctoritas Spectralis
- **Motto** Codexium Chromaticus — Sequentiae Umbrarum 
 (Colours Codified - Shades Sequenced)
- **Version:** 1.0.0
- **Tagline:** The Spectral Compliance Authority — every
  palette issued by this bureau is law.
- **Classification:** PyQt6 desktop color theme governance tool.
- **Status:** Active development. Core pipeline functional.
  26/26 tests pass.

---

## II. Purpose

### Problem Statement

The Cogniverse suite shares a single aesthetic language —
ModusArcanus. Color values are hardcoded as constants across
every application. Changing the palette requires editing every
file. There is no mechanism for composing new palettes,
auditing their accessibility compliance, or distributing
them as a ratified contract.

### Motivation

Bureau I centralizes chromatic authority. One tool composes,
audits, ratifies, and exports the palette. All downstream
applications consume its output. The Wizard works with color
perceptually (OKLAB), not by guessing hex values.

### Intended Outcome

A ratified theme.json file serving as the canonical inter-app
color contract. Every Tower application reads this file.
Palette changes propagate by replacing a single file.

### Anti-Purpose

This is not a general-purpose design tool. It does not manage
typography, spacing, or layout. It governs color and nothing
else.

---

## III. Audience

- **Primary:** The Wizard (LordFingers) — sole operator.
- **Secondary:** Tower applications consuming theme.json.
  The Builder as integration partner.
- **Assumed Knowledge:** Familiarity with hex color values and
  the ModusArcanus palette system.

---

## IV. Design Philosophy

- Perceptual over mathematical — OKLAB space for all
  derivation, not RGB arithmetic.
- Authority over suggestion — ratified palettes carry
  SHA-256 seals and Latin designators.
- Live feedback over batch processing — the entire
  interface reskins in real time.
- Compliance as gatekeeper — WCAG AA auditing blocks
  ratification by default. Override is recorded.
- Rejects: Cool greys, pure white, pure black.

---

## V. Technical Concept

Two colors enter (BG and FG). Ten tokens exit. The
derivation pipeline operates in OKLAB perceptual space.
The audit engine validates every token pairing against
WCAG 2.1 and APCA standards. The render engine reskins
the application itself in real time.

Core abstractions: TokenSet (10 canonical tokens),
ContrastMatrix (per-pair ratios), SealRecord (SHA-256
hash + timestamp + designator), ThemePackage (the
complete theme.json export).

Key decisions: colour-science for OKLAB transforms,
SQLite for the Chromatic Registry, QSS regeneration
with 150ms debounce.

---

## VI. Functional Scope

### Core

- Hex input + OKLAB slider palette composition
- Automatic 10-token derivation from BG/FG pair
- Real-time WCAG 2.1 + APCA contrast matrix
- CVD simulation (deuteranopia, protanopia, achromatopsia)
- Ratification with SHA-256 seal + Latin designator
- Export: theme.json, .qss, .md palette card
- Chromatic Registry (SQLite) with full history
- Live self-reskinning preview

### Exclusions

- No AI integration, no network dependency
- No typography or layout management

---

## VII. Constraints

- Python 3.11+, PyQt6 6.6+, colour-science 0.4.4+
- Target: CastrumDigitos (Debian Trixie, KDE Plasma 6)
- Single-user application

---

## VIII. Success Criteria

- Compose, ratify, and export in under 60 seconds
- 26/26 tests pass; WCAG AA audit is correct
- Failure: ratified theme.json produces visual artifacts

---

## IX. Glossary

- **Compositio** — palette composition stage
- **Scrutinium** — contrast audit stage
- **Ratificatio** — seal generation and registry entry
- **Promulgatio** — export to theme.json, .qss, .md
- **Designator** — two-word Latin palette name
  (e.g. "Aureus Abyssalis")

---

*Ordo Discordia, Cosmos Inania*
