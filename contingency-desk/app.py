"""Run with streamlit run app.py. All session transitions are delegated to store."""
import streamlit as st

import engine
import store
import ui
from style import CSS


# These are control bounds explicitly specified in the brief, not financial outputs.
DIAL_MIN = 60.0
DIAL_MAX = 120.0
DIAL_STEP = 0.50
PRE_CONFLICT_DATE = "2026-02-27"
BOARD_COLUMNS = {
    "Fired": (store.FIRED, store.ACTIONED),
    "Armed and watching": (store.ARMED, store.WATCHING),
    "Drafts awaiting you": (store.DRAFTED,),
    "Dismissed": (store.DISMISSED,),
}
SEVERITIES = ("critical", "high", "medium", "low")


def navigate(screen, plan_id=None):
    st.session_state.screen = screen
    if plan_id is not None:
        st.session_state.selected_plan = plan_id


def update_market():
    st.session_state.shocked = engine.shock(st.session_state.facts, st.session_state.brent)
    fired = store.sweep(st.session_state.plans, st.session_state.shocked,
                        st.session_state.facts, engine.evaluate_trigger)
    if fired:
        st.session_state.notice = "Fired: " + ", ".join(fired)


def move_dial():
    # Keep the scenario separate from Streamlit's page-local widget lifecycle.
    st.session_state.brent = st.session_state.dial_brent
    update_market()


def preset(value):
    st.session_state.brent = value
    st.session_state.dial_brent = value
    update_market()
    selected = st.session_state.plans[st.session_state.selected_plan]
    if selected["state"] == store.FIRED:
        navigate("Plan")


def reset_demo():
    st.session_state.plans = engine.load_plans()
    st.session_state.brent = engine.brent_now(st.session_state.facts)
    st.session_state.dial_brent = st.session_state.brent
    st.session_state.selected_plan = next(iter(st.session_state.plans))
    for key in list(st.session_state):
        if key.startswith(("level_", "reason_", "rank_")):
            del st.session_state[key]
    st.session_state.error = None
    st.session_state.notice = "Demo reset. Original drafts and pre-armed approval restored."
    update_market()


def transition(operation, plan_id, *args):
    try:
        st.session_state.plans[plan_id] = operation(
            st.session_state.plans[plan_id], st.session_state.rm, *args)
    except store.TransitionError as exc:
        st.session_state.error = str(exc)
        return
    st.session_state.error = None
    st.session_state.notice = f'{plan_id}: {st.session_state.plans[plan_id]["state"]}'
    update_market()
    if operation is store.arm and st.session_state.plans[plan_id]["state"] == store.WATCHING:
        navigate("Dial")


def arm_plan(plan_id):
    transition(store.arm, plan_id, st.session_state[f"level_{plan_id}"])


def dismiss_plan(plan_id):
    transition(store.dismiss, plan_id, st.session_state.get(f"reason_{plan_id}", ""))


def action_plan(plan_id):
    transition(store.action, plan_id, st.session_state[f"rank_{plan_id}"])


def select_rank(plan_id, rank):
    st.session_state[f"rank_{plan_id}"] = rank


def observation(plan):
    return engine.evaluate_trigger(plan, st.session_state.shocked, st.session_state.facts,
                                   plan["governance"].get("armed_trigger_level"))


def board():
    st.markdown('<h1>Contingency board</h1><p class="lead">Reasoning reviewed before the event. '
                'Action approved when it matters.</p>', unsafe_allow_html=True)
    observations = {pid: observation(p) for pid, p in st.session_state.plans.items()}
    snapshot = {**st.session_state.shocked, "observations": observations}
    for column, (label, states) in zip(st.columns(len(BOARD_COLUMNS)), BOARD_COLUMNS.items()):
        with column:
            plans = [p for p in st.session_state.plans.values() if p["state"] in states]
            # abs is a sorting key only; the displayed distance is the engine's signed figure.
            plans.sort(key=lambda p: (SEVERITIES.index(p["severity"]),
                       observations[p["plan_id"]]["distance_pct"] is None,
                       abs(observations[p["plan_id"]]["distance_pct"] or float()), p["plan_id"]))
            st.markdown(f'<div class="board-heading">{ui.text(label)} <span>{len(plans)}</span></div>',
                        unsafe_allow_html=True)
            if not plans:
                st.markdown('<p class="empty-column">No plans here</p>', unsafe_allow_html=True)
            for plan in plans:
                st.markdown(ui.render_board_row(plan, snapshot), unsafe_allow_html=True)
                st.button(f'Open {plan["plan_id"]}', key=f'open_{plan["plan_id"]}',
                          on_click=navigate, args=("Plan", plan["plan_id"]), use_container_width=True)


def plan_screen():
    plan = st.session_state.plans[st.session_state.selected_plan]
    with st.container(key="plan-navigation"):
        for column, candidate in zip(st.columns(len(st.session_state.plans)), st.session_state.plans.values()):
            column.button(candidate["plan_id"], on_click=navigate, args=("Plan", candidate["plan_id"]),
                          type="primary" if candidate["plan_id"] == plan["plan_id"] else "secondary",
                          use_container_width=True)
    st.markdown(ui.render_plan_card(plan, observation(plan), st.session_state.shocked), unsafe_allow_html=True)
    action_bar(plan)


def action_bar(plan):
    pid = plan["plan_id"]
    with st.container(key="plan-action-bar"):
        st.markdown(f'<div class="bar-heading">{ui.text(pid)} · {ui.text(plan["state"])}'
                    f'<small>Relationship manager · {ui.text(st.session_state.rm)}</small></div>', unsafe_allow_html=True)
        if plan["state"] == store.DRAFTED:
            level, arm, dismiss = st.columns([2, 1, 1], vertical_alignment="bottom")
            with level:
                st.number_input(f'Trigger level ({plan["trigger"]["unit"]})',
                                value=float(plan["trigger"]["level"]), format="%.2f", key=f"level_{pid}")
            arm.button("Arm", type="primary", on_click=arm_plan, args=(pid,), use_container_width=True)
            dismiss.button("Dismiss", on_click=dismiss_plan, args=(pid,), use_container_width=True)
            st.text_input("Dismissal reason", key=f"reason_{pid}", placeholder="Required to dismiss this plan")
        elif plan["state"] == store.FIRED:
            rank_key = f"rank_{pid}"
            if rank_key not in st.session_state:
                st.session_state[rank_key] = next(iter(plan["actions"]))["rank"]
            chosen = next(a for a in plan["actions"] if a["rank"] == st.session_state[rank_key])
            with st.expander("Choose ranked action · " + str(chosen["rank"])):
                for action in plan["actions"]:
                    st.button(f'{action["rank"]} · {action["action"]}', key=f'choose_{pid}_{action["rank"]}',
                              on_click=select_rank, args=(pid, action["rank"]))
            st.markdown(f'<p class="chosen-action">{ui.text(chosen["action"])}</p>', unsafe_allow_html=True)
            take, stand = st.columns(2)
            take.button("Take action", type="primary", on_click=action_plan, args=(pid,), use_container_width=True)
            stand.button("Stand down", on_click=dismiss_plan, args=(pid,), use_container_width=True)
            st.text_input("Stand-down reason", key=f"reason_{pid}", placeholder="Required to stand down this plan")
        else:
            st.button("Watching for trigger" if plan["state"] == store.WATCHING else plan["state"].capitalize(),
                      disabled=True, use_container_width=True)
            if plan["governance"].get("resolution_reason"):
                st.caption(plan["governance"]["resolution_reason"])
        if st.session_state.error:
            st.error(st.session_state.error)


def dial():
    facts = st.session_state.facts
    shocked = st.session_state.shocked
    pre_conflict = facts["market"]["brent"][PRE_CONFLICT_DATE]
    today = engine.brent_now(facts)
    st.markdown('<h1>Scenario dial</h1><p class="lead">Move Brent. Watch the facilities and the plans respond.</p>'
                f'<div class="brent-value">USD {shocked["brent"]:.2f}<span>/bbl · Brent</span></div>', unsafe_allow_html=True)
    st.session_state.dial_brent = st.session_state.brent
    st.slider("Brent (USD/bbl)", min_value=DIAL_MIN, max_value=DIAL_MAX, step=DIAL_STEP,
              key="dial_brent", format="%.2f", on_change=move_dial)
    st.markdown(f'<div class="dial-ticks"><span>{pre_conflict:.2f} · pre-conflict, {ui.text(PRE_CONFLICT_DATE)}</span>'
                f'<span>{today:.2f} · today</span></div>', unsafe_allow_html=True)
    with st.container(key="dial-presets"):
        historical, current, reset = st.columns(3)
        historical.button(f'Pre-conflict · {pre_conflict:.2f}', on_click=preset, args=(pre_conflict,), use_container_width=True)
        current.button(f'Today · {today:.2f}', on_click=preset, args=(today,), use_container_width=True)
        reset.button("Reset demo", on_click=reset_demo, use_container_width=True)
    st.markdown('<h2>Facility watch</h2>' + ui.render_dial_strip(shocked), unsafe_allow_html=True)
    st.markdown('<h2>Plans at this scenario</h2>', unsafe_allow_html=True)
    for column, plan in zip(st.columns(len(st.session_state.plans)), st.session_state.plans.values()):
        with column:
            st.markdown(ui.render_board_row(plan, {**shocked, "observations": {plan["plan_id"]: observation(plan)}}),
                        unsafe_allow_html=True)
            st.button(f'Review {plan["plan_id"]}', key=f'dial_{plan["plan_id"]}', on_click=navigate,
                      args=("Plan", plan["plan_id"]), use_container_width=True)


def main():
    st.set_page_config(page_title="Contingency Desk", layout="wide")
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)
    if "plans" not in st.session_state:
        st.session_state.facts = engine.load_facts()
        st.session_state.plans = engine.load_plans()
        st.session_state.selected_plan = next(iter(st.session_state.plans))
        st.session_state.rm = next(p["governance"]["armed_by"] for p in st.session_state.plans.values()
                                   if p["governance"].get("armed_by"))
        st.session_state.screen = "Board"
        st.session_state.brent = engine.brent_now(st.session_state.facts)
        st.session_state.error = None
        st.session_state.notice = None
        update_market()
    st.markdown('<div class="desk-masthead"><span>The Contingency Desk</span>'
                f'<small>Private banking · Snapshot {ui.text(st.session_state.facts["as_of"])}</small></div>',
                unsafe_allow_html=True)
    with st.container(key="desk-navigation"):
        for column, screen in zip(st.columns(3), ("Board", "Plan", "Dial")):
            column.button(screen, on_click=navigate, args=(screen,), use_container_width=True,
                          type="primary" if st.session_state.screen == screen else "secondary")
    if st.session_state.notice:
        st.markdown(f'<p class="session-notice" role="status">{ui.text(st.session_state.notice)}</p>',
                    unsafe_allow_html=True)
    {"Board": board, "Plan": plan_screen, "Dial": dial}[st.session_state.screen]()


if __name__ == "__main__":
    main()
