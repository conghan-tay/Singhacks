# Contingency Desk — design readiness for the portfolio build

Written 2026-09-05, after the pivot from hackathon demo to portfolio piece.
Target: a system whose UX, service decomposition and tradeoffs hold up under interview questioning.

---

## Part 1 — What exists today

Three folders under `SingHacks/`. Git tree is clean at `d6f3412` (5 commits, main).

### `contingency-desk/` — the hackathon build (the domain asset)

| File | LOC | State | Verdict for the portfolio build |
|---|---|---|---|
| `engine.py` | 111 | Pure arithmetic: Brent-beta shock, facility LTV, trigger eval, `resolve()` variable dispatch | **Keep as-is.** Already a clean pure core with an extension seam. Becomes a library, not a service. |
| `store.py` | 186 | Plan state machine, sha256 arming signature, append-only decision log, `sweep()` | **Keep the model, replace the mechanism.** The state machine and signature are the interview story. The storage (`st.session_state`, deepcopy) is a toy. |
| `verify.py` | 288 | Recomputes every on-screen number from the challenge CSVs → `out/facts.json` | **Keep.** Becomes the offline ingestion/snapshot job. |
| `seed/build_seed.py` | 97 | 12 risk factors, 21 exposure edges with per-edge provenance | **Keep.** Becomes reference data with an owner. |
| `plans/build_plans.py` | 345 | Emits PLAN-001..003 with computed numbers, hand-written prose | **Replace.** This is the offline stand-in for the authoring agent. It becomes the real agent's contract and its golden-output fixture. |
| `schema/plan.schema.json` | 518 | The plan contract, enforced in tests | **Keep and version.** Best single artefact in the repo. |
| `app.py` / `ui.py` / `style.py` | 225 / 200 / 153 | Streamlit board, plan card, scenario dial. Escaped HTML, no arithmetic in the view | **Decision pending** (see Part 3). Good separation, wrong runtime for a UX showcase. |
| `tests/` | 455 | ~43 assertions pinning numbers, plans, engine, state machine | **Keep.** These are unit/contract tests. There are no E2E tests. |
| `docs/` | 614 | architecture, design tokens, sequence, glossary, state machine | Partial; see Part 2. |

Note: project memory records "BLOCKING: `app.py`, `ui.py`, `style.py` do not exist" — that is now
stale. The UI was built in `5f6f7e7`/`97cc371` and merged in PR #1.

### `MySingHacks/` — the architecture asset (different domain, right shape)

A finished production agentic template for a *customer support refund* flow. Go gateway as the only
API surface, Temporal for durable execution, LangGraph nodes running as Temporal activities, Chroma
retrieval, Redis rate limits, an MCP tool service, docker compose, a k8s manifest, GitHub Actions CI,
Go + Python unit tests, and a real E2E harness (`compose.e2e.yaml`, `RUN_E2E=1`, poll-until-status).
Dependencies are exactly pinned in `pyproject.toml`.

This is not on the Contingency Desk demo path and never was. For the portfolio build it is the single
most reusable thing in the repo: **lift the patterns, not the domain.** Specifically worth lifting —
the gateway/worker split, the "worker serves no HTTP, it polls a queue" argument, the E2E harness
shape, the version pinning discipline, and the capability→implementation table in its README.

### `singhacks-jb-wealth-intelligence/` — challenge data pack

11 CSVs + `rm_notes.json` + problem statement. Input only, read-only, never modified.

### The honest summary

The **domain model is done and it is good**: a deterministic engine, a governed state machine, a
signed approval that provably predates the outcome, an evidence chain where every citation resolves
to a real row in a real file. That is the part most projects fake.

What is missing is **everything that makes it a system**. There are no services, no persistence, no
API, no events, no asynchrony, no concurrency, no failure handling, and no agent on the live path.
It is one process reading JSON files into session state. For a hackathon that was the correct call.
For "expert knowledge in building agentic and backend systems" it is currently unevidenced.

---

## Part 2 — Checklist against the design artefacts

> **Correction, same session.** The first version of this checklist was written without opening
> `MySingHacks/docs/`, which holds `contingency-desk.md` (369 lines: product argument, data model,
> the deterministic/LLM boundary, journeys J0–J5, build order and cut lines) and
> `contingency-desk-requirements.md` (221 lines: F1–F8 functional requirements and N1–N7
> non-functional requirements, each with a priority and an acceptance criterion). Five rows below
> were called MISSING or PARTIAL when they were substantially written. The table is corrected.
> The headline finding changed as a result — see *The actual gap*, below.

Legend: **DONE** usable with reframing · **PARTIAL** exists, materially incomplete ·
**MISSING** does not exist · **CONFLICTS** exists and contradicts a decision taken

| # | Artefact | Status | Where it stands / what it needs |
|---|---|---|---|
| 1 | **Goal** | DONE | `contingency-desk.md` opens with the product statement and the governance thesis — "a trading desk does not work out what an event means after it happens; it writes the plan before, and executes on the trigger." Needs reframing for a portfolio reader, not rewriting. |
| 2 | **User journeys / stories** | DONE | J0–J5, written in depth: overnight war-game, the Monday board, review-and-arm, the fire, meeting prep, the dial. Missing only the *failure* journeys — fires at 03:00 with no RM awake, snapshot invalidates an armed plan, duplicate tick, watcher restart mid-watch — and the operator journeys (replay, backfill, re-author). Those are the event-driven ones, so they carry weight now. |
| 3 | **Functional requirements** | DONE | F1–F8, ~40 numbered requirements, each with priority (M0/M1/S/C) and a concrete acceptance criterion. Better than most production specs. Needs: priorities re-derived (M0 meant "the pitch dies without it") and the M0/M1 split re-cut against the new target. |
| 4 | **Non-functional requirements** | PARTIAL | N1–N7 exist and N1 (determinism), N4.4 (injection is structurally impossible, not filtered) and all of N5 (governance, model risk) are strong enough to keep verbatim. Insufficient for the new architecture in six specific ways — see below. |
| 5 | **Out of scope** | DONE | §0 states the system boundary; §3 "Requirements we are deliberately not meeting" gives six exclusions each with a one-line defence. This is the right shape. Re-decide the contents: every exclusion was chosen against a 12-hour clock. |
| 6 | **Future extensions** | MISSING | The cut lines (J0 → J4 → drift → ranking weights) are adjacent but they are deferrals under deadline, not a roadmap. |
| 7 | **Core entities and schemas** | PARTIAL | §3 sketches `risk_factors`, `exposure_edges`, `plans` at field level; `plan.schema.json` (518 lines) is real and enforced. Missing: DDL, the snapshot and market-tick entities, and — the important one — the **domain event schemas** with a versioning and compatibility policy. |
| 8 | **APIs / interfaces** | MISSING | Genuinely absent. N7.2 asserts adapters as a principle; no contract exists anywhere. Needs the public REST + SSE surface, the internal event contracts (topics, keys, ordering scope), the watcher interface, and the agent's tool interface. |
| 9 | **Data flow** | PARTIAL | `architecture.md` splits offline vs in-app, accurate for the Streamlit build. Needs redrawing for the event path: ingest → snapshot → projection → tick → watcher → domain events → read model → UI, with the authoring pipeline hanging off snapshot events. |
| 10 | **High-level design** | PARTIAL | Two good mermaid diagrams, plus real decisions already taken in the requirements (F5.2 one Temporal workflow per plan; N3.2 durability lives in Temporal, not an app DB). Still missing the **tradeoff register** — the artefact the interview actually probes. |
| 11 | **Frameworks / versions** | PARTIAL | `MySingHacks/pyproject.toml` pins exactly and comments *why* each pin. Carry that standard. The dependency list itself changes with the domain, and D2 adds Postgres to a stack that has none. |
| 12 | **E2E tests** | PARTIAL | Better than I first said: every F-requirement carries an acceptance criterion, and those are E2E test cases already written in prose (F3.1's "reproduces CF-0005 = 59.15% today and 78.5% at 2025-12-31" is a test). What is missing is the harness for this domain and the sad paths — `MySingHacks/tests/e2e/` has the shape to copy. |
| 13 | **Build plan** | PARTIAL | §6 gives seven ordered steps with explicit cut lines and a never-cut rule. Not PR-shaped: no per-step test or done condition, and the ordering optimises for "what survives if the clock runs out", which is no longer the constraint. |

### The actual gap

Not missing documents. **The spec is well ahead of the implementation, and it was written for a
different architecture than the one now chosen.**

`contingency-desk-requirements.md` describes a system with a Temporal workflow per plan, Postgres,
MCP-served tools, assumption drift and the `STALE` state, supersession chains, pre-trade LTV checks,
and an acceptance workflow for agent-proposed exposure edges. The built Streamlit app implements
roughly a third of that — no Temporal, no Postgres, no `STALE`, no supersession, no pre-trade check,
no live agent. `contingency-desk/` is not an implementation of this spec; it is a demo-shaped subset
of it. Before the spec becomes the portfolio contract, that delta needs auditing row by row, because
a document claiming F5.6 against code that does not implement it is worse than no document.

### Why the NFRs are insufficient — six specific gaps

1. **The Demo/Bank two-column structure is now unusable.** Every N row splits "what is proven by
   Saturday" from "what the design implies in a bank". There is no Saturday. Each row has to be
   re-decided into a build target or a stated non-goal. As written the doc permits claiming the Bank
   column without building it — legitimate for a pitch, fatal when an interviewer asks whether you
   built it.
2. **N3.2 conflicts with D2.** It states: *"No application database holds workflow state; durability
   is Temporal's event history. Plan content and reference data live in Postgres."* D2 makes a
   Postgres outbox the event log. That is now two durable logs, and nothing says which is the source
   of truth for plan state. This is the most consequential gap in the document and precisely the
   thread an interviewer pulls.
3. **No event-driven NFRs exist,** because the design was not event-driven. Absent: delivery
   semantics, consumer idempotency, ordering scope (per plan? per client? global?), event schema
   versioning and compatibility, consumer lag SLO, replay semantics, poison-message and DLQ handling,
   outbox drain latency, and event-time vs processing-time. N2.2's *"triggers evaluated on price
   change, not on a poll cycle"* is the only clause pointing this way. Note N3.3 — *fire late rather
   than not at all, marking the delay* — is already a genuine event-driven requirement, well stated.
4. **N2's targets are stage-shaped.** *"< 1 s for 20 clients — the dial must feel instant on stage."*
   N2.5 says outright that *"the argument is the sizing, not a benchmark we ran."* Honest for a pitch;
   for a portfolio piece a scaled load test is achievable, which turns the weakest NFR section into
   the strongest artefact in the repo.
5. **N6 usability predates D4.** Verification is *"walking J1 → J2 without a keyboard"* and *"read the
   script on stage as written."* With React and SSE the real requirements are about asynchrony: what
   the RM sees when a plan fires while she is on another screen, optimistic vs server-confirmed state
   on arm, SSE reconnect and gap-fill, and the loading/empty/error state of every view. None specified.
6. **§4 traceability maps to judging criteria** — four criteria at 25% each. They no longer exist.
   Remap to something real or delete the table; leaving it makes the whole document read as a pitch
   annex.

Keep verbatim: N1 in full, N3.1, N3.3, N3.4 (degraded mode when the model provider is down), N4.3,
N4.4, and all of N5. N5.1 — the arming record as the artefact that makes post-hoc rationalisation
structurally unavailable — is the best paragraph in the repository and should survive every rewrite.

### Stale or wrong, fix before it propagates

1. Project memory said the UI was unbuilt. It is built — `app.py`/`ui.py`/`style.py`, PR #1. Corrected.
2. `AGENT_BRIEF.md` is a spent delegation contract. Archive it; it must not read as current spec.
3. `contingency-desk/README.md` still frames the repo as a hackathon build packet.
4. `PLAN-001` suitability says "largest is SYN-EQ-0001 at 19.6% of PF-0001 / pass". The real figure is
   26.56%, and BALG's `max_single_position_pct` is 15.0 — SYN-FI-0204 at 15.72% also exceeds it. A
   test pins the data and names the discrepancy without asserting a verdict. Deliberate, but a
   portfolio reviewer will find it where a judge would not have.
5. "PF-0002 is a custody account so no mandate limit applies" — `portfolios.csv` does assign BALG to
   PF-0002. What is true is `service_model=Custody`, `benchmark="None - custody only"`. Note F2.1's
   acceptance criterion already states this correctly, so the two documents disagree.
6. `CF-0002` (CL-0014) breaches at Brent 106.46, inside the dial range, with no plan attached. This is
   Lau Chi Ming, held in reserve for judges' questions — a reserve that no longer has a purpose.
7. `store._now()` is wall-clock, so live entries date 2026-09-05 against a dataset whose "today" is
   2026-08-26. Trivial in Streamlit; in the event-driven rebuild this is the event-time vs
   processing-time decision and needs designing, not patching.

### Two artefacts not on the list that I would add

- **ADR log.** One short record per decision, written as it is taken. Cheap during the build,
  impossible to reconstruct afterwards, and the direct answer to "what did you reject?"
- **Observability and demonstrability.** Nobody evaluating a portfolio piece runs `docker compose up`.
  Structured logs, traces, and an event-timeline view that makes the async path *visible* are what
  convert backend work into something a reader can see. Highest value-per-hour item in the plan.

---

## Part 3 — Decisions that gate the design document

None of the artefacts above can be written honestly until these are settled.

**D1 — Target shape.** Rebuild the Contingency Desk as a distributed system in a fresh repo reusing
MySingHacks' patterns; or fold the wealth domain into MySingHacks, replacing the support-ticket
domain; or keep one repo with the Streamlit app as a legacy demo path alongside a new backend.

**D2 — Event substrate.** Kafka/Redpanda (the default answer, heaviest); NATS JetStream (lighter,
still a real log); or Postgres as the log — transactional outbox plus `LISTEN/NOTIFY` — with Temporal
for durable per-plan watching. Option three is defensible and often the *better* interview answer,
but only if the NFRs are written first to justify it.

**D3 — Persistence model.** Event-sourced plan aggregate with CQRS read models, or a conventional
table plus the existing append-only decision log. The signature and decision log already lean toward
the first; event sourcing without a real need is also the classic over-engineering flag.

**D4 — Frontend.** "Clean, thoughtful, intuitive UX/UI" is an explicit goal, and Streamlit cannot
carry it — the current `ui.py` already fights the framework by rendering raw HTML through
`st.markdown`. A real frontend costs time that would otherwise go to the backend story.

**D5 — Agent scope on the live path.** The hackathon deliberately froze the LLM output offline. For
the portfolio piece the authoring agent should run for real — which raises everything interesting:
non-determinism at a boundary that must stay deterministic, cost and latency, retries, evaluation,
and how a drafted plan is proven faithful to the numbers it cites.

---

## Part 4 — Decisions taken (2026-09-05)

| ID | Decision | Consequence |
|---|---|---|
| **D1** | **Fold the wealth domain into `MySingHacks`.** | Inherits a working compose/k8s/CI/E2E stack on day one. Requires *removing* the support-ticket domain, not layering beside it, and renaming the project — a repo that reads as "template with a domain bolted on" defeats the purpose. The Go gateway stays the only API surface; the Python worker keeps polling the Temporal task queue. |
| **D2** | **Postgres transactional outbox + `LISTEN/NOTIFY` as the log; Temporal for durable per-plan watching.** | Adds Postgres to a stack that currently has none (Temporal dev-server uses SQLite; Redis is rate limits only). Every write that must publish an event writes the event in the same transaction. Consumers are idempotent, delivery is at-least-once, ordering is per plan aggregate. The NFRs must justify this over Kafka explicitly — that argument is the point of choosing it. |
| **D3** | **Open.** Event-sourced aggregate + CQRS vs table + append-only decision log. | Blocked on NFRs. Durability, replay and audit-retention requirements decide it. Do not pre-empt in the entity schemas — model the events either way, since D2 requires them regardless. |
| **D4** | **Next.js + React; SSE for fires.** | The board becomes a live view: plans arrive and fire without a refresh, which is what makes the async backend legible to a reader. Streamlit's `app.py`/`ui.py` retire; `style.py`'s tokens and `docs/design.md` carry over as the design system. The gateway grows an SSE endpoint alongside REST. |
| **D5** | **Recommended, not yet confirmed: the authoring agent runs live.** | "Agentic systems" is a stated goal and a frozen JSON file does not evidence it. Runs as a LangGraph graph whose nodes are Temporal activities (the pattern already in the repo), triggered by a snapshot event. Tests pin it with recorded fixtures so the suite stays deterministic and free. |

### Open tension worth naming now

D1 hands you Chroma, Redis and an MCP tool service. Each needs a real justification in the new
domain or it should come out: retrieval over `rm_notes.json` and mandate policy is a genuine fit;
Redis rate limiting at the edge is fine; the MCP service is a strong fit if the **deterministic
engine is exposed as the agent's tools** — that makes "the model reads numbers, it never computes
them" an architectural fact rather than a claim. Carrying any of them unjustified is worse than not
having them.

### Next artefact

NFRs, ahead of the HLD, because D2 and D3 both hang off them.
