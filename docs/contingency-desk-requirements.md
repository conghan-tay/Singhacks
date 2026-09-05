# The Contingency Desk — Functional & Non-Functional Requirements

Companion to [`contingency-desk.md`](contingency-desk.md), which holds the product argument, the
client analysis and the demo script. This document is the build contract: what the system must do,
how well, and how we prove it.

**Scope assumption.** Two columns run through this document: **Demo** — what is built and enforced
by Saturday, verified by a test or by the demo itself — and **Bank** — what the same design implies
in a production private-banking deployment, which is what we argue when a judge asks "could this
operate inside a regulated bank." Anything with no Demo commitment is stated as such rather than
implied. We do not claim in the pitch anything the Demo column does not support.

Priorities: **M0** demo-critical, never cut (the governance argument dies without it) · **M1** must ·
**S** should · **C** stretch. These align with the build order in §5 of the design doc.

---

## 0. Actors and system boundary

| Actor | Role |
|---|---|
| **RM (Priscilla)** | Sole decision-maker. Authors nothing the system cannot explain; arms, edits, fires, dismisses. The only actor who can move a plan into `ARMED` or `ACTIONED`. |
| **Plan author agent** | LLM. Drafts plans, narrates the deterministic chain, critiques actions against mandate. Never evaluates a trigger, never computes a number that reaches the screen. |
| **Exposure engine** | Deterministic. Aggregation, look-through, LTV, mandate bands, liquidity coverage, trigger evaluation. |
| **Product control (Bank column only)** | Owns `exposure_edges`. In the demo this is seed data plus RM-authored edges; in a bank it is a maintained reference-data function with its own approval workflow. |
| **Market/event feed** | Demo: `market_context.csv` five snapshots + the scenario dial. Bank: intraday price and reference-data feeds. |

Out of scope, explicitly: order execution, booking, client-facing portal, real custody or credit
system integration, tax computation beyond flagging domicile-relevant unrealised positions,
authentication beyond a single-tenant API key.

---

## 1. Functional requirements

### F1 — Data and snapshot model

| ID | Requirement | Pri | Acceptance |
|---|---|---|---|
| F1.1 | Load the full dataset (20 clients, 24 portfolios, 1,015 holding rows across 5 snapshots, 62 instruments, 48 mandate rows, 393 transactions, 5 facilities, 20 planned cash needs, 115 market rows, 16 events, 28 RM notes) into a queryable store with the snapshot date as a first-class dimension. | M1 | A single query returns any client's positions at any of the five dates; totals reconcile to the CSVs. |
| F1.2 | Every monetary value carries a currency. Cross-currency aggregation uses the FX rate **at the same snapshot** as the position, and the rate used is recoverable from the result. | M1 | Hartono's USD 46.57m total is reproduced from SGD/USD/IDR legs; changing the snapshot changes both positions and rates together. |
| F1.3 | `event_log.csv` is the only permitted source of 2026 world events. No model-generated event claim reaches the screen. | M0 | Any event referenced in rendered output carries an `event_id`. A narration citing an event not in the log fails a test. |
| F1.4 | Known data imperfections are surfaced, not smoothed: quarterly-reported private funds are marked stale with their as-of date; missing or zero-priced instruments are flagged and excluded from lending value rather than defaulted to zero. | S | Ravi's and Hartono's lending-value computations list which inputs are stale and what was excluded. |
| F1.5 | Ingest is idempotent and re-runnable from the raw CSVs; no manual fix-ups in the store. | M1 | `make seed` twice yields identical row counts and identical engine output. |

### F2 — Exposure and look-through engine (deterministic)

| ID | Requirement | Pri | Acceptance |
|---|---|---|---|
| F2.1 | Aggregate exposure to a `risk_factor` **across all of a client's portfolios**, including custody accounts excluded from mandate measurement. | M0 | Hartono's Bara exposure returns 41.4% of total wealth, and the result states that `PF-0002` is custody and off-mandate. |
| F2.2 | Resolve look-through via `exposure_edges` over five source types: `direct`, `fund_sector`, `structured_underlying`, `source_of_wealth`, `collateral`. Edges are seeded reference data with `provenance` on every row. | M0 | `SYN-SP-0505` resolves to three underlying legs; each returned edge names its provenance. |
| F2.3 | Return exposure as an **evidence chain** — an ordered path of edges from source of wealth to consequence — not as a scalar. Every node in the path is addressable and openable. | M0 | The Hartono chain in §4/J2 of the design doc renders from data, with no hard-coded string. |
| F2.4 | Detect that multiple legs of a worst-of structure resolve to the same driving factor, and report the structure's diversification as nominal. | M1 | `SYN-SP-0505` is reported as single-factor (the Strait) with the three legs and their shared factor listed. |
| F2.5 | Detect the same underlying held twice through different wrappers within a client. | S | Ravi's Helios exposure via `SYN-ST-0103` and `SYN-SP-0502` combines into one figure. |
| F2.6 | Propose new candidate edges from `instruments.underlying_reference` free text. Proposals enter as `DRAFT` edges and are inert until a human accepts them. | S | A proposed edge never affects any computed figure before acceptance; acceptance is recorded with actor and timestamp. |

### F3 — Credit, collateral and liquidity

| ID | Requirement | Pri | Acceptance |
|---|---|---|---|
| F3.1 | Compute lending value per facility from collateral positions × per-asset advance rates, and LTV = drawn / lending value, at any snapshot. | M0 | Reproduces `CF-0005` = 59.15% today and 78.5% at 2025-12-31; `CF-0001` = 61.68% / 75.64% / 73.71% across the three dates. |
| F3.2 | Decompose an LTV change into the part driven by drawdown and the part driven by collateral value. | M0 | Ravi's Q2 breach attributes to the USD 1.7m draw, and reports the counterfactual 55.86% without it. |
| F3.3 | Invert the LTV arithmetic: given a facility and a trigger level, solve for the collateral market value, then the underlying move, then — through a stated beta — the observable trigger variable. | M0 | `CF-0005` yields Bara −16.08% and Brent ≈ 79, with every intermediate quantity shown and the beta labelled as an assumption. |
| F3.4 | **Pre-trade check**: given a proposed drawdown, return post-trade LTV against the facility's trigger before the draw is placed. | M1 | Ravi + USD 1.7m returns 75.64% vs a 75.0% trigger, with the arithmetic, not a verdict alone. |
| F3.5 | Match `planned_cash_needs` and uncalled `commitments` against what is actually sellable, and report which portfolio the shortfall would come from and the resulting concentration change. | S | `CN-001` (SGD 9m, Mar–Jun 2027) reports funding from the mandate portfolio and the resulting increase in Hartono's concentration. |

### F4 — Plans

| ID | Requirement | Pri | Acceptance |
|---|---|---|---|
| F4.1 | A plan is a persisted object: `trigger_expr`, `projected_consequence`, ranked `actions[]`, `client_script`, `suitability_verdict`, evidence chain reference, state, and arming record. | M0 | Schema exists; a plan round-trips through the store without loss. |
| F4.2 | `trigger_expr` is a typed expression over observable variables (`risk_factors`, market levels, facility LTV, exposure percentages) evaluated by the engine. **A trigger is never evaluated by a model.** | M0 | Trigger evaluation has no code path to the model adapter — enforced by a test, not by convention. |
| F4.3 | The agent drafts a plan from client context: holdings, mandate, risk profile, objectives, `rm_notes`, and the computed evidence chain. All figures in the draft are injected from engine output; the model may not author a number. | M0 | A draft's numbers are byte-identical to the engine values they cite. |
| F4.4 | Produce a `suitability_verdict` against the portfolio's mandate bands, concentration limits, risk profile and the client's stated objective, naming which constraint each action touches. | M1 | Hartono's verdict cites Balanced Growth bands and his stated diversification objective; Abdullah's cites "outside the Gulf, outside shipping." |
| F4.5 | Detect and surface where `rm_notes` contradict the numbers, quoting the note with its date. | M1 | Abdullah's 2026-04-15 note surfaces against the computed 42.1% correlated block. |
| F4.6 | The RM can edit any field of a draft — trigger level, actions, script — before arming, and the edit is attributed. | M0 | Trigger 79 → 82 is persisted with actor and timestamp, and the armed plan carries the edited value. |

### F5 — Arming, watching, firing (governance core)

| ID | Requirement | Pri | Acceptance |
|---|---|---|---|
| F5.1 | State machine `DRAFTED → ARMED → WATCHING → FIRED → ACTIONED \| DISMISSED`, with `WATCHING → STALE → ARMED` for re-authoring. Illegal transitions are rejected. | M0 | Transition tests cover every legal edge and at least three illegal ones. |
| F5.2 | One long-running Temporal workflow per plan. `ARMED` and `ACTIONED` are `interrupt()` points resumed by signal. | M0 | A plan armed, then the worker restarted, still fires correctly — demonstrated live if time allows, tested regardless. |
| F5.3 | Arming captures an immutable record: the exact plan content, the evidence chain **as computed at that moment**, the market state it assumed, actor, timestamp, signature. | M0 | The armed snapshot is retrievable after firing and is not mutated by later market moves. |
| F5.4 | On a market state change, re-evaluate every `WATCHING` trigger and fire those satisfied. One scenario change fires plans across multiple clients. | M0 | The dial to Brent 78 fires Hartono's and Abdullah's plans in the same pass. |
| F5.5 | A fired plan presents current computed values **alongside** the values projected at arming time. | M0 | The fire card shows both columns and the delta. |
| F5.6 | **Assumption drift**: if the world moved through a path materially different from the armed assumption, the plan fires as `STALE` and refuses to present its action set as still valid, stating which assumption broke. | M1 | A scenario in which Brent falls but Bara does not follow the assumed beta produces a drift flag naming the beta, not an action list. |
| F5.7 | Editing an armed plan supersedes it: the prior version is retained and linked via `superseded_by`. Armed plans are never mutated in place. | M1 | Version chain is queryable; the original arming signature survives. |
| F5.8 | Actioning a plan requires an explicit RM decision. No action executes on a trigger alone. | M0 | No code path reaches an action side effect without a signal carrying an actor. |

### F6 — Scenario and stress

| ID | Requirement | Pri | Acceptance |
|---|---|---|---|
| F6.1 | A scenario is a shock vector over `risk_factors`, applied through the same engine used for live evaluation. No separate scenario code path. | M1 | The engine module used by the dial is the module used by the watcher — one import, verified by test. |
| F6.2 | Beta and propagation assumptions are displayed on screen with their derivation (Feb→Mar Brent +43.6% vs Bara +31.7% ⇒ 0.73) and are never presented as a forecast. | M0 | The screen shows the derivation; the word "forecast" appears nowhere. |
| F6.3 | Second-order consequences propagate: direct position, structured-product legs, collateral LTV, and planned cash needs, all from one shock. | M1 | Brent 78 produces the Hartono chain end to end, including the `CN-001` consequence. |
| F6.4 | Results that the data cannot support are refused rather than invented (e.g. no barrier level for `SYN-SP-0505` ⇒ report the single-factor finding instead). | M0 | The output states the limitation explicitly; no fabricated barrier appears anywhere. |
| F6.5 | Nightly war-game: run a standing scenario set on a schedule and write drafts for the RM. | C | First cut line. Mocked if time is short, and labelled as mocked in the pitch. |

### F7 — Book view and prioritisation

| ID | Requirement | Pri | Acceptance |
|---|---|---|---|
| F7.1 | Four-column board: Fired / Armed and watching / Drafts awaiting you / Stale, across the whole book. | M1 | Renders in under the ten seconds it gets on screen. |
| F7.2 | Ranking = severity × proximity to trigger × client consequence, with **every component clickable through to its arithmetic**. | M1 | Clicking any ranking component opens the computation, not a tooltip. |
| F7.3 | Ranking weights are configurable; if cut, they are fixed constants and disclosed as such. | C | Last cut before J1 ranking becomes fixed. |
| F7.4 | Meeting prep view per client. | C | Second cut line. |

### F8 — Audit and explainability

| ID | Requirement | Pri | Acceptance |
|---|---|---|---|
| F8.1 | Every rendered number is traceable to its inputs and the transformation applied, in one interaction. | M0 | Any figure on the J2 card opens to its formula and source rows. |
| F8.2 | Every plan state transition is recorded with actor, timestamp, prior state and the inputs that caused it. | M0 | The Temporal event history plus the plan record together reconstruct the full life of a plan. |
| F8.3 | Model-authored content is visually distinguished from computed content wherever both appear. | M1 | The J2 card marks the script and rationale as drafted, and the figures as computed. |
| F8.4 | Every LLM call's prompt, model, version and output is retained against the plan version it produced. | S | Retrievable per plan; supports the "reviewed before the event" claim under challenge. |

---

## 2. Non-functional requirements

### N1 — Correctness and determinism

| ID | Requirement | Demo target / verification | Bank target |
|---|---|---|---|
| N1.1 | Engine output is deterministic: identical inputs ⇒ byte-identical results, no model in the numeric path. | Golden-value tests on all five clients' LTVs and Hartono's exposure percentages; CI fails on drift. | Same, plus daily reconciliation against product control's own figures. |
| N1.2 | Every figure is reproducible from stored inputs at a stated as-of time. | Recomputing an armed plan from its snapshot reproduces its projected consequence. | Point-in-time reconstruction for any past date, retained for the regulatory period. |
| N1.3 | Rounding and currency conversion are applied once, at presentation, never compounded through intermediate steps. | Unit test on a three-leg cross-currency aggregation. | Same, with a house rounding policy. |
| N1.4 | The system states uncertainty rather than filling gaps. Missing input ⇒ explicit gap, never a default. | F1.4 and F6.4 acceptance. | Data-quality SLA with product control. |

### N2 — Latency and throughput

| ID | Requirement | Demo target / verification | Bank target |
|---|---|---|---|
| N2.1 | Board load (whole book, ranked). | < 2 s cold, measured live. | < 2 s p95 at 40 clients/RM. |
| N2.2 | Trigger re-evaluation after a market state change, across the whole book. | < 1 s for 20 clients — the dial must feel instant on stage. | < 30 s p95 book-wide on an intraday tick; triggers evaluated on price change, not on a poll cycle. |
| N2.3 | Plan drafting (LLM path). | < 30 s, run ahead of the demo, never on the critical path of a live journey. | Asynchronous by design; the RM is never blocked on a model. |
| N2.4 | Evidence-chain expansion on click. | < 300 ms — it is the moment the argument lands. | < 300 ms p95. |
| N2.5 | Throughput sizing. | 20 clients, ~5 plans each ⇒ ~100 concurrent `WATCHING` workflows. | 1,000 RMs × 30 clients × 5 plans ≈ 150k long-running workflows. This is Temporal's designed load profile, not a rewrite; the argument is the sizing, not a benchmark we ran. |

### N3 — Durability and availability

| ID | Requirement | Demo target / verification | Bank target |
|---|---|---|---|
| N3.1 | An armed plan survives process restarts and deploys without losing its state or its arming record. | Restart the worker mid-watch; the plan still fires. Covered by the time-skipping workflow tests. | Multi-AZ Temporal, rolling deploys during market hours. |
| N3.2 | No application database holds workflow state; durability is Temporal's event history. Plan content and reference data live in Postgres. | Existing template property, retained. | Retention and archival policy on closed histories. |
| N3.3 | A trigger cannot be missed because a component was down: on recovery, evaluation runs against the market state that occurred while it was down and fires late rather than not at all, marking the delay. | Tested by stopping the watcher across a dial turn. | Same, with an SLO on detection-to-fire lag and alerting when it is breached. |
| N3.4 | Degraded mode: if the model provider is unavailable, watching, firing and all deterministic output continue; only drafting and narration degrade. | `MODEL_PROVIDER=fake` runs the full fire path. | Explicit degraded-mode contract; model unavailability is not a trading-risk incident. |

### N4 — Security and data protection

| ID | Requirement | Demo target / verification | Bank target |
|---|---|---|---|
| N4.1 | Client data is treated as real client data despite being synthetic — no data leaves the local stack except model calls, and no client data is committed to the repository beyond the provided dataset. | Repo check; `.env` never committed. | Data residency per booking centre (SG/HK), encryption at rest and in transit, no cross-border movement of client data without booking-centre approval. |
| N4.2 | Authorisation is RM-scoped: an RM sees only their own book, and arming authority is bound to the covering RM. | Single-tenant API key; scoping asserted in the data layer and stated as a known demo simplification. | JWT/OIDC at the gateway, entitlement checks per client relationship, four-eyes on plans above a materiality threshold. |
| N4.3 | Content sent to the model is minimised and bounded: client identity is not required for drafting and is pseudonymised in prompts; free-text `rm_notes` are delimited and treated as untrusted input. | Prompt-construction test asserts delimiting and the absence of identifiers. | Contractual no-training terms, or an in-perimeter model. This is the answer to "would JB send client data to OpenAI" — the architecture allows the model to be swapped without touching a graph node. |
| N4.4 | Prompt injection through `rm_notes` or `underlying_reference` cannot change a computed figure, a trigger, or a plan state. | The model has no write path to triggers or state — F4.2, F4.3 and F5.8 make this structural rather than a filter. Adversarial note test. | Same, plus content scanning on ingest. |
| N4.5 | Secrets are configuration, never code; no key appears in logs or traces. | Existing template property; log inspection in CI. | Managed secret store, rotation. |

### N5 — Governance, compliance and model risk

| ID | Requirement | Demo target / verification | Bank target |
|---|---|---|---|
| N5.1 | The arming record is the governance artefact: a human reviewed this reasoning **before** the event, signed and timestamped, with the assumed market state attached. Post-hoc rationalisation is structurally unavailable. | Demonstrated in J2, retained through J3, immutable per F5.3/F5.7. | Signed with the RM's identity credential; retained per the bank's advice-record retention period. |
| N5.2 | No advice reaches a client without an RM decision; no side effect executes on a trigger alone. | F5.8. | Suitability sign-off flow, plus adviser-attestation records. |
| N5.3 | Model outputs are labelled, bounded to narration and drafting, and never enter the numeric or control path. | F4.2/F4.3 tests; the boundary table in §3 of the design doc is the artefact. | Model risk management: registered model inventory, documented intended use, periodic validation of the drafting and critique steps. |
| N5.4 | Look-through mappings are reference data with provenance and human acceptance, not model inference. | `provenance` on every edge; proposed edges inert until accepted (F2.6). | Product control ownership with maker-checker on edge changes. |
| N5.5 | Full traceability of any figure or claim shown to an RM or read to a client. | F8.1/F8.2. | Supervisory review and audit extract on demand. |
| N5.6 | Assumptions are labelled as assumptions wherever they appear, including in client-facing script text. | F6.2; script review in J2. | Disclosure standards applied to generated client-facing language. |

### N6 — Usability

| ID | Requirement | Demo target / verification |
|---|---|---|
| N6.1 | The RM can reach the reason behind any ranking or figure in one click, and back out in one. | Verified by walking J1 → J2 without a keyboard. |
| N6.2 | A fired plan requires no reconstruction of context: the reasoning was written and reviewed before the event and is shown as armed. | The J3 card opens complete. |
| N6.3 | The client script is speakable aloud without editing — plain language, no jargon, no unexplained numbers. | Read Hartono's script on stage as written. |
| N6.4 | Nothing on screen is unattributed: computed, drafted, or assumed, each is visually distinct. | F8.3. |

### N7 — Operability and integration

| ID | Requirement | Demo target / verification | Bank target |
|---|---|---|---|
| N7.1 | Structured JSON logs, Temporal Web UI for run inspection, optional LangSmith traces. | Existing template property. | Central log aggregation, trace sampling with a redaction policy. |
| N7.2 | External systems sit behind interfaces: market data, custody positions, credit facilities, and the model provider are each replaceable without touching graph nodes. | Repository/adapter interfaces retained from the template. | Integration to core custody, credit and market-data platforms; the CSVs are the seam, not the design. |
| N7.3 | Business tools are served over MCP, independent of the agent process. | Existing template property. | Tool services owned by their domain teams. |
| N7.4 | Seeded reference data (`risk_factors`, `exposure_edges`) is versioned and re-seedable; a change to an edge is auditable. | `make seed` is idempotent; edges carry provenance. | Reference-data release process. |
| N7.5 | Cost per plan draft is bounded and observable. | Fake provider for tests so the suite costs nothing; drafting is not on the live demo path. | Per-RM cost ceiling; drafting batched overnight (F6.5). |

---

## 3. Requirements we are deliberately not meeting

Stating these is worth more than pretending otherwise, and each has a one-line answer if asked.

- **Real-time market data.** Five snapshots plus a dial. The engine is written against a market-state
  interface, so the feed is a swap, not a redesign.
- **Multi-RM authorisation and entitlements.** Single tenant, one API key. The scoping point is
  identified (N4.2), not implemented.
- **Barrier-level modelling of structured products.** The dataset does not carry barriers. We report
  the single-factor finding instead, which is the stronger claim and is defensible from the data.
- **Beta stability.** One regime, one regression window, two observations. Labelled on screen as an
  assumption with its derivation; it is an input the RM can override, not a forecast we defend.
- **Tax computation.** Domicile is used for flagging, not for calculating a liability.
- **Twenty clients in depth.** Three clients, deliberately. The board covers twenty; the reasoning
  covers three, per the challenge's own guidance.

---

## 4. Traceability

| Judging criterion | Weight | Requirements carrying it |
|---|---|---|
| Client-Centric Innovation | 25% | F2.1–F2.5, F3.3, F3.4, F4.4, F4.5, F6.3 |
| User Experience & Design | 25% | F7.1–F7.2, F8.1, F8.3, N6.1–N6.4, N2.1, N2.4 |
| Technical & Operational Feasibility | 25% | F1.3, F4.2, F5.1–F5.3, N1, N3, N4, N5, N7 |
| Strategic Impact | 25% | F5.3 (arming as the governance artefact), F5.8, N5.1, N5.2, N4.3 |

Cut order from §5 of the design doc, restated as requirement IDs: **F6.5 → F7.4 → F5.6 → F7.3.**
**F2.3 and F5.3 are never cut** — the evidence chain and the arming record are the entire argument.
