# Glossary

Terms as this project uses them. Where a term has a general meaning and a narrower one here,
the narrow one wins.

---

## The core verb

**Arm / arming a plan.** The RM reads a `DRAFTED` plan, optionally changes the trigger level,
and signs it. The plan becomes live and can fire without her. Literal sense: arming a tripwire —
the mechanism was already built, arming is what lets it go off on its own.

Arming writes `governance.armed_by`, `armed_at`, `armed_trigger_level` and `armed_signature`,
then registers `(variable, operator, level)` with the watcher. The value of the record is the
timestamp: the decision is made while the market is calm and provably before the event.

**Armed signature.** `sha256(json.dumps(plan_body, sort_keys=True))` with the `governance` **and
`state`** keys removed - both of those change legitimately as the plan moves through its lifecycle,
the reasoning does not. `store.verify_signature(plan)` recomputes it and compares; the fired card
shows the result. Proves the body she approved was not quietly rewritten afterwards. This is the
artefact a post-hoc AI explanation cannot produce.

**Pre-armed plan.** PLAN-003 ships in `WATCHING`, armed by Priscilla at 2026-08-24 08:52 - twelve
days before the dial moves. PLAN-001 ships `DRAFTED` and is armed live. The pair is deliberate: the
live one shows what arming *is*, the seeded one shows what the arming record is *worth*, because its
timestamp and signature were written before the market moved. `store.arm(..., at=)` backdates only
in the offline authoring pass; the UI never passes it.

**Armed trigger level.** The level the *human* signed, which may differ from the level the agent
drafted. `trigger.level` keeps the drafted value; the watcher uses `governance.armed_trigger_level`.
Both render on the fired card, so machine proposal vs human approval is always visible.

**Human interrupt.** A transition only a person can perform. There are exactly two:
`DRAFTED → ARMED` (before the event) and `FIRED → ACTIONED` (nothing executes without it).
Everything between them is arithmetic. Borrowed from Temporal's `interrupt()`.

---

## Plan lifecycle

| State | Meaning |
|---|---|
| `DRAFTED` | Agent authored it overnight. Nothing armed, nothing sent. |
| `ARMED` | RM signed it. Momentary — the system moves it on immediately. |
| `WATCHING` | Trigger registered. Evaluated on every market observation. |
| `FIRED` | Trigger evaluated true. Needs a human decision. |
| `ACTIONED` | RM picked a ranked action. Terminal. |
| `DISMISSED` | RM rejected it, with a reason. Terminal. Reasons feed authoring. |
| `STALE` | Armed, but the world moved off the assumption. **Not implemented** — cut. |

**Decision log.** `governance.decision_log`, append-only: `{at, actor, from, to, note}` per
transition. Nothing is ever edited in place.

**Plan.** One JSON object per (client, scenario). Trigger + evidence chain + projected
consequence + ranked actions + client script + suitability + assumptions + confidence +
governance. Validated against `schema/plan.schema.json`.

---

## Trigger machinery

**Trigger.** An observable condition, e.g. `BRENT < 79.00`. Four fields do the work:
`variable`, `operator`, `level`, and `evaluated_by`.

**`evaluated_by: "deterministic"`.** A schema `const`. A plan claiming a model evaluates its
trigger fails validation. The sentence for the slide: *a trigger is never evaluated by a model.*

**Derivation.** The ordered arithmetic from source data to the trigger level, rendered on the
card as `step → value` with a `source` per step. The trigger is derived on screen, never asserted.

**Distance to trigger.** `distance_pct` — signed % move from `current_value` to `level`.
PLAN-001: -22.17%. Used for board ranking alongside severity.

**Watcher.** The deterministic component holding `(variable, operator, level)` per armed plan and
evaluating it against observed market state. In the demo it is a loop over `WATCHING` plans on
slider change; in the production slide it is a durable workflow per plan.

**Fired observation.** The market state that made the trigger true, recorded on the plan.

---

## Evidence and look-through

**Look-through.** Seeing the risk factor *behind* an instrument rather than the instrument's own
label — a fund's sector, a structured note's underlyings. Here it is **seeded reference data,
not a runtime inference**, which is how a bank actually does it (Product Control owns the map).

**Risk factor.** ~15 rows: `BARA`, `BRENT`, `HK_RESIDENTIAL`, `XAU`, etc. The thing exposure
resolves down to.

**Exposure edge.** One row of the look-through map: `source_id → risk_factor_id` with a `weight`,
a `source_type` (`direct` | `fund_sector` | `structured_underlying` | `source_of_wealth` |
`collateral`) and a `provenance` string naming the column it came from or `RM-authored`.

**Evidence chain.** The ordered path of edges from source-of-wealth to consequence, one **hop**
per row, each carrying `provenance`, `source_file` and a `confidence`. The single most important
element on the plan card. Hartono's: coal wealth → 41.42% direct Bara → worst-of leg of the FCN →
collateral for CF-0005 → funds CN-001.

**Provenance.** Which column or table an edge came from. Present so a hop can be audited rather
than trusted.

---

## Wealth-management terms

**RM.** Relationship Manager. Priscilla Ong; 20 clients, Asia desk. The user.

**Lombard loan.** Credit secured on a portfolio of securities rather than property. CF-0005 is
one: SGD 8m drawn against PF-0002.

**Facility / drawn.** The credit line and the amount actually borrowed against it.

**Advance rate.** Fraction of a holding's market value the bank will lend against, per asset.
Bara 50%, USD call deposit 90%. Riskier asset, lower advance rate.

**Lending value.** Σ (market value × advance rate) across the collateral pool. The denominator
of LTV. Falls when the collateral falls.

**LTV.** `drawn / lending_value`. CF-0005: 59.15% today, margin call at 70%.

**Margin call.** The lender demanding cash or more collateral once LTV crosses the trigger.

**Cure.** What it takes to bring LTV back under the trigger — cash paydown or additional
collateral. At Brent 72.40: SGD 418,143 cash, or SGD 1,194,693 of collateral.

**Mandate / mandate bands.** The agreed asset-allocation ranges for a portfolio (BALG =
Balanced Growth: equity 40–65%, FI 15–40%, …). Compliance is measured against them.

**Service model.** `DISCRETIONARY` | `ADVISORY` | `CUSTODY`. **Custody accounts are not measured
by mandate bands** — which is why Hartono's 41.42% Bara position appears on no report. That gap
is the finding, not a bug.

**Suitability verdict.** `consistent` | `conflicts_with_stated_objective` | `outside_mandate` |
`insufficient_data`, plus per-check results.

**`not_measured`.** A check result distinct from both pass and fail: no limit applies, so nothing
was ever tested. Must look different from pass and fail in the UI — it *is* the finding.

**FCN — Fixed Coupon Note.** A structured note paying a fixed coupon, with principal at risk
against underlyings. SYN-SP-0505, 9.20% coupon.

**Worst-of.** The note references several names and settles off whichever performs worst — so
one bad name is enough. Hartono's three legs (Bara, Pacific Orient Shipping, Global Energy
Majors) are all oil-sensitive: a three-name basket that is one factor.

**Barrier / knock-in.** The level at which a structured note's principal protection disappears.
`instruments.csv` gives none for SYN-SP-0505, so none is modelled — stated as an assumption.

**Planned cash need.** A known future outflow with a window and a likelihood. CN-001: SGD 9m
Singapore property deposit, Mar–Jun 2027, *Likely*. Any cure competes with it.

**Source of wealth.** Where the client's money came from. Treated as an exposure edge here:
wealth outside the bank is the same factor as wealth inside it.

**Beta.** Sensitivity of an instrument to a risk factor. Bara β = 0.721 to Brent — a 10% Brent
fall implies -7.21% on Bara.

**OLS through origin.** The regression used for betas, forced through zero, on four
snapshot-to-snapshot returns. Four observations is an assumption, not a risk model. Said out loud
on the card.

**Snapshot.** A dated position/price cut of the book. Every plan pins the snapshot it was
computed against (`authored.based_on_snapshot`, 2026-08-26).

**Second-order effect.** What an action *costs* or causes downstream. Schema-required on every
action — an action rendered without its cost is a bug.

---

## Screens and journeys

**Board.** Four columns: Fired / Armed and watching / Drafts awaiting you / Dismissed. Ranked by
severity then proximity. On stage for five seconds.

**Plan card.** The product. Trigger derivation, evidence chain, consequence, ranked actions,
client script, suitability, assumptions, confidence, state-dependent action bar.

**Dial.** One Brent slider, 60–120, default 101.50. Revalues the book and re-evaluates every
`WATCHING` trigger. Marked at 72.40.

| Journey | What it is | In the build? |
|---|---|---|
| **J0** | Overnight unattended scenario walk that authors drafts | Offline only — plans are pre-generated |
| **J1** | 08:40 Monday, the board | Yes, thin |
| **J2** | Review and arm a draft | Yes — the core demo |
| **J3** | The trigger fires, RM acts | Yes |
| **J4** | Meeting prep, contradiction detection | Cut |
| **J5** | The dial | Yes |

---

## Numbers worth memorising

- **78.85** — where the CF-0005 trigger actually solves.
- **79.00** — the level armed, rounded down for margin. **At 79.00 nothing fires. That is correct.**
- **72.40** — the demo dial setting. Brent on 2026-02-27, the day before the conflict; a real row
  in `market_context.csv`. Gives LTV 73.86%, cure SGD 418,143, Hartono -8.34%, Abdullah -4.27%,
  and CL-0002 **+0.65%** - the tech client gains when oil falls.
- **101.50** — Brent today (2026-08-26).
- **41.42%** — Bara as a share of Hartono's household wealth, in a custody account.
- **6.18%** — SYN-SP-0505 as a share of PF-0001, and 100% of its structured-products bucket.
- **0.721** — Bara beta to Brent.
- **70%** — CF-0005 margin-call LTV. **59.15%** today. **78.50%** at 2025-12-31 — it was already
  through the trigger once and was cured by the rally, not by a decision.
