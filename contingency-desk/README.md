# Contingency Desk — build packet

Deterministic layer and delegation contract for the SingHacks Julius Baer challenge.
The MySingHacks repo is not on the demo path.

| Path | What it is |
|---|---|
| `verify.py` | Recomputes every on-screen number from the challenge CSVs. `python3 verify.py --write` |
| `out/verified_numbers.md` | Pitch-facing fact sheet, corrections to the design doc, assumptions to show on screen |
| `out/facts.json` | Machine-readable engine output — households, betas, facility trigger solves, scenario |
| `seed/` | 12 risk factors, 21 exposure edges. Look-through as reference data with per-edge provenance |
| `schema/plan.schema.json` | The plan contract. `trigger.evaluated_by` is a constant: `"deterministic"` |
| `schema/state_machine.md` | DRAFTED → ARMED → WATCHING → FIRED → ACTIONED \| DISMISSED. No STALE |
| `plans/PLAN-001..003.json` | The three drafted plans. Numbers computed, prose hand-written |
| `engine.py` | Deterministic engine: `shock`, `evaluate_trigger`. Arithmetic only. `python3 engine.py` demos it |
| `store.py` | Plan state machine and the arming signature. `python3 store.py` walks DRAFTED → ACTIONED |
| `tests/` | 37 assertions pinning the numbers, the plans, the engine and the state machine |
| `docs/design.md` | Colour tokens, type scale, card anatomy, worked evidence-chain HTML/CSS |
| `docs/architecture.md` | Demo architecture + production shape, for the feasibility slide |
| `docs/sequence.md` | Arm → watch → fire, the dial, and why the signature matters |
| `AGENT_BRIEF.md` | Hand this to the UI agent verbatim |

```bash
pip3 install --break-system-packages pytest jsonschema pandas
python3 verify.py --write && python3 seed/build_seed.py && python3 plans/build_plans.py
python3 -m pytest tests/ -q
```

**Demo dial goes to 72.40**, the Brent level the day before the conflict — a real row in
`market_context.csv`. At 79.00 the facility does not breach.
