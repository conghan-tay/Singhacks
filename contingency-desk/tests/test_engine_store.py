"""The engine and the state machine. If these fail, the demo cannot be driven."""
import os, sys
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import engine, store


@pytest.fixture(scope="module")
def F(): return engine.load_facts()


@pytest.fixture
def P(): return engine.load_plans()


def test_shock_at_today_is_a_noop(F):
    s = engine.shock(F, engine.brent_now(F))
    assert abs(s["clients"]["CL-0001"]["delta_usd"]) < 1
    assert abs(s["facilities"]["CF-0005"]["ltv"] - 59.15) < 0.01


def test_dial_to_preconflict_breaches_cf0005(F):
    s = engine.shock(F, 72.40)
    f = s["facilities"]["CF-0005"]
    assert f["breached"] and abs(f["ltv"] - 73.86) < 0.05
    assert abs(f["cure_cash"] - 418_143) < 500


def test_79_does_not_breach(F):
    assert not engine.shock(F, 79.0)["facilities"]["CF-0005"]["breached"]


def test_tech_client_gains_when_oil_falls(F):
    s = engine.shock(F, 72.40)
    assert s["clients"]["CL-0002"]["delta_usd"] > 0
    assert s["clients"]["CL-0001"]["delta_pct"] < -8
    assert s["clients"]["CL-0019"]["delta_pct"] < -4


def test_trigger_evaluation_is_deterministic(F, P):
    s = engine.shock(F, 72.40)
    for pid in ("PLAN-001", "PLAN-003"):
        assert engine.evaluate_trigger(P[pid], s, F)["hit"]
    s2 = engine.shock(F, engine.brent_now(F))
    assert not engine.evaluate_trigger(P["PLAN-001"], s2, F)["hit"]
    assert not engine.evaluate_trigger(P["PLAN-002"], s2, F)["hit"]


def test_armed_level_overrides_drafted_level(F, P):
    s = engine.shock(F, 80.0)
    assert not engine.evaluate_trigger(P["PLAN-001"], s, F)["hit"]
    assert engine.evaluate_trigger(P["PLAN-001"], s, F, level=85.0)["hit"]


# --------------------------------------------------------------- state machine
def test_full_walk_drafted_to_actioned(F, P):
    p = store.arm(P["PLAN-001"], "priscilla.ong@juliusbaer.com", trigger_level=79.0)
    assert p["state"] == store.WATCHING
    assert p["governance"]["armed_signature"] and p["governance"]["armed_at"]
    P["PLAN-001"] = p
    assert P["PLAN-003"]["state"] == store.WATCHING, "PLAN-003 ships pre-armed; it is not armed here"
    fired = store.sweep(P, engine.shock(F, 72.40), F, engine.evaluate_trigger)
    assert set(fired) == {"PLAN-001", "PLAN-003"}
    done = store.action(P["PLAN-001"], "priscilla.ong@juliusbaer.com", rank=1)
    assert done["state"] == store.ACTIONED
    assert done["governance"]["resolution"] == "ACTIONED"
    assert [e["to"] for e in done["governance"]["decision_log"]] == [
        "DRAFTED", "ARMED", "WATCHING", "FIRED", "ACTIONED"]


def test_illegal_transitions_are_refused(P):
    with pytest.raises(store.TransitionError):
        store.fire(P["PLAN-001"], {})                      # not watching yet
    with pytest.raises(store.TransitionError):
        store.dismiss(P["PLAN-001"], "rm", "")             # no reason


def test_dismiss_from_drafted_is_terminal(P):
    d = store.dismiss(P["PLAN-002"], "rm", "Client already ring-fenced the deposit")
    assert d["state"] == store.DISMISSED
    assert store.ALLOWED[d["state"]] == set()


def test_signature_changes_if_the_body_is_edited(P):
    p = store.arm(P["PLAN-001"], "rm")
    sig = p["governance"]["armed_signature"]
    p2 = dict(p); p2["actions"] = p["actions"][1:]
    assert store.signature(p2) != sig, "the signature must not survive a rewrite of the reasoning"


def test_signature_ignores_governance(P):
    p = store.arm(P["PLAN-002"], "rm")
    assert store.signature(p) == p["governance"]["armed_signature"]


def test_prearmed_plan_carries_a_signature_written_before_the_event(P):
    """PLAN-003 ships armed on 2026-08-24. The gap between arming and firing is the whole claim.

    PLAN-001 stays DRAFTED so the RM performs the human interrupt live. One card demonstrates the
    mechanism, the other demonstrates the artefact.
    """
    p3, p1 = P["PLAN-003"], P["PLAN-001"]
    assert p1["state"] == store.DRAFTED and p1["governance"]["armed_at"] is None
    assert p3["state"] == store.WATCHING
    assert p3["governance"]["armed_at"] == "2026-08-24T08:52:00+08:00"
    assert p3["governance"]["armed_by"] == "priscilla.ong@juliusbaer.com"
    assert store.verify_signature(p3)["ok"] is True
    assert [e["to"] for e in p3["governance"]["decision_log"]] == ["DRAFTED", "ARMED", "WATCHING"]
    assert all(e["at"].startswith("2026-08-24") for e in p3["governance"]["decision_log"])


def test_armed_vs_now_available_after_firing(F, P):
    P["PLAN-001"] = store.arm(P["PLAN-001"], "rm", trigger_level=79.0)
    store.sweep(P, engine.shock(F, 72.40), F, engine.evaluate_trigger)
    v = store.armed_vs_now(P["PLAN-001"], engine.shock(F, 72.40))
    assert v["armed_level"] == 79.0 and v["observed_value"] == 72.40 and v["projected"]


def test_signature_is_checked_not_just_written(P):
    """Writing a hash proves nothing unless something recomputes it."""
    unarmed = store.verify_signature(P["PLAN-002"])
    assert unarmed == {"signed": False, "ok": None, "expected": None, "actual": None}

    p = store.arm(P["PLAN-001"], "priscilla.ong@juliusbaer.com", trigger_level=79.0)
    assert store.verify_signature(p)["ok"] is True

    import copy
    tampered = copy.deepcopy(p)
    tampered["actions"][0]["second_order"] = "no downside at all"
    assert store.verify_signature(tampered)["ok"] is False, "a quiet rewrite must not verify"

    moved = store.fire(p, {"expression": "BRENT < 79", "variable": "BRENT", "observed": 72.40})
    assert store.verify_signature(moved)["ok"] is True, "a legitimate state change must still verify"
    assert store.armed_vs_now(moved, None)["signature_ok"] is True
