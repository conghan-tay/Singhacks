# Verified numbers — Contingency Desk

Every figure below is recomputed from `singhacks-jb-wealth-intelligence/data/` by `verify.py`.
Re-run `python3 verify.py --write` before each rehearsal. Nothing here came from a language model.

As of snapshot **2026-08-26**. Brent USD **101.50** (pre-conflict 2026-02-27: **72.40**).

---

## ⚠️ Four corrections to `docs/contingency-desk.md`

**1. The FCN shows as 6.18% of PF-0001, not 3.6%.**
`SYN-SP-0505` is SGD 2,247,678 of PF-0001 (USD 1,662,484) = **6.18%**, and it is the *entire*
Structured Products bucket. Band is 0–15%, so it is still in band and the point survives —
but say 6.2%, and the stronger line is available: *the note is 100% of his structured
products allocation, and one third of it references the stock he already owns 41% of.*

**2. Abdullah's impact is ~USD 1.06m, not 1.8–2.5m.**
Under the same Brent-beta method used for Hartono, at Brent 79: POS −12.19%, GEM −12.53%,
APAC Shipping −8.90%, FCN −3.83%. Total **−USD 1,064,495 = −3.30%** of his wealth.
The doc's −17/−16/−12% per name implies a different (unstated) method and roughly doubles the
number. Use the smaller figure — it is the one you can defend, and his headline was never the
loss size, it is that **42.13% of a portfolio built to be uncorrelated with his shipping
business is the same trade as his shipping business**.

**3. Dial to 78, not 79.** The trigger solves at Brent **78.85**. At exactly 79.00, CF-0005
sits at 69.92% against a 70% trigger — it does *not* fire. Arm the plan at "Brent < 79",
turn the dial to **78**.

**4. Bara's beta is 0.721, not 0.73.** OLS through the origin on four snapshot returns
(R² 0.99) rather than the single Feb→Mar interval. Same conclusion, better provenance.

---

## The trigger, derived

| Step | Value |
|---|---|
| CF-0005 drawn | SGD 8,000,000 |
| Margin-call LTV | 70.0% |
| Required lending value | 8,000,000 / 0.70 = **SGD 11,428,571** |
| Lending value today | SGD 13,525,392 |
| Collateral pool must fall | **−15.50%** |
| Pool: Bara 29,000,000 sh @ IDR 11,340 | SGD 26,077,344 @ 50% advance = SGD 13,038,672 |
| Pool: USD Call Deposit | SGD 540,800 @ 90% advance = SGD 486,720 |
| Bara beta to Brent | **0.721** (R² 0.99) |
| **Brent trigger** | **USD 78.85** |

Brent was **72.40** before the conflict and **69.00** at the start of the year.
**78.85 is above both.** This does not need a crisis. It needs the crisis to end.

### CF-0005 history — the breach that cured itself

| Date | Drawn (SGD) | Lending value | LTV |
|---|---:|---:|---:|
| 2025-12-31 | 8,000,000 | 10,191,000 | **78.50%** ← already through the 70% trigger |
| 2026-02-27 | 8,000,000 | 10,571,380 | 75.68% |
| 2026-03-31 | 8,000,000 | 13,591,166 | 58.86% |
| 2026-06-30 | 8,000,000 | 12,866,020 | 62.18% |
| 2026-08-26 | 8,000,000 | 13,525,392 | 59.15% |

Cured by the energy rally, not by an action. Nobody decided anything.

---

## Brent level that breaks every facility in the book

| Facility | Client | LTV now | Trigger | Collateral move needed | Brent level |
|---|---|---:|---:|---:|---|
| CF-0005 | CL-0001 Hartono | 59.15% | 70% | −15.50% | **falls to 78.85** |
| CF-0002 | CL-0014 Lau | 69.41% | 70% | −0.85% | rises to 106.46 |
| CF-0001 | CL-0002 Ravi | 73.71% | 75% | −1.73% | rises to 128.67 |
| CF-0004 | CL-0011 | 32.29% | 80% | −59.64% | — |
| CF-0003 | CL-0013 | 20.39% | 75% | −72.82% | — |

Lau and Ravi are the *tight* facilities on paper — 0.59 and 1.29 points of headroom — and both
are hurt by Brent going **up**. Hartono has 10.85 points of headroom and is the one who breaks
first, because he breaks in the opposite direction. That is the whole argument for look-through
in one table, and it is Q&A gold.

---

## Dial: Brent 101.50 → 79.00 (−22.17%)

| Client | Household | Δ USD | Δ % |
|---|---:|---:|---:|
| CL-0001 Hartono | 46,571,821 | **−3,004,373** | −6.45% |
| CL-0019 Abdullah | 32,214,266 | **−1,064,495** | −3.30% |
| CL-0002 Ravi | 46,699,200 | +234,955 | +0.50% |

Hartono: Bara −15.98% = **−USD 3,081,537** on one name.
Abdullah: POS −448,158 · GEM −360,710 · APAC Shipping −254,767 · FCN −159,004.
Ravi *gains* — the technology complex has a mildly negative beta to Brent. Use this: the book is
not one-directional, so a single scenario genuinely re-ranks who she calls first.

Facilities at Brent 78: CF-0005 crosses 70%. Everything else improves.

---

## Dial: Brent 101.50 → 72.40 — the demo setting

72.40 is the Brent price on **2026-02-27**, the day before the conflict. It is a row in
`market_context.csv`, not a number we chose.

| | |
|---|---:|
| CF-0005 LTV | **73.86%** against a 70% trigger — **BREACH** |
| Lending value | SGD 10,831,225 |
| Cure required | SGD 418,143 cash, or SGD 1,194,693 of additional Bara collateral |
| CL-0001 Hartono | -3,885,656 USD (-8.34%) |
| CL-0019 Abdullah | -1,376,747 USD (-4.27%) |
| CL-0002 Ravi | +303,876 USD (+0.65%) |

These supersede any earlier 72.40 figures quoted in conversation: the household deltas here
revalue **every** position at its own beta, including the diversified funds with small negative
betas that partly offset the concentrated names. Ravi gains.

---

## Household concentration

**CL-0001 Hartono Wijaya Kusuma** — USD 46,571,821, age 34, Balanced Growth, risk tolerance 6,
tax domicile Indonesia.

| | |
|---|---|
| Bara Nusantara Energy Tbk, PF-0002 (Custody) | USD 19,287,977 = **41.42% of household** |
| PF-0001 mandate report | Equity 50.14% (40–65), FI 25.17% (15–40), Alt 7.19% (0–25), Comm 6.35% (0–10), **SP 6.18% (0–15)**, Cash 4.95% (2–15) |
| Every band | **in band** |

The mandate report is clean. It is clean because PF-0002 is a custody account and mandates do not
measure custody accounts.

**CL-0019 Abdullah Al-Mansoori** — USD 32,214,266, age 49, Balanced Growth, tolerance 6, UAE.

| Holding | USD | % |
|---|---:|---:|
| SYN-SP-0505 FCN (worst-of POS / GEM / Bara) | 4,156,210 | 12.90% |
| SYN-ST-0104 Pacific Orient Shipping — *also a worst-of leg* | 3,676,056 | 11.41% |
| SYN-EQ-0008 Global Energy Majors — *also a worst-of leg* | 2,878,800 | 8.94% |
| SYN-EQ-0025 Asia Pacific Shipping and Logistics | 2,862,200 | 8.88% |
| **Block** | **13,573,266** | **42.13%** |

Stated objective: *"Build wealth outside the Gulf region and outside the shipping sector."*

**SYN-SP-0505 is held by exactly two clients in the book: CL-0001 and CL-0019.** One dial turn.

---

## Quotes, verified verbatim from `rm_notes.json`

- **Hartono, 2026-01-08** — *"He was clear that the Julius Baer relationship is meant to be the
  part of the family's wealth that is not tied to the mine. Did not want to discuss reducing the
  legacy shareholding, said it would be read as a signal by his uncles."*
- **Hartono, 2026-04-14** — *"Asked what products give him more of that. Discussed the shipping
  and energy FCN, he subscribed the following day… expects to need around SGD 9m for the deposit
  in early 2027."*
- **Abdullah, 2026-04-15** — *"He said the point of the Asia portfolio was to be uncorrelated
  with the Gulf business. It currently is not."*
- **Abdullah, 2026-08-12** — *"He asked for a view on what happens to his portfolio if the Strait
  reopens and normalises. **We have not modelled this.**"*
- **Ravi, 2026-06-11** — *"I flagged that this increases his utilisation at exactly the moment his
  collateral is most volatile. He acknowledged the point but proceeded."*

Planned cash needs: **CN-001** CL-0001 SGD 9,000,000, 2027-03-01 → 2027-06-30, *Likely*.
**CN-017** CL-0019 USD 5,000,000, 2027-01-01 → 2027-12-31, *Likely*.

---

## Assumptions to put on screen

1. **Single factor.** Everything is one Brent shock. Betas are OLS through the origin on four
   snapshot-to-snapshot returns. Four observations is not a risk model — it is a stated,
   inspectable assumption, and the UI shows the beta and the R² on every hop.
2. **FX held constant at 2026-08-26.** A Brent fall would plausibly move USDIDR, which moves the
   SGD value of Bara collateral. Not modelled. Name it before a judge does.
3. **No barrier.** `instruments.csv` gives no barrier or strike for SYN-SP-0505, so no knock-in is
   modelled and none is invented. The FCN moves at its measured beta only. The real point is
   qualitative: all three worst-of legs are the same trade.
4. **Private valuations lag a quarter.** Untouched — that is how the industry works.
5. **Gulf logistics proxy is low-confidence.** Abdullah's operating-business factor is proxied by
   listed shipping. Flagged as RM-authored, low confidence, on screen.

---

## Ravi — hold in reserve for Q&A

CF-0001 breached at 2026-06-30: LTV **75.64%** against a 75.0% trigger.
Lending value *rose* that quarter, 7,782,285 → 8,593,650. The breach was caused entirely by the
USD 1.7m drawdown on 11 June. Without it: 4,800,000 / 8,593,650 = **55.86%**.

Not a market forecast — pre-trade arithmetic. The system fires when the draw is *requested*.
He also holds Helios Cloud twice: `SYN-ST-0103` direct and `SYN-SP-0502` (ELN, single underlying
Helios). Same look-through pattern, technology instead of energy.

Also in reserve: **CL-0014 Lau Chi Ming**, CF-0002 at 69.41% against a 70% trigger — 0.59 points.
