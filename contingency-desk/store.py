"""Plan state machine. The only place a plan's state changes.

DRAFTED -> ARMED -> WATCHING -> FIRED -> ACTIONED | DISMISSED
STALE is deliberately not implemented.

Two transitions are performed by a human and nothing substitutes for them:
  DRAFTED -> ARMED    the RM signs reasoning she can inspect, BEFORE the event
  FIRED   -> ACTIONED nothing executes without it
"""
from __future__ import annotations
import copy, hashlib, json
from datetime import datetime, timezone, timedelta

SGT = timezone(timedelta(hours=8))

DRAFTED, ARMED, WATCHING, FIRED, ACTIONED, DISMISSED = (
    "DRAFTED", "ARMED", "WATCHING", "FIRED", "ACTIONED", "DISMISSED")

ALLOWED = {
    DRAFTED:   {ARMED, DISMISSED},
    ARMED:     {WATCHING},
    WATCHING:  {FIRED},
    FIRED:     {ACTIONED, DISMISSED},
    ACTIONED:  set(),
    DISMISSED: set(),
}
TERMINAL = {ACTIONED, DISMISSED}


class TransitionError(Exception):
    pass


def _now() -> str:
    return datetime.now(SGT).isoformat(timespec="seconds")


SIG_EXCLUDE = {"governance", "state"}


def signature(plan: dict) -> str:
    """sha256 over the canonical plan body, excluding `governance` and `state`.

    Those two change legitimately as the plan moves through its lifecycle; the reasoning does not.
    So the signature covers exactly what the RM read and approved - trigger, evidence chain,
    consequence, actions, script, suitability, assumptions - and nothing that is allowed to move
    afterwards. That is what makes the arming record worth having: the reasoning cannot be quietly
    rewritten, and the approval provably predates the outcome.
    """
    body = {k: v for k, v in plan.items() if k not in SIG_EXCLUDE}
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def verify_signature(plan: dict) -> dict:
    """Recompute the signature and compare it to the one written at arming.

    Writing a hash proves nothing on its own; this is the function that makes the arming record an
    assertion rather than a decoration. Call it every time a signature is put on screen.

    Returns {signed, ok, expected, actual}. `ok` is None for a plan that was never armed.
    """
    expected = plan["governance"].get("armed_signature")
    if not expected:
        return {"signed": False, "ok": None, "expected": None, "actual": None}
    actual = signature(plan)
    return {"signed": True, "ok": actual == expected, "expected": expected, "actual": actual}


def _log(plan: dict, actor: str, to: str, note: str = "", at: str | None = None) -> None:
    plan["governance"]["decision_log"].append(
        {"at": at or _now(), "actor": actor, "from": plan["state"], "to": to, "note": note})


def _transition(plan: dict, to: str, actor: str, note: str = "", at: str | None = None) -> dict:
    if to not in ALLOWED[plan["state"]]:
        raise TransitionError(f"{plan['plan_id']}: {plan['state']} -> {to} is not allowed")
    _log(plan, actor, to, note, at)
    plan["state"] = to
    return plan


# ------------------------------------------------------------------ human interrupt 1
def arm(plan: dict, rm: str, trigger_level: float | None = None, note: str = "",
        at: str | None = None) -> dict:
    """The RM signs the plan. Optionally at a level different from the drafted one.

    `at` backdates the record. Its only legitimate caller is the offline authoring pass that seeds a
    plan the RM armed before the demo window opened; the UI never passes it, so on any live path the
    timestamp is wall-clock and the arming provably predates whatever fires it.
    """
    plan = copy.deepcopy(plan)
    lvl = plan["trigger"]["level"] if trigger_level is None else float(trigger_level)
    g = plan["governance"]
    g["armed_by"] = rm
    g["armed_at"] = at or _now()
    g["armed_trigger_level"] = lvl
    g["armed_signature"] = signature(plan)
    edited = "" if lvl == plan["trigger"]["level"] else f" (level edited {plan['trigger']['level']:g} -> {lvl:g})"
    _transition(plan, ARMED, rm, (note + edited).strip(), at)
    return _transition(plan, WATCHING, "system", "trigger registered with the watcher", at)


def dismiss(plan: dict, rm: str, reason: str) -> dict:
    if not reason or not reason.strip():
        raise TransitionError("a dismissal must carry a reason - it is authoring signal")
    plan = copy.deepcopy(plan)
    plan["governance"]["resolution"] = DISMISSED
    plan["governance"]["resolution_reason"] = reason.strip()
    return _transition(plan, DISMISSED, rm, reason.strip())


# ------------------------------------------------------------------ deterministic
def fire(plan: dict, observation: dict) -> dict:
    """Called only by the watcher, only on a deterministic evaluation. No model reaches this."""
    plan = copy.deepcopy(plan)
    plan["governance"]["fired_at"] = _now()
    plan["governance"]["fired_observation"] = observation
    return _transition(plan, FIRED, "watcher", observation.get("expression", ""))


# ------------------------------------------------------------------ human interrupt 2
def action(plan: dict, rm: str, rank: int, note: str = "") -> dict:
    plan = copy.deepcopy(plan)
    chosen = next((a for a in plan["actions"] if a["rank"] == rank), None)
    if chosen is None:
        raise TransitionError(f"no action with rank {rank}")
    plan["governance"]["resolution"] = ACTIONED
    plan["governance"]["resolution_reason"] = f"Action {rank}: {chosen['action']}"
    return _transition(plan, ACTIONED, rm, (note or chosen["action"])[:200])


# ------------------------------------------------------------------ the watching sweep
def sweep(plans: dict, state: dict, facts: dict, evaluate) -> list[str]:
    """Evaluate every WATCHING plan against a market state. Returns the plan_ids that fired.

    `evaluate` is engine.evaluate_trigger, injected so the store never imports the engine.
    """
    fired = []
    for pid, plan in plans.items():
        if plan["state"] != WATCHING:
            continue
        r = evaluate(plan, state, facts, plan["governance"].get("armed_trigger_level"))
        if r["hit"]:
            plans[pid] = fire(plan, r)
            fired.append(pid)
    return fired


def armed_vs_now(plan: dict, state: dict) -> dict | None:
    """What the plan projected at arming time, against what is true now. Shown on a fired card."""
    if plan["state"] not in (FIRED, ACTIONED, DISMISSED) or not plan["governance"].get("fired_observation"):
        return None
    o = plan["governance"]["fired_observation"]
    return {"armed_by": plan["governance"]["armed_by"], "armed_at": plan["governance"]["armed_at"],
            "armed_level": plan["governance"]["armed_trigger_level"],
            "signature": plan["governance"]["armed_signature"],
            "signature_ok": verify_signature(plan)["ok"],
            "projected": plan["projected_consequence"]["items"],
            "observed_variable": o.get("variable"), "observed_value": o.get("observed"),
            "fired_at": plan["governance"]["fired_at"]}


if __name__ == "__main__":
    import engine
    F, P = engine.load_facts(), engine.load_plans()
    p = P["PLAN-001"]
    print(p["state"])
    p = arm(p, "priscilla.ong@juliusbaer.com", trigger_level=79.0)
    print(p["state"], p["governance"]["armed_signature"][:16], "...")
    P["PLAN-001"] = p
    print("PLAN-003 ships pre-armed:", P["PLAN-003"]["state"],
          P["PLAN-003"]["governance"]["armed_at"], verify_signature(P["PLAN-003"])["ok"])
    st = engine.shock(F, 72.40)
    print("fired:", sweep(P, st, F, engine.evaluate_trigger))
    P["PLAN-001"] = action(P["PLAN-001"], "priscilla.ong@juliusbaer.com", rank=1)
    print(P["PLAN-001"]["state"])
    for e in P["PLAN-001"]["governance"]["decision_log"]:
        print(f"   {e['at']}  {e['actor']:34s} {str(e['from']):9s} -> {e['to']:9s} {e['note'][:60]}")
    print("signature verifies:", verify_signature(P["PLAN-001"]))
    tampered = copy.deepcopy(P["PLAN-001"])
    tampered["actions"][0]["second_order"] = "no downside at all"
    print("after a quiet rewrite:", verify_signature(tampered)["ok"])
    try:
        arm(P["PLAN-001"], "x")
    except TransitionError as e:
        print("guard ok:", e)
