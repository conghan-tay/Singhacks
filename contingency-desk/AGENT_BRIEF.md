# Brief for the UI agent

Paste this whole file as the task. It is written to be handed over without further context.

---

You are building the front end of **The Contingency Desk**, a Streamlit app for a private-banking
Relationship Manager. It is a hackathon demo: one five-minute live walkthrough, judged on clarity
and actionability, not on feature count.

## Hard rules

1. **Do not compute anything.** Every number comes from `engine.shock()`, `out/facts.json`,
   or a `plans/*.json`. If a number you need is not available from those, stop and say so.
   Do not derive it yourself and do not put a numeric literal in the UI.
2. **Do not modify** `engine.py`, `store.py`, `verify.py`, `out/`, `seed/`, `plans/*.json`,
   `schema/`, or `tests/`. Those already exist, they are tested, and they are not yours.
3. **No network calls anywhere.** No LLM calls, no market data, no fonts from a CDN.
   The app must run with the machine offline.
4. **One process.** `streamlit run app.py`. No separate API, no build step, no node.
5. Python 3.11, `streamlit` and `pandas` only.

## Ownership split

**Already written. Read them, call them, do not touch them:**

```
engine.py    load_facts() load_plans() brent_now(facts)
             shock(facts, brent_level) -> {brent, mult, facilities{}, clients{}}
             evaluate_trigger(plan, state, facts, level=None) -> {hit, observed, level, ...}
store.py     arm(plan, rm, trigger_level=None)  dismiss(plan, rm, reason)
             fire(plan, observation)            action(plan, rm, rank)
             sweep(plans, state, facts, evaluate) -> [plan_id, ...]
             armed_vs_now(plan, state)          signature(plan)
             TransitionError, ALLOWED, and the state constants
```

Run `python3 engine.py` and `python3 store.py` — each has a `__main__` that prints a worked
example, including a full DRAFTED → ACTIONED walk with its decision log. That is the behaviour
you are wrapping.

**Yours to write:**

```
app.py       entry point, routing between the three screens, session state wiring
ui.py        render_plan_card(plan, state_snapshot, shocked) -> str    (returns HTML)
             render_evidence_chain(plan) -> str                        (returns HTML)
             render_board_row(plan, shocked) -> str                    (returns HTML)
             render_dial_strip(shocked) -> str                         (returns HTML)
style.py     CSS = """..."""  one constant, injected once
```

Five files. Nothing else. No arithmetic in any of them.

`shock()` returns per-facility `{lending_value, ltv, trigger_ltv, breached, headroom, cure_cash}`
and per-client `{delta_usd, delta_pct, household_usd, moves[]}` where each move carries
`{instrument_id, name, portfolio_id, beta, market_value_usd, pct, usd_delta, shocked_usd}`.
Everything the three screens need is in there.

## The three screens

**1. Board.** Four columns: `Fired` / `Armed and watching` / `Drafts awaiting you` / `Dismissed`.
Cards move between columns as state changes. Each card: client name, plan title, severity,
current distance to trigger as a percentage. Ranked within each column by severity then proximity.
This screen is on stage for five seconds. Do not over-invest in it.

**2. Plan card.** This is the product. Everything below is visible at once or one click away,
in this order:

- Title, client, state chip, severity
- **Trigger** — the expression in large type, then `trigger.derivation` rendered as a numbered
  list of `step -> value`, each with its `source` in small grey text. The trigger is *derived*
  on screen, never asserted.
- **Evidence chain** — `plan.evidence_chain` as a vertical path, one row per hop, connected.
  Each row shows `label`, `detail`, and `provenance` + `source_file` as a small monospace tag.
  Colour the `confidence: "medium"` and `"low"` hops differently. This element is the single most
  important thing on the screen; give it the most design attention.
- **Projected consequence** — `summary`, then `items` as a two-column table of `label` / `value`,
  with `basis` in small grey text underneath each.
- **Ranked actions** — each with `action`, `rationale`, and `second_order` clearly labelled as
  the cost. An action without its cost showing is a bug.
- **Client script** — `opening`, `key_points` as a list, then `likely_objection` / `response`
  visually paired.
- **Suitability** — `verdict` as a chip, `objective_conflict` in prose, then `checks` as a table
  with pass / fail / not_measured badges. `not_measured` must look *different* from both pass and
  fail — it is the finding, not an error.
- **Assumptions** — always visible, never behind a toggle. Plus `confidence.level` and
  `confidence.what_we_would_check`.
- **Actions bar**, state-dependent: `DRAFTED` -> [Arm] [Dismiss] with an editable trigger level;
  `FIRED` -> [Take action] [Stand down]; otherwise disabled.
- When state is `FIRED`: a band at the top showing **projected at arming** versus **actual now**,
  side by side, plus the armed signature, who armed it and when.

**3. Dial.** One slider, Brent, range 60 to 120, default 101.50, step 0.50.
Mark 72.40 on the axis as *"pre-conflict, 2026-02-27"*. On change, call `engine.shock`, re-render
the affected facility LTVs, and evaluate every `WATCHING` plan's trigger. Plans that trip move to
`FIRED` and the board updates.

## State machine

`store.py` already implements it — call `arm`, `dismiss`, `fire`, `action` and `sweep` rather than
writing transitions yourself. `schema/state_machine.md` is the reference for what each one does.
It appends
`{at, actor, from, to, note}` to `plan["governance"]["decision_log"]`. Arming writes `armed_by`,
`armed_at`, `armed_trigger_level`, and `armed_signature` = `store.signature(plan)`.
Dismissal requires a non-empty reason and `store` will raise `TransitionError` without one — surface
that as a validation message, do not swallow it. Keep the plan dict in `st.session_state`;
nothing is persisted to disk.

`STALE` is not implemented. Do not add it.

## Visual direction

**Read `docs/design.md` first and follow it literally** — it carries the colour tokens, the type
scale, the plan-card block order, the badge rules, and a worked HTML+CSS example of the evidence
chain. Treat its values as given rather than as suggestions. The summary below is the gist only.

Private bank, not consumer fintech. Restrained: one accent colour, generous whitespace, a serif
for headings if you like, system sans for everything else. No emoji, no gradients, no shadows on
everything, no progress rings. Numbers are the design. Right-align them, use tabular figures,
never truncate a currency figure.

Hide Streamlit's chrome:

```python
st.set_page_config(page_title="Contingency Desk", layout="wide")
st.markdown("<style>#MainMenu,footer,header{visibility:hidden}</style>", unsafe_allow_html=True)
```

Build the plan card as one HTML string through `st.markdown(..., unsafe_allow_html=True)` rather
than stacking Streamlit widgets — widgets will not give you the density this needs. Only the
buttons and the slider are real Streamlit controls.

## Acceptance

- `python3 -m pytest tests/ -q` still passes untouched (37 tests).
- `streamlit run app.py` works with the network disabled.
- Every figure rendered can be traced to a key in `facts.json` or a plan JSON. No literals in the
  UI code except labels.
- Walking PLAN-001 from `DRAFTED` to `ACTIONED` takes at most four clicks.
- Every state change goes through `store.py`. `grep -n 'state.*=' ui.py app.py` shows no direct
  assignment to `plan["state"]`.
- The dial at 72.40 fires PLAN-001 and PLAN-003 together. **At 79.00 nothing fires** — that is
  correct behaviour, not a bug. The trigger solves at 78.85.
