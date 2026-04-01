# Exposition.dux.tome.md
### A Structural Guide for Application Exposition Documents

---

## What Is an Exposition Document?

An exposition document is the foundational record of an application's *why*, *what*, and *how* — written before, during, or after development to articulate intent, guide decisions, and communicate the project to collaborators, stakeholders, or your future self. It is not a user manual, not a changelog, and not a spec sheet. It is a living argument for why the application exists and how it should be understood.

---

## I. Identity

The opening section establishes what the application *is* at its most essential. It should be answerable in a single paragraph by anyone who reads it.

- **Name & Version** — the canonical name of the application and its current or intended version.
- **Tagline or Thesis** — one sentence that captures the soul of the application. This is not a marketing line; it is a precise statement of purpose.
- **Classification** — what kind of thing is this? (tool, platform, service, framework, game, interface, etc.) Naming the category sets the expectations everything else is measured against.
- **Status** — where does the project currently stand? (concept, prototype, active development, stable, deprecated) Be honest.

---

## II. Purpose

This section answers: *why does this application exist?*

- **Problem Statement** — describe the specific problem, friction, gap, or need the application addresses. Resist the urge to frame this as a pitch. Describe the problem as it actually exists in the world.
- **Motivation** — what drove the creation of this application? Personal necessity, observed need, intellectual interest, commercial opportunity? Motivation provides human context.
- **Intended Outcome** — what is the world like *after* someone uses this application well? What has changed, improved, or become possible?
- **Anti-Purpose** — optionally, what is this application explicitly *not* trying to do? Scope boundaries stated here prevent scope creep later.

---

## III. Audience

Clarity about who the application is for shapes every subsequent decision.

- **Primary Users** — who is the core user? Describe them by behavior and context, not demographics. What do they already know? What do they need to accomplish?
- **Secondary Users** — who else interacts with the application, even indirectly? (administrators, API consumers, collaborators, etc.)
- **Assumed Knowledge** — what can the application reasonably expect its users to already understand? This defines the floor of complexity that is acceptable.
- **Out-of-Scope Audiences** — who is this application not designed for? Stating this is not exclusion — it is honesty about fit.

---

## IV. Design Philosophy

Design philosophy is the set of values and principles that guide every decision where multiple reasonable options exist. It does not describe what was built — it describes *how decisions were made*.

- **Core Principles** — list 3–6 guiding values in plain language. These should be specific enough to adjudicate real tradeoffs. ("Simple over powerful" is a principle. "Good UX" is not.)
- **Tradeoff Positions** — where two good things are in tension, which does this application favor and why? (e.g., flexibility vs. simplicity, performance vs. readability, convention vs. control)
- **Aesthetic Direction** — what tone, feel, or sensibility should the application carry? This applies to code, interface, and documentation alike.
- **What This Philosophy Rejects** — good design philosophy has edges. Note what approaches or values were considered and consciously set aside.

---

## V. Technical Concept

This section describes the *architecture of ideas* — not the implementation detail, but the conceptual model that the technical decisions are built on.

- **Mental Model** — how should a user or developer think about what this application does internally? Describe the dominant metaphor or abstraction.
- **Core Abstractions** — what are the key concepts, entities, or objects the application reasons about? Name them and define their relationships in plain terms.
- **Data Flow Overview** — at a high level, how does information move through the application? What enters, what transforms, what exits?
- **System Boundaries** — what does the application own, and what does it depend on externally? Where are the edges of its responsibility?
- **Key Technical Decisions** — what choices were made that significantly shaped the architecture? Note the decision and the reason, not just the outcome.

---

## VI. Functional Scope

This section defines the surface area of what the application does — not how it does it.

- **Core Capabilities** — the primary functions the application provides. These are the things it must do to fulfill its purpose.
- **Supporting Capabilities** — features or functions that exist to enable, extend, or improve the core, but are not the purpose themselves.
- **Explicit Exclusions** — things the application will not do, even if they seem related. This is as important as what it includes.
- **Future Scope (Optional)** — capabilities that are not present now but are anticipated or reserved for. Keep this brief; it is a signal of direction, not a promise.

---

## VII. Constraints & Context

Every application exists inside a set of real-world pressures. Naming them honestly makes the exposition trustworthy.

- **Technical Constraints** — platform targets, language choices, performance requirements, dependency limits, or infrastructure realities that bound what is possible.
- **Time & Resource Constraints** — the practical limits of development capacity that influenced what was built or deferred.
- **External Dependencies** — third-party services, APIs, libraries, or standards the application relies on. Note what risks those dependencies carry.
- **Regulatory or Compliance Context** — any legal, privacy, accessibility, or standards requirements that must be satisfied.

---

## VIII. Success Criteria

An exposition document should be falsifiable. Define what a successful application looks like.

- **Functional Success** — the application works as described when these conditions are met.
- **User Success** — a user has been served well when they can accomplish this.
- **Quality Benchmarks** — performance targets, reliability expectations, test coverage goals, or other measurable standards.
- **Failure Conditions** — what would indicate the application has failed its purpose, even if it technically runs?

---

## IX. Glossary (As Needed)

For applications with domain-specific terminology, internal naming conventions, or concepts that carry precise meaning within this project, a glossary prevents ambiguity throughout the document and across collaborators.

Each entry should define the term as it is used *in this application*, not as it exists generically. Note where usage diverges from common convention.

---

## X. Revision Notes

An exposition document changes as understanding deepens. Keep a brief log of significant revisions — not every edit, but any change that reflects a meaningful shift in purpose, philosophy, or scope.

- Date
- What changed
- Why it changed

---

## Guidance on Use

This structure is not a form to fill out. It is a set of questions to answer in whatever order makes sense for the project at hand. Some sections will be dense; others may be a single sentence. The measure of a good exposition document is not its completeness but its clarity — a reader should come away knowing what this application is, why it exists, and how it thinks.

Write it in your own voice. Revise it when the application changes. Share it when collaboration begins.

---

*Exposition.dux.tome.md — Structural Guide v1.0*
