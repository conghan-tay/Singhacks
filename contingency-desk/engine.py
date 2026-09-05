"""Deterministic engine. Arithmetic only - no model, no network, no I/O beyond facts.json.

Everything the UI displays comes from here or straight out of a plan JSON.
If a number is not produced by this module, it does not go on screen.
"""
from __future__ import annotations
import json, os
from typing import Any

ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DATE = "2026-08-26"


def load_facts(path: str | None = None) -> dict:
    return json.load(open(path or os.path.join(ROOT, "out", "facts.json")))


def load_plans(path: str | None = None) -> dict:
    d = path or os.path.join(ROOT, "plans")
    return {p["plan_id"]: p for p in
            (json.load(open(os.path.join(d, f))) for f in sorted(os.listdir(d)) if f.endswith(".json"))}


def brent_now(facts: dict) -> float:
    return facts["market"]["brent"][BASE_DATE]


def shock(facts: dict, brent_level: float) -> dict:
    """Revalue the book at a Brent level.

    Linear in Brent by construction: every position moves at its own precomputed beta, and a
    facility's lending value is the beta-weighted sum of its collateral's lending values.
    """
    b0 = brent_now(facts)
    m = brent_level / b0 - 1

    facilities = {}
    for fid, f in facts["facilities"].items():
        lv = f["lending_value"] + f["C"] * m
        ltv = 100 * f["drawn"] / lv
        facilities[fid] = {
            "facility_id": fid, "client_id": f["client_id"], "ccy": f["ccy"],
            "drawn": f["drawn"], "lending_value": lv, "ltv": ltv,
            "trigger_ltv": f["trigger_ltv"], "breached": ltv >= f["trigger_ltv"],
            "headroom": 0.01 * f["trigger_ltv"] * lv - f["drawn"],
            "cure_cash": max(0.0, f["drawn"] - 0.01 * f["trigger_ltv"] * lv),
        }

    clients: dict[str, Any] = {}
    for p in facts["positions"]:
        c = clients.setdefault(p["client_id"], {"delta_usd": 0.0, "moves": []})
        d = p["market_value_usd"] * p["beta"] * m
        c["delta_usd"] += d
        c["moves"].append({**{k: p[k] for k in
                              ("instrument_id", "name", "portfolio_id", "beta", "market_value_usd")},
                           "pct": 100 * p["beta"] * m, "usd_delta": d,
                           "shocked_usd": p["market_value_usd"] * (1 + p["beta"] * m)})
    for cid, c in clients.items():
        c["household_usd"] = facts["clients"][cid]["household_usd"]
        c["delta_pct"] = 100 * c["delta_usd"] / c["household_usd"]
        c["moves"].sort(key=lambda z: z["usd_delta"])

    return {"brent": brent_level, "mult": m, "facilities": facilities, "clients": clients}


def resolve(variable: str, state: dict, facts: dict) -> float:
    """Resolve a trigger variable against a shocked state. Extend here, never in the UI."""
    if variable == "BRENT":
        return state["brent"]
    if variable.endswith(".LTV"):
        return state["facilities"][variable.split(".")[0]]["ltv"]
    if variable.endswith(".HEADROOM"):
        return state["facilities"][variable.split(".")[0]]["headroom"]
    raise KeyError(f"unknown trigger variable: {variable}")


_OPS = {"<": lambda a, b: a < b, "<=": lambda a, b: a <= b,
        ">": lambda a, b: a > b, ">=": lambda a, b: a >= b}


def evaluate_trigger(plan: dict, state: dict, facts: dict, level: float | None = None) -> dict:
    """Deterministic. A model never reaches this function.

    `level` overrides the drafted level with the one the RM actually armed.
    """
    t = plan["trigger"]
    assert t["evaluated_by"] == "deterministic", "a trigger is never evaluated by a model"
    lvl = t["level"] if level is None else level
    observed = resolve(t["variable"], state, facts)
    hit = _OPS[t["operator"]](observed, lvl)
    return {"hit": hit, "observed": observed, "level": lvl,
            "variable": t["variable"], "operator": t["operator"],
            "expression": f"{t['variable']} {t['operator']} {lvl:g}",
            "distance_pct": 100 * (lvl / observed - 1) if observed else None}


def brent_for_facility_trigger(facts: dict, facility_id: str) -> float:
    """The Brent level at which a facility reaches its margin call. Used for the derivation panel."""
    return facts["facilities"][facility_id]["brent_trigger"]


if __name__ == "__main__":
    F = load_facts(); P = load_plans()
    for b in (brent_now(F), 79.0, 72.40):
        s = shock(F, b)
        fired = [pid for pid, pl in P.items() if evaluate_trigger(pl, s, F)["hit"]]
        cf5 = s["facilities"]["CF-0005"]
        print(f"Brent {b:6.2f}  CF-0005 LTV {cf5['ltv']:6.2f}%  "
              f"CL-0001 {s['clients']['CL-0001']['delta_pct']:+6.2f}%  "
              f"CL-0019 {s['clients']['CL-0019']['delta_pct']:+6.2f}%  "
              f"CL-0002 {s['clients']['CL-0002']['delta_pct']:+6.2f}%  fired={fired}")
