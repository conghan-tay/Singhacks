"""Golden assertions for every number that appears on screen or in the pitch.

Run before each rehearsal:  python3 -m pytest tests/ -q
If a test fails, the demo is wrong. Fix the demo, not the test.

These exist so an AI agent building the UI can be validated against truth rather than trusted.
"""
import json, os, subprocess, sys
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(os.environ["HOME"], "mnt/SingHacks/singhacks-jb-wealth-intelligence/data")


@pytest.fixture(scope="session")
def facts():
    p = os.path.join(ROOT, "out", "facts.json")
    if not os.path.exists(p):
        subprocess.run([sys.executable, os.path.join(ROOT, "verify.py"), "--write"], check=True)
    return json.load(open(p))


@pytest.fixture(scope="session")
def plans():
    return {pid: json.load(open(os.path.join(ROOT, "plans", f"{pid}.json")))
            for pid in ("PLAN-001", "PLAN-002", "PLAN-003")}


def approx(a, b, tol=0.01):
    return abs(a - b) <= tol


# --------------------------------------------------------------- the headline finding
def test_bara_is_41_4_pct_of_hartono_household(facts):
    bara = next(t for t in facts["clients"]["CL-0001"]["top"] if t["instrument_id"] == "SYN-ST-0101")
    assert approx(bara["pct_household"], 41.42, 0.01)
    assert approx(bara["usd"], 19_287_976.54, 1.0)
    assert bara["portfolio_id"] == "PF-0002", "the concentration must be in the CUSTODY account or the story breaks"


def test_hartono_household_total(facts):
    assert approx(facts["clients"]["CL-0001"]["household_usd"], 46_571_821.48, 1.0)


def test_custody_account_is_not_mandate_measured():
    import csv
    rows = list(csv.DictReader(open(f"{DATA}/portfolios.csv")))
    pf2 = next(r for r in rows if r["portfolio_id"] == "PF-0002")
    assert pf2["service_model"] == "Custody"
    assert pf2["client_id"] == "CL-0001"


def test_fcn_weight_in_pf0001_is_6_18_not_3_6():
    """Correction to the design doc: 6.18%, and it is the entire Structured Products bucket."""
    import csv
    T = "2026-08-26"
    rows = [r for r in csv.DictReader(open(f"{DATA}/holdings.csv"))
            if r["portfolio_id"] == "PF-0001" and r["snapshot_date"] == T]
    tot = sum(float(r["market_value_base"]) for r in rows)
    fcn = next(r for r in rows if r["instrument_id"] == "SYN-SP-0505")
    w = 100 * float(fcn["market_value_base"]) / tot
    assert approx(w, 6.18, 0.01)
    sp = sum(float(r["market_value_base"]) for r in rows if r["asset_class"] == "Structured Products")
    assert approx(float(fcn["market_value_base"]), sp, 1.0), "the FCN is the whole SP allocation"


# --------------------------------------------------------------- the facility
def test_cf0005_current_state(facts):
    f = facts["facilities"]["CF-0005"]
    assert approx(f["drawn"], 8_000_000, 1)
    assert approx(f["lending_value"], 13_525_392.14, 1.0)
    assert approx(f["ltv_now"], 59.15, 0.01)
    assert approx(f["trigger_ltv"], 70.0, 0.001)


def test_cf0005_was_already_breached_at_baseline(facts):
    hist = {h["date"]: h for h in facts["facilities"]["CF-0005"]["history"]}
    assert approx(hist["2025-12-31"]["ltv"], 78.50, 0.01)
    assert hist["2025-12-31"]["ltv"] > 70.0, "the breach that cured itself is the setup for the whole plan"
    assert hist["2025-12-31"]["drawn"] == hist["2026-08-26"]["drawn"], "cured by price, not by an action"


def test_brent_trigger_is_78_85(facts):
    assert approx(facts["facilities"]["CF-0005"]["brent_trigger"], 78.85, 0.05)


def test_trigger_is_above_pre_conflict_brent(facts):
    """The single most important claim in the pitch: this is not a tail scenario."""
    assert facts["facilities"]["CF-0005"]["brent_trigger"] > facts["market"]["brent"]["2026-02-27"]
    assert facts["market"]["brent"]["2026-02-27"] == 72.40


def test_dial_to_79_does_not_fire_but_78_does(facts):
    f = facts["facilities"]["CF-0005"]
    B0 = facts["market"]["brent"]["2026-08-26"]
    def ltv(B):
        lv = f["lending_value"] + f["C"] * (B / B0 - 1)
        return 100 * f["drawn"] / lv
    assert ltv(79.0) < 70.0, "at exactly 79 the facility does NOT breach - do not dial to 79 on stage"
    assert ltv(78.0) > 70.0
    assert ltv(72.40) > 70.0


def test_ltv_at_pre_conflict_brent(facts):
    f = facts["facilities"]["CF-0005"]
    B0 = facts["market"]["brent"]["2026-08-26"]
    lv = f["lending_value"] + f["C"] * (72.40 / B0 - 1)
    assert approx(100 * f["drawn"] / lv, 73.86, 0.05)
    cure = f["drawn"] - 0.70 * lv
    assert approx(cure, 418_143, 500)


# --------------------------------------------------------------- betas
def test_bara_beta(facts):
    b = facts["betas"]["SYN-ST-0101"]
    assert approx(b["beta"], 0.721, 0.002)
    assert b["r2"] > 0.95


def test_tech_beta_is_negative(facts):
    """Ravi gains when oil falls. The book is not one-directional - this is the ranking argument."""
    assert facts["betas"]["SYN-ST-0103"]["beta"] < 0


# --------------------------------------------------------------- Abdullah
def test_abdullah_block_is_42_13_pct(facts):
    blk = facts["clients"]["CL-0019"]["shipping_energy_block"]
    assert approx(blk["pct"], 42.13, 0.01)
    assert approx(blk["usd"], 13_573_266, 5)


def test_abdullah_impact_is_about_1m_not_2m(facts):
    """Correction to the design doc: 1.06m, not 1.8-2.5m."""
    d = facts["scenario_brent_79"]["clients"]["CL-0019"]["usd_delta"]
    assert -1_150_000 < d < -1_000_000


def test_fcn_held_by_exactly_two_clients():
    import csv
    T = "2026-08-26"
    holders = {r["client_id"] for r in csv.DictReader(open(f"{DATA}/holdings.csv"))
               if r["snapshot_date"] == T and r["instrument_id"] == "SYN-SP-0505"}
    assert holders == {"CL-0001", "CL-0019"}, "one dial turn, two clients - the demo climax"


# --------------------------------------------------------------- book ranking
def test_the_tightest_facilities_break_the_other_way(facts):
    """Lau and Ravi have the least headroom and are hurt by Brent RISING. Hartono breaks first."""
    B0 = facts["market"]["brent"]["2026-08-26"]
    fac = facts["facilities"]
    assert fac["CF-0002"]["ltv_now"] > fac["CF-0005"]["ltv_now"]
    assert fac["CF-0001"]["ltv_now"] > fac["CF-0005"]["ltv_now"]
    assert fac["CF-0005"]["brent_trigger"] < B0
    assert fac["CF-0002"]["brent_trigger"] > B0
    assert fac["CF-0001"]["brent_trigger"] > B0


def test_hartono_pf0001_is_within_every_mandate_band():
    """The mandate report is green. That is what makes the finding a finding."""
    import csv
    T = "2026-08-26"
    rows = [r for r in csv.DictReader(open(f"{DATA}/holdings.csv"))
            if r["portfolio_id"] == "PF-0001" and r["snapshot_date"] == T]
    tot = sum(float(r["market_value_base"]) for r in rows)
    bands = {r["asset_class"]: (float(r["min_pct"]), float(r["max_pct"]))
             for r in csv.DictReader(open(f"{DATA}/mandates.csv")) if r["mandate_code"] == "BALG"}
    agg = {}
    for r in rows:
        agg[r["asset_class"]] = agg.get(r["asset_class"], 0) + float(r["market_value_base"])
    for ac, mv in agg.items():
        lo, hi = bands[ac]
        assert lo <= 100 * mv / tot <= hi, f"{ac} is out of band - the pitch says every band is green"


# --------------------------------------------------------------- plans
def test_plans_validate_against_schema(plans):
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.load(open(os.path.join(ROOT, "schema", "plan.schema.json")))
    for pid, p in plans.items():
        jsonschema.validate(p, schema)


def test_plans_start_drafted_and_unsigned(plans):
    for pid, p in plans.items():
        assert p["state"] == "DRAFTED"
        assert p["governance"]["armed_by"] is None
        assert p["governance"]["armed_signature"] is None


def test_no_trigger_is_model_evaluated(plans):
    for pid, p in plans.items():
        assert p["trigger"]["evaluated_by"] == "deterministic"


def test_every_action_states_its_second_order_effect(plans):
    for pid, p in plans.items():
        assert len(p["actions"]) >= 2
        for a in p["actions"]:
            assert a["second_order"].strip(), f"{pid} action {a['rank']} has no stated cost"


def test_every_evidence_hop_has_provenance(plans):
    for pid, p in plans.items():
        assert len(p["evidence_chain"]) >= 2
        for hop in p["evidence_chain"]:
            assert hop["provenance"].strip()
            assert hop["source_file"].endswith(".csv") or hop["source_file"].endswith(".json")


def test_assumptions_are_present_on_every_plan(plans):
    for pid, p in plans.items():
        assert len(p["assumptions"]) >= 4
        assert any("FX" in a or "fx" in a for a in p["assumptions"])
        assert any("barrier" in a.lower() for a in p["assumptions"])
        assert p["confidence"]["what_we_would_check"]


def test_plan_numbers_match_facts(plans, facts):
    p1 = plans["PLAN-001"]
    assert approx(p1["trigger"]["current_value"], facts["market"]["brent"]["2026-08-26"], 0.001)
    assert p1["trigger"]["level"] == 79.00
    assert approx(p1["projected_consequence"]["household_delta_usd"],
                  facts["scenario_brent_79"]["clients"]["CL-0001"]["usd_delta"], 1.0)
    p3 = plans["PLAN-003"]
    assert approx(p3["projected_consequence"]["household_delta_usd"],
                  facts["scenario_brent_79"]["clients"]["CL-0019"]["usd_delta"], 1.0)


def test_shared_trigger_across_two_clients(plans):
    assert plans["PLAN-001"]["trigger"]["expression"] == plans["PLAN-003"]["trigger"]["expression"]
    assert plans["PLAN-001"]["client_id"] != plans["PLAN-003"]["client_id"]
