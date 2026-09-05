#!/usr/bin/env python3
"""Contingency Desk - deterministic verification pass.

Recomputes every number that appears on screen or in the pitch, straight from
data/. Nothing here is an LLM output. Run before every rehearsal.

    python3 verify.py            # prints the report
    python3 verify.py --write    # also writes out/facts.json + out/verified_numbers.md
"""
import os, sys, json, datetime
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("SINGHACKS_DATA") or os.path.join(
    os.path.dirname(HERE), "singhacks-jb-wealth-intelligence", "data")
if not os.path.isdir(DATA):
    sys.exit(f"challenge data not found at {DATA} - set SINGHACKS_DATA to override")
SNAPS = ["2025-12-31", "2026-02-27", "2026-03-31", "2026-06-30", "2026-08-26"]
T = "2026-08-26"

cl  = pd.read_csv(f"{DATA}/clients.csv")
pf  = pd.read_csv(f"{DATA}/portfolios.csv")
hd  = pd.read_csv(f"{DATA}/holdings.csv")
ins = pd.read_csv(f"{DATA}/instruments.csv")
cf  = pd.read_csv(f"{DATA}/credit_facilities.csv")
mc  = pd.read_csv(f"{DATA}/market_context.csv")
pcn = pd.read_csv(f"{DATA}/planned_cash_needs.csv")
mnd = pd.read_csv(f"{DATA}/mandates.csv")

facts = {"generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
         "as_of": T, "assumptions": {}, "clients": {}, "facilities": {}, "betas": {}}
lines = []
def out(s=""):
    lines.append(s); print(s)

# ---------------------------------------------------------------- market
brent = mc[mc.series_id == "BRENT_USD_BBL"].set_index("snapshot_date").value
B0 = float(brent[T])
facts["market"] = {"brent": {d: float(brent[d]) for d in SNAPS}}

out("=" * 78)
out("BRENT USD/bbl        " + "  ".join(f"{d[5:]}={brent[d]:>6.2f}" for d in SNAPS))
out(f"  pre-conflict (2026-02-27) = {brent['2026-02-27']:.2f}   today = {B0:.2f}")

# ---------------------------------------------------------------- betas to Brent
# OLS through the origin on the four snapshot-to-snapshot returns.
# One factor, four observations. Stated as an assumption, never as a forecast.
bx = [float(brent[SNAPS[i+1]]) / float(brent[SNAPS[i]]) - 1 for i in range(4)]

def beta_to_brent(instrument_id):
    r = ins[ins.instrument_id == instrument_id]
    if r.empty:
        return None
    p = [float(r.iloc[0][f"price_{d}"]) for d in SNAPS]
    y = [p[i+1] / p[i] - 1 for i in range(4)]
    num = sum(a * b for a, b in zip(bx, y)); den = sum(a * a for a in bx)
    if den == 0:
        return None
    b = num / den
    ybar = sum(y) / len(y)
    ss_res = sum((yi - b * xi) ** 2 for xi, yi in zip(bx, y))
    ss_tot = sum((yi - ybar) ** 2 for yi in y)
    r2 = 1 - ss_res / ss_tot if ss_tot else float("nan")
    return {"beta": b, "r2": r2}

WATCH = ["SYN-ST-0101", "SYN-ST-0104", "SYN-EQ-0008", "SYN-EQ-0025",
         "SYN-SP-0505", "SYN-ST-0103", "SYN-SP-0502"]
out()
out("BRENT BETAS  (OLS through origin, 4 snapshot returns; single factor)")
for i in WATCH:
    b = beta_to_brent(i)
    nm = ins[ins.instrument_id == i].iloc[0].instrument_name[:46]
    facts["betas"][i] = b
    out(f"  {i}  beta={b['beta']:+.3f}  r2={b['r2']:.2f}   {nm}")

# ---------------------------------------------------------------- households
def household(cid):
    h = hd[(hd.client_id == cid) & (hd.snapshot_date == T)]
    tot = float(h.market_value_usd.sum())
    g = (h.groupby(["instrument_id", "instrument_name", "portfolio_id"], as_index=False)
           .market_value_usd.sum().sort_values("market_value_usd", ascending=False))
    g["pct"] = 100 * g.market_value_usd / tot
    return tot, g

for cid in ["CL-0001", "CL-0019", "CL-0002"]:
    c = cl[cl.client_id == cid].iloc[0]
    tot, g = household(cid)
    facts["clients"][cid] = {
        "name": c.client_name, "age": int(c.age), "risk_profile": c.risk_profile,
        "risk_tolerance": int(c.risk_tolerance_score), "tax_domicile": c.tax_domicile,
        "source_of_wealth": c.source_of_wealth, "objectives": c.objectives,
        "household_usd": tot,
        "top": [{"instrument_id": r.instrument_id, "name": r.instrument_name,
                 "portfolio_id": r.portfolio_id, "usd": float(r.market_value_usd),
                 "pct_household": float(r.pct)} for r in g.head(6).itertuples()],
    }
    out()
    out("=" * 78)
    out(f"{cid}  {c.client_name}   household USD {tot:,.0f}   ({c.risk_profile}, tol {c.risk_tolerance_score})")
    for r in g.head(5).itertuples():
        out(f"   {r.pct:5.2f}%  {r.portfolio_id}  {r.instrument_name[:44]:46s} USD {r.market_value_usd:>12,.0f}")

# Abdullah's identified block
blk = ["SYN-SP-0505", "SYN-ST-0104", "SYN-EQ-0008", "SYN-EQ-0025"]
h19 = hd[(hd.client_id == "CL-0019") & (hd.snapshot_date == T)]
tot19 = float(h19.market_value_usd.sum())
blk_usd = float(h19[h19.instrument_id.isin(blk)].market_value_usd.sum())
facts["clients"]["CL-0019"]["shipping_energy_block"] = {
    "instruments": blk, "usd": blk_usd, "pct": 100 * blk_usd / tot19}
out(f"   -> shipping+energy block {', '.join(blk)} = USD {blk_usd:,.0f} = {100*blk_usd/tot19:.2f}%")

# ---------------------------------------------------------------- facilities
def facility_row(fid):
    r = cf[cf.facility_id == fid].iloc[0]
    hist = [{"date": d, "drawn": float(r[f"drawn_{d}"]),
             "collateral_mv": float(r[f"collateral_market_value_{d}"]),
             "lending_value": float(r[f"lending_value_{d}"]),
             "ltv": float(r[f"ltv_pct_{d}"])} for d in SNAPS]
    return r, hist

def brent_trigger(fid):
    """Brent level at which this facility's LTV reaches its margin-call trigger.
    Linear in Brent: LV(B) = LV0 + C * (B/B0 - 1), C = sum(lending_value_i * beta_i)."""
    r, hist = facility_row(fid)
    port = r.collateral_portfolio_id
    pool = hd[(hd.portfolio_id == port) & (hd.snapshot_date == T)]
    LV0 = float(pool.lending_value_base.sum())
    drawn = float(r[f"drawn_{T}"]); trig = float(r.margin_call_ltv_pct) / 100
    C = 0.0; legs = []
    for x in pool.itertuples():
        b = beta_to_brent(x.instrument_id)
        beta = b["beta"] if b else 0.0
        C += float(x.lending_value_base) * beta
        legs.append({"instrument_id": x.instrument_id, "name": x.instrument_name,
                     "mv_base": float(x.market_value_base),
                     "advance_rate": float(x.advance_rate_pct),
                     "lending_value": float(x.lending_value_base), "beta": beta})
    LV_target = drawn / trig
    B_trig = B0 * (1 + (LV_target - LV0) / C) if C else None
    return {"facility_id": fid, "client_id": r.client_id, "portfolio": port,
            "ccy": r.facility_ccy, "drawn": drawn, "lending_value": LV0,
            "ltv_now": float(r[f"ltv_pct_{T}"]), "trigger_ltv": float(r.margin_call_ltv_pct),
            "lending_value_at_trigger": LV_target, "C": C, "brent_trigger": B_trig,
            "collateral_move_required": LV_target / LV0 - 1, "legs": legs, "history": hist}

out()
out("=" * 78)
out("FACILITIES — Brent level that puts each facility on margin call")
out("  (single-factor Brent shock, betas above, FX held constant)")
for fid in cf.facility_id:
    t = brent_trigger(fid)
    facts["facilities"][fid] = t
    bt = f"{t['brent_trigger']:.2f}" if t["brent_trigger"] else "n/a"
    direction = "fall to" if (t["brent_trigger"] or 0) < B0 else "rise to"
    out(f"  {fid} {t['client_id']}  LTV {t['ltv_now']:5.2f}% vs {t['trigger_ltv']:.0f}%  "
        f"collateral must move {100*t['collateral_move_required']:+6.2f}%  ->  Brent {direction} {bt}")

# ---------------------------------------------------------------- the demo trigger
cf5 = facts["facilities"]["CF-0005"]
out()
out("-" * 78)
out("CF-0005 (Hartono) — the demo trigger, derived not asserted")
r5, hist5 = facility_row("CF-0005")
for hgt in hist5:
    out(f"   {hgt['date']}  drawn SGD {hgt['drawn']:>11,.0f}   LV {hgt['lending_value']:>12,.0f}   LTV {hgt['ltv']:6.2f}%")
out(f"   required lending value at 70%      = {cf5['drawn']:,.0f} / 0.70 = SGD {cf5['lending_value_at_trigger']:,.0f}")
out(f"   today's lending value              = SGD {cf5['lending_value']:,.0f}")
out(f"   collateral pool must fall          = {100*cf5['collateral_move_required']:.2f}%")
out(f"   Bara beta to Brent                 = {facts['betas']['SYN-ST-0101']['beta']:.3f}")
out(f"   => BRENT TRIGGER                   = USD {cf5['brent_trigger']:.2f}   (today {B0:.2f}, pre-conflict {brent['2026-02-27']:.2f})")
out(f"   Brent {cf5['brent_trigger']:.0f} is ABOVE the pre-conflict level. This is not a tail. It is the good scenario.")

# ---------------------------------------------------------------- shock engine
def shock(brent_level, client_ids=("CL-0001", "CL-0019", "CL-0002")):
    """Revalue holdings under a Brent level and re-test every facility trigger."""
    mult = brent_level / B0 - 1
    res = {"brent": brent_level, "clients": {}, "facilities": {}}
    for cid in client_ids:
        h = hd[(hd.client_id == cid) & (hd.snapshot_date == T)].copy()
        deltas = []
        for x in h.itertuples():
            b = beta_to_brent(x.instrument_id)
            beta = b["beta"] if b else 0.0
            d = float(x.market_value_usd) * beta * mult
            if abs(d) > 1000:
                deltas.append({"instrument_id": x.instrument_id, "name": x.instrument_name,
                               "portfolio_id": x.portfolio_id, "beta": beta,
                               "pct": 100 * beta * mult, "usd_delta": d})
        tot = float(h.market_value_usd.sum())
        res["clients"][cid] = {"household_usd": tot,
                               "usd_delta": sum(d["usd_delta"] for d in deltas),
                               "moves": sorted(deltas, key=lambda z: z["usd_delta"])}
    for fid, t in facts["facilities"].items():
        LV = t["lending_value"] + t["C"] * mult
        res["facilities"][fid] = {"lending_value": LV, "ltv": 100 * t["drawn"] / LV,
                                  "trigger": t["trigger_ltv"],
                                  "breached": (100 * t["drawn"] / LV) >= t["trigger_ltv"]}
    return res

DIAL = 79.0
s = shock(DIAL)
facts["scenario_brent_79"] = s
out()
out("=" * 78)
out(f"DIAL: Brent {B0:.2f} -> {DIAL:.2f}   ({100*(DIAL/B0-1):+.2f}%)")
for cid, v in s["clients"].items():
    nm = facts["clients"][cid]["name"]
    out(f"  {cid} {nm:26s} household {v['usd_delta']:>+14,.0f} USD  ({100*v['usd_delta']/v['household_usd']:+.2f}% of wealth)")
    for m in v["moves"][:4]:
        out(f"        {m['instrument_id']}  {m['name'][:40]:42s} {m['pct']:+7.2f}%  {m['usd_delta']:>+12,.0f}")
out("  facilities:")
for fid, v in s["facilities"].items():
    flag = "  *** MARGIN CALL ***" if v["breached"] else ""
    out(f"        {fid}  LTV {v['ltv']:6.2f}%  vs trigger {v['trigger']:.0f}%{flag}")

# ---------------------------------------------------------------- mandate optics
out()
out("=" * 78)
out("MANDATE OPTICS — what the report shows vs what the household holds")
p1 = hd[(hd.portfolio_id == "PF-0001") & (hd.snapshot_date == T)]
tot1 = float(p1.market_value_base.sum())
bands = mnd[mnd.mandate_code == "BALG"].set_index("asset_class")
for ac, v in p1.groupby("asset_class").market_value_base.sum().sort_values(ascending=False).items():
    w = 100 * v / tot1
    lo, hi = float(bands.loc[ac].min_pct), float(bands.loc[ac].max_pct)
    ok = "in band" if lo <= w <= hi else "BREACH"
    out(f"   PF-0001  {ac:22s} {w:6.2f}%   band {lo:.0f}-{hi:.0f}%   {ok}")
fcn = p1[p1.instrument_id == "SYN-SP-0505"].iloc[0]
out(f"   FCN SYN-SP-0505 shows on the mandate report as {100*float(fcn.market_value_base)/tot1:.2f}% of PF-0001 "
    f"(USD {float(fcn.market_value_usd):,.0f}) — within the 0-15% Structured Products band.")
bara = hd[(hd.client_id == "CL-0001") & (hd.snapshot_date == T) & (hd.instrument_id == "SYN-ST-0101")].iloc[0]
tot_h, _ = household("CL-0001")
out(f"   Bara SYN-ST-0101 sits in PF-0002 (Custody) = {100*float(bara.market_value_usd)/tot_h:.2f}% of household wealth, "
    f"measured by no mandate.")

# ---------------------------------------------------------------- cash needs
out()
out("PLANNED CASH NEEDS")
for r in pcn[pcn.client_id.isin(["CL-0001", "CL-0019", "CL-0002"])].itertuples():
    out(f"   {r.need_id} {r.client_id}  {r.currency} {r.amount:,.0f}  {r.due_from}..{r.due_to}  {r.certainty}  — {r.description}")
    facts["clients"].setdefault(r.client_id, {}).setdefault("cash_needs", []).append(
        {"need_id": r.need_id, "ccy": r.currency, "amount": float(r.amount),
         "from": r.due_from, "to": r.due_to, "certainty": r.certainty, "desc": r.description})

# ---------------------------------------------------------------- who shares the note
out()
out("SHARED INSTRUMENTS (one dial turn, two clients)")
for i in ["SYN-SP-0505", "SYN-ST-0104", "SYN-EQ-0008"]:
    x = hd[(hd.snapshot_date == T) & (hd.instrument_id == i)]
    out(f"   {i}: " + ", ".join(f"{r.client_id}/{r.portfolio_id} USD {r.market_value_usd:,.0f}" for r in x.itertuples()))


# ---------------------------------------------------------------- positions for the app
# Emitted so the Streamlit app needs ONLY facts.json - no CSVs, no pandas at runtime.
positions = []
for cid in ["CL-0001", "CL-0019", "CL-0002"]:
    for x in hd[(hd.client_id == cid) & (hd.snapshot_date == T)].itertuples():
        b = beta_to_brent(x.instrument_id)
        positions.append({
            "client_id": cid, "portfolio_id": x.portfolio_id,
            "instrument_id": x.instrument_id, "name": x.instrument_name,
            "asset_class": x.asset_class, "market_value_usd": float(x.market_value_usd),
            "market_value_base": float(x.market_value_base),
            "weight_pct": float(x.weight_pct), "liquidity_tier": x.liquidity_tier,
            "advance_rate_pct": float(x.advance_rate_pct),
            "lending_value_base": float(x.lending_value_base),
            "beta": (b["beta"] if b else 0.0),
        })
facts["positions"] = positions

facts["assumptions"] = {
    "single_factor": "All shocks are a single Brent factor. Betas are OLS through the origin on four "
                     "snapshot-to-snapshot returns. Four observations is not a risk model; it is a "
                     "stated, inspectable assumption.",
    "fx_constant": "FX held at 2026-08-26. A Brent fall would plausibly move USDIDR, which would move "
                   "the SGD value of the Bara collateral. Not modelled. Named on screen.",
    "no_barrier": "instruments.csv gives no barrier level for SYN-SP-0505, so no knock-in is modelled. "
                  "The FCN is shown at its Brent beta only; the real point is that all three worst-of "
                  "legs are the same trade.",
    "private_lag": "Private and quarterly-reported valuations lag by a quarter. Untouched.",
}

if "--write" in sys.argv:
    with open(f"{HERE}/out/facts.json", "w") as f:
        json.dump(facts, f, indent=2, default=float)
    with open(f"{HERE}/out/verify_report.txt", "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\nwrote {HERE}/out/facts.json and out/verify_report.txt")
