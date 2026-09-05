# The Contingency Desk

> Priscilla's problem is not information. It is latency. A trading desk does not work out what
> an event means after it happens — it writes the plan before, and executes on the trigger.
> This is that, for a private banking book.

**Product**: per client, a book of *armed contingency plans*. Each plan is a trigger condition on an
observable variable, the consequence traced through that client's actual positions and look-through
exposures, a ranked action set, and a client-ready script — authored by an agent, reviewed and
**armed by the RM before the event**, watched continuously, fired the moment the trigger hits.

The arming step is the governance artefact. The reasoning was reviewed by a human *before* the
market moved, so no post-hoc rationalisation is available to it.

---

## 1. The three clients

All figures at snapshot `2026-08-26` unless stated. Verified against the dataset.

### CL-0001 Hartono Wijaya Kusuma — the look-through showpiece

USD 46.57m across **two** portfolios. The mandate report shows a tidy Balanced Growth book.
The household view shows one bet, five layers deep:

| Layer | Exposure |
|---|---|
| Source of wealth | Family coal mining and energy group (Indonesia) |
| Custody `PF-0002` | Bara Nusantara Energy Tbk, USD 19.29m = **41.4% of total wealth** |
| Mandate `PF-0001` | `SYN-SP-0505` FCN, worst-of basket = Pacific Orient Shipping / Global Energy Majors ADR / **Bara Nusantara Energy** |
| Collateral `CF-0005` | SGD 8.0m drawn against `PF-0002` — i.e. against the Bara stake |
| Cash need `CN-001` | SGD 9.0m property deposit, Mar–Jun 2027 |

`PF-0002` is a **custody** account, so it is excluded from mandate measurement. The 41.4% never
appears on the mandate report. The FCN references the same name and does appear — as
"Structured Products, 3.6%".

`CF-0005` history: LTV **78.5%** at 2025-12-31 against a **70% trigger**. Cured by the energy
rally, not by an action. Today 59.15%.

RM notes: 2026-01-08 refused to discuss reducing the legacy shareholding ("would be read as a
signal by my uncles"). 2026-04-14 called about the energy rally, asked what gives him *more* of
it, subscribed the FCN the following day.

### CL-0019 Abdullah Al-Mansoori — the scenario client

USD 32.21m, single portfolio `PF-0023`.

| Holding | Weight |
|---|---|
| `SYN-SP-0505` FCN (worst-of POS / GEM ADR / Bara) | 12.9% |
| Pacific Orient Shipping Ltd — **also a worst-of leg** | 11.4% |
| Global Energy Majors Equity Fund — **also a worst-of leg** | 8.9% |
| Asia Pacific Shipping and Logistics Fund | 8.9% |
| | **42.1%** |

Operating business: Gulf logistics, port services and marine chartering.
Stated objective: *"Build wealth outside the Gulf region and outside the shipping sector."*

RM note 2026-04-15: *"He said the point of the Asia portfolio was to be uncorrelated with the Gulf
business. It currently is not."*
RM note 2026-08-12: *"He asked for a view on what happens to his portfolio if the Strait reopens
and normalises. **We have not modelled this.**"*

He and Hartono hold the same note. One dial turn fires plans on both.

### CL-0002 Ravi Chandrasekaran — the backtest

`CF-0001`, USD Lombard against `PF-0003`, margin-call trigger **75.0%**.

| Date | Drawn | Lending value | LTV |
|---|---|---|---|
| 2026-03-31 | 4,800,000 | 7,782,285 | 61.68% |
| 2026-06-30 | 6,500,000 | 8,593,650 | **75.64% — BREACH** |
| 2026-08-26 | 6,500,000 | 8,818,810 | 73.71% |

**Lending value rose over that quarter.** The breach was not caused by the market — it was caused
entirely by the USD 1.7m draw. Without it, LTV would have been 55.86%.

RM note 2026-06-11: *"Drew a further USD 1.7m to fund a pre-IPO secondary. I flagged that this
increases his utilisation at exactly the moment his collateral is most volatile. He acknowledged
the point but proceeded."*

So this is not a market-forecast alert. It is **pre-trade arithmetic**: the system fires at the
moment the draw is requested, and says "this puts you at 75.6% against a 75% trigger." Unarguable.

He also holds Helios Cloud twice — `SYN-ST-0103` directly and `SYN-SP-0502` (ELN, single
underlying Helios). Same look-through pattern, tech instead of energy.

---

## 2. Scenario calibration — "the Strait reopens"

State the beta as an assumption on screen. Do not present it as a forecast.

Brent: 72.40 pre-conflict (2026-02-27) → 101.50 today.
Bara Nusantara: 8,720 → 11,340 (+30.0%).
Feb→Mar: Brent +43.6%, Bara +31.7% ⇒ **beta ≈ 0.73**.

### The exact trigger for CF-0005

Collateral `PF-0002`: Bara SGD 26,077,344 @ 50% advance + USD deposit SGD 540,800 @ 90%
= lending value SGD 13,525,392. Drawn SGD 8,000,000 ⇒ LTV 59.15%.

Margin call at 70% ⇒ required lending value = 8,000,000 / 0.70 = 11,428,571
⇒ Bara lending value = 10,941,851 ⇒ Bara market value = SGD 21,883,703
⇒ **Bara −16.08%** ⇒ at beta 0.73, **Brent ≈ USD 79.1**.

> **Plan trigger: Brent < USD 79 → CF-0005 margin call.**
> Brent was 72.40 before the conflict. This is not a tail scenario. It is the *good* scenario.

That is the whole product in one line: the RM's client is one de-escalation away from a margin
call, and nothing on his report says so.

### Second-order, same trigger, same client

- Direct Bara position −16% ≈ **−USD 3.1m**, 6.6% of total wealth, one name, one move.
- `SYN-SP-0505` worst-of: **all three legs are the same trade, and that trade is the Strait.**
  The note's diversification is nominal — a single-factor bet dressed as a three-name basket.
  *(The dataset does not give a barrier level. Do not invent one. Say the above instead — it is
  the stronger point and it is defensible.)*
- `CN-001`: SGD 9m deposit due Mar–Jun 2027 must then come from the diversified mandate,
  leaving him more concentrated, not less.

### Abdullah, same trigger

Reverting ~70% of the post-conflict gains: POS −17%, GEM fund −16%, APAC Shipping fund −12%,
plus the note. Roughly **−USD 1.8m to 2.5m on the identified 42% block**, at the same moment
charter rates normalise against his operating business. State it as a range with the assumption
visible.

---

## 3. Data model

Look-through is **seeded reference data, not an engine**. This is how a bank actually does it —
product control maintains the mapping. Say so in the pitch; it is the answer to "could this
operate inside a regulated bank."

```
risk_factors        ~15 rows
  risk_factor_id, name, category
  e.g. BARA, PACIFIC_ORIENT_SHIPPING, GLOBAL_ENERGY_MAJORS, HELIOS_CLOUD,
       GOLDEN_HARBOUR, XAU, HK_RESIDENTIAL, US_LONG_DURATION, USD_FUNDING,
       GREATER_CHINA_LUXURY, BRENT, INDONESIAN_COAL

exposure_edges      ~100 rows, hand-seeded
  source_type   direct | fund_sector | structured_underlying | source_of_wealth | collateral
  source_id     instrument_id or client_id
  risk_factor_id
  weight        0..1
  provenance    'instruments.underlying_reference' | 'clients.source_of_wealth' | RM-authored

plans
  plan_id, client_id, state, trigger_expr, projected_consequence,
  actions[], client_script, suitability_verdict,
  armed_by, armed_at, armed_signature, superseded_by
```

Plan state machine — **one long-running Temporal workflow per plan**:

```
DRAFTED ──► ARMED ──► WATCHING ──► FIRED ──► ACTIONED | DISMISSED
              ▲          │
              └── STALE ◄┘   (world moved differently from the armed assumption)
```

`ARMED` and `ACTIONED` are both `interrupt()`. This is your existing template with the domain
swapped — you are not inventing architecture.

### Deterministic vs LLM

| Deterministic (no model) | LLM |
|---|---|
| Exposure aggregation across portfolios | Drafting plans from client context |
| LTV, lending value, advance-rate haircuts | Proposing new exposure edges from `underlying_reference` free text, **for human review** |
| Trigger evaluation | Narrating the deterministic chain into what Priscilla says out loud |
| Mandate band and concentration checks | Detecting where `rm_notes` contradict the numbers |
| Liquidity coverage vs `planned_cash_needs` | Critiquing a proposed action against mandate, risk profile, objectives |

**A trigger is never evaluated by a model.** Put that sentence on a slide.

---

## 4. The journeys

Six journeys. J1–J3 are the loop; J0 feeds it; J4 and J5 are views over the same engine.
Priscilla Ong, RM, Asia desk, 20 clients, meetings over the next fortnight. Today is 2026-08-26.

### J0 — Overnight, unattended: the war-game

*Actor: the agent. Trigger: schedule.*

Walks the scenario set across the whole book — Hormuz reopens / escalates further / Fed hikes /
tech drawdown repeats / HK property leg down 15% — computing consequence through
`exposure_edges` for every client. Wherever the consequence is material against that client's
mandate bands, stated objectives or `planned_cash_needs`, it drafts a plan: trigger expression,
projected consequence, ranked actions, client script, suitability verdict.

Drafts land in Priscilla's queue at state `DRAFTED`. Nothing is armed. Nothing is sent.

This is where the intelligence lives, and it runs while she sleeps. It is also the honest answer
to "where is the AI" — the model authors and argues; it never evaluates a trigger and never acts.

> Rubric: proactive detection, event-driven idea generation.

### J1 — 08:40 Monday: the board

*Actor: Priscilla. Trigger: she opens the app. Duration: ten minutes.*

Not charts. Four columns:

| Column | Meaning |
|---|---|
| **Fired** | Trigger hit since she last looked. Needs a decision. |
| **Armed and watching** | Live. She signed these. Shown with current distance to trigger. |
| **Drafts awaiting you** | J0's overnight output. Needs review. |
| **Stale** | Armed, but the world moved off the assumption. Needs re-authoring. |

Ranked by `severity × proximity to trigger × client consequence`, each factor clickable down to
the arithmetic that produced it. This is the answer to *"twenty clients, one RM — who does she
call first, and can you defend the ranking?"* The defence is that the ranking is arithmetic, not
an LLM opinion, and every term opens.

> Rubric: prioritisation across the book, defensible ranking.

### J2 — Reviewing and arming a draft

*Actor: Priscilla. The core human-in-the-loop journey. Demo this one slowly.*

A plan card opens to six things:

1. **Trigger** — `Brent < USD 79`, with the derivation shown (see §2), not asserted.
2. **Evidence chain**, rendered as the actual path through the data:
   `Indonesian coal (source_of_wealth) → Bara 41.4% direct in PF-0002 (custody, off-mandate)
   → worst-of leg of SYN-SP-0505 in PF-0001 → collateral for CF-0005 → funds CN-001`
   Every hop is a row in `exposure_edges` with its `provenance` field visible.
3. **Projected consequence** — the LTV arithmetic, the position impact, the funding gap.
4. **Ranked actions**, each with its second-order effect stated.
5. **Draft client script** — what she actually says to Hartono.
6. **Suitability verdict** against the Balanced Growth mandate, risk tolerance 6, and his stated
   objective "diversify away from the family operating business."

She can move the trigger level, delete an action, rewrite a line of the script, or reject with a
reason. Rejections with reasons feed back as authoring signal.

Arming writes a **signed, timestamped record**: who approved what reasoning, against which data,
at which time — *before the event*. That record is the single most valuable artefact in the
product. A post-hoc AI explanation can always be accused of rationalising an outcome it already
knew. This one cannot: it predates the outcome.

> Rubric: explainability, traceability, suitability, human oversight. This journey alone touches
> four of the six governance criteria.

### J3 — The trigger fires

*Actor: monitor, then Priscilla. Trigger: market state crosses the armed condition.*

The plan's Temporal workflow wakes on signal and transitions `WATCHING → FIRED`. Priscilla is
notified. She opens it and **the work is already done, because she wrote it last week** — that is
the entire product thesis in one interaction.

The card shows current numbers **against what was projected at arming time**, so she can see
whether the world behaved as the plan assumed. She picks an action and approves; that is the
second `interrupt()`, and it is what actually executes.

Build the honest failure case too. If the trigger fired but the underlying assumption has
drifted — Brent fell below 79 but for a demand reason rather than a supply reason, so the Bara
beta no longer holds — the system says **assumption drifted**, refuses to present the pre-written
action as still valid, and asks her to re-author. A plan that fires into changed conditions is
worse than no plan, because she trusts it.

> Rubric: *"'We are not sure, and here is what we would check' beats a confident answer the data
> does not support. Confident fabrication scores badly."* This is that, built in.

### J4 — Meeting prep

*Actor: Priscilla. Trigger: a meeting in the next fortnight.*

Pull one client, get the pack: what is armed for them, what fired since last contact, the
household exposure picture, the **contradictions between what they have said and what they
hold**, and the questions they are likely to ask.

The contradiction detector is the LLM doing something only an LLM can do — reading `rm_notes`
against computed state:

- Abdullah: *"the point of the Asia portfolio was to be uncorrelated with the Gulf business"* vs
  42.1% in shipping and energy, two of the names doubled through a worst-of note.
- Hartono: *"the Julius Baer relationship is meant to be the part of the family's wealth that is
  not tied to the mine"* vs 41.4% of that wealth in Bara, financed by SGD 8m drawn against it.
- Ravi: acknowledged the collateral point on 11 June and drew anyway, six days before it breached.

Abdullah's demo writes itself. His note of 2026-08-12 ends *"We have not modelled this."*
She walks in with it modelled.

> Rubric: RM–client conversation quality, client-centric innovation.

### J5 — The dial

*Actor: Priscilla, or a judge. Trigger: manual.*

Interactive scenario across the whole book. A scenario is just a shock vector over
`risk_factors`, so this reuses the J0 engine with a human turning the knob instead of a cron.

Set it to "Strait reopens, Brent to 78" and four plans fire on Hartono at once — the note's three
worst-of legs are all the same trade and all move together, the 41.4% direct position falls, and
CF-0005 crosses its 70% trigger — while Abdullah's 42.1% shipping-and-energy block falls at the
same moment charter rates normalise against the business that funds him.

Two clients, one instrument, one dial turn, opposite stated intentions, identical exposure.

> Rubric: scenario analysis, and the demo moment that makes the rest legible.

---

## 5. Demo script — J1 → J2 → J5 → J3

Chronological. It makes the human-in-the-loop step impossible to miss.

**J1 — Monday 08:40, the board.** Four columns: Fired / Armed and watching / Drafts awaiting you /
Stale. Ranked by severity × proximity to trigger × client consequence, every component clickable.
Ten seconds on screen. *"Twenty clients, one RM. This is the ranking, and every part of it is
arithmetic you can open."*

**J2 — Arming a plan (slow down here).** Open Hartono's draft. Show:
- trigger `Brent < 79`
- the evidence chain rendered as a path:
  `Indonesian coal (source of wealth) → Bara 41.4% direct in PF-0002 (custody, off-mandate)
   → worst-of leg of SYN-SP-0505 in PF-0001 → collateral for CF-0005 → funds CN-001`
- projected consequence with the LTV arithmetic
- ranked actions and the draft client script
- suitability verdict against the Balanced Growth mandate and his stated objective
  ("diversify away from the family operating business")

Priscilla edits the trigger from 79 to 82, deletes one action, rewrites a line of the script, arms
it. Signed, timestamped. **Say out loud: this happened before the event.**

**J5 — The dial.** "Strait reopens, Brent to 78." Turn it.

**J3 — Fire.** Plans fire across Hartono and Abdullah simultaneously. Hartono's card opens with
the work already done because Priscilla wrote it last week — current numbers shown against what
was projected at arming time. She picks an action and approves.

Then show the honest case: one plan fires but flags **assumption drifted** — the world moved
differently from what she armed against, so the system refuses to pretend the plan still applies
and asks her to re-author. *"We are not sure, and here is what we would check"* beats a confident
answer the data does not support — that is in the rubric.

Close on Abdullah's RM note, 2026-08-12: *"We have not modelled this."* Now it is modelled.

---

## 6. Build order and cut lines

1. `risk_factors` + `exposure_edges` seed data, and the deterministic exposure/LTV engine. **Nothing works without this.**
2. Plan schema + Temporal workflow with `ARMED` and `ACTIONED` interrupts.
3. J2 plan card (authoring + arming + evidence chain rendering) — the rubric lives here.
4. J3 fire path + the assumption-drift check.
5. J1 board as a shell over what exists.
6. J5 dial — a scenario is just a shock vector over `risk_factors`; reuse the engine.
7. J0 nightly war-game = J5 on a schedule, writing drafts. **First cut line — mock it if time is short.**

Cut, in this order, if the clock runs out: J0, then J4 meeting prep, then the assumption-drift
case, then J1's ranking weights become fixed instead of tunable. **Never cut J2's evidence chain
or the arming signature** — that is the entire governance argument.

Hold Lau Chi Ming (CL-0014, LTV 69.41% vs 70% trigger, HKD 60m due mid-2027, accumulator struck
on the same name as his own collateral) in reserve for judges' questions. Do not put him in the
demo.
