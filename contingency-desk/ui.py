"""Escaped HTML presentation. Financial values belong to the engine and plan files."""
from html import escape

import store


def text(value):
    return escape(str(value), quote=True)


def badge(label, kind=None):
    return f'<span class="badge {text(kind or label)}">{text(label.replace("_", " "))}</span>'


def percent(value, signed=False):
    return format(value, "+.2f" if signed else ".2f") + "%"


def money(value, ccy="USD", signed=False):
    return f'{text(ccy)} {format(value, "+,.0f" if signed else ",.0f")}'


def delta_class(value):
    return "negative" if format(value, "+f").startswith("-") else "positive"


def bullets(values):
    return '<ul>' + ''.join(f'<li>{text(v)}</li>' for v in values) + '</ul>'


def item_table(items):
    return ('<table class="value-table"><tbody>' + ''.join(
        f'<tr><th scope="row">{text(i["label"])}<small>{text(i["basis"])}</small></th>'
        f'<td>{text(i["value"])}</td></tr>' for i in items) + '</tbody></table>')


def render_evidence_chain(plan) -> str:
    hops = []
    for hop in plan["evidence_chain"]:
        hops.append(
            f'<li class="hop" data-conf="{text(hop["confidence"])}">'
            f'<span class="hop-kind">{text(hop["kind"].replace("_", " "))}'
            f' · {text(hop["confidence"])} confidence</span><div class="hop-body">'
            f'<div class="hop-label">{text(hop["label"])}</div>'
            f'<div class="hop-detail">{text(hop["detail"])}</div>'
            f'<div class="hop-prov"><code>{text(hop["provenance"])}</code>'
            f' · {text(hop["source_file"])} · {text(hop["ref"])}</div></div></li>'
        )
    return '<ol class="pc-chain">' + ''.join(hops) + '</ol>'


def _signature(plan):
    checked = store.verify_signature(plan)
    if not checked["signed"]:
        return '<p class="caption">Not armed</p>'
    label = "signature verified" if checked["ok"] else "SIGNATURE MISMATCH"
    kind = "pass" if checked["ok"] else "fail"
    governance = plan["governance"]
    return (
        f'<div class="signature"><code title="{text(checked["expected"])}">'
        f'{text(checked["expected"][:16])}</code> {badge(label, kind)}'
        f'<small>Armed by {text(governance["armed_by"])}'
        f' · {text(governance["armed_at"])}</small></div>'
    )


def _current_consequence(plan, shocked):
    client = shocked["clients"][plan["client_id"]]
    rows = [f'<tr><th scope="row">Brent</th><td>USD {shocked["brent"]:.2f}/bbl</td></tr>',
            f'<tr><th scope="row">Household impact</th><td class="{delta_class(client["delta_usd"])}">'
            f'{money(client["delta_usd"], signed=True)}<br>{percent(client["delta_pct"], signed=True)}</td></tr>']
    for facility in shocked["facilities"].values():
        if facility["client_id"] != plan["client_id"]:
            continue
        rows.extend([
            f'<tr><th scope="row">{text(facility["facility_id"])} LTV</th><td>'
            f'{percent(facility["ltv"])} {badge("BREACH", "fail") if facility["breached"] else ""}'
            f'<small>Trigger {percent(facility["trigger_ltv"])}</small></td></tr>',
            f'<tr><th scope="row">Lending value</th><td>{money(facility["lending_value"], facility["ccy"])}</td></tr>',
            f'<tr><th scope="row">Cash cure</th><td>{money(facility["cure_cash"], facility["ccy"])}</td></tr>',
        ])
    return '<table class="value-table"><tbody>' + ''.join(rows) + '</tbody></table>'


def _fired_band(plan, shocked):
    comparison = store.armed_vs_now(plan, shocked)
    if comparison is None:
        return ''
    trigger = plan["trigger"]
    return (
        '<aside class="pc-fired-band"><div class="comparison">'
        '<section><h2>Projected at arming</h2>'
        f'<p class="caption">Drafted level {trigger["level"]:.2f} {text(trigger["unit"])}'
        f' · Armed level {comparison["armed_level"]:.2f} {text(trigger["unit"])}</p>'
        '<p class="caption">Signed plan projection; editing the trigger does not rewrite this scenario.</p>'
        f'{item_table(comparison["projected"])}</section>'
        '<section><h2>Actual now</h2><p class="caption">Current dial scenario · deterministic simulation</p>'
        f'{_current_consequence(plan, shocked)}'
        f'<small>Fired at {text(comparison["fired_at"])} · '
        f'{text(comparison["observed_variable"])} observed {comparison["observed_value"]:.2f}</small>'
        '</section></div>' + _signature(plan) + '</aside>'
    )


def render_plan_card(plan, state_snapshot, shocked) -> str:
    """state_snapshot is engine.evaluate_trigger's result at the effective trigger level."""
    trigger = plan["trigger"]
    derivation = ''.join(
        f'<li><div class="derivation-row"><span>{text(row["step"])}</span>'
        f'<span class="number">{text(row["value"])}</span></div><small>{text(row["source"])}</small></li>'
        for row in trigger["derivation"]
    )
    actions = ''.join(
        f'<article class="ranked-action"><div class="action-heading"><span class="rank">{text(a["rank"])}</span>'
        f'<h3>{text(a["action"])}</h3></div><p><strong>Rationale</strong> · {text(a["rationale"])}</p>'
        f'<div class="action-cost"><strong>Cost</strong><p>{text(a["second_order"])}</p></div>'
        + (f'<p class="requirements"><strong>Requires</strong> · {text("; ".join(a["requires"]))}</p>'
           if a["requires"] else '') + '</article>' for a in plan["actions"]
    )
    script = plan["client_script"]
    suitability = plan["suitability"]
    checks = ''.join(
        f'<tr><th scope="row">{text(c["check"])}<p>{text(c["detail"])}</p></th>'
        f'<td>{badge(c["result"])}</td></tr>' for c in suitability["checks"]
    )
    confidence = plan["confidence"]
    verdict_kind = "pass" if suitability["verdict"] == "consistent" else "fail"
    distance = state_snapshot["distance_pct"]
    distance_label = percent(distance, signed=True) if distance is not None else "Not available"
    log = ''.join(
        f'<li><small>{text(e["at"])} · {text(e["actor"])}</small>'
        f'<p>{text(e["from"] or "Authored")} → {text(e["to"])}</p><p>{text(e["note"])}</p></li>'
        for e in plan["governance"]["decision_log"]
    )
    html = (
        '<article class="plan-card">' + _fired_band(plan, shocked)
        + '<header class="pc-head">'
        f'<div class="plan-meta">{text(plan["plan_id"])} · {text(plan["client_id"])} '
        f'{badge(plan["state"])} {badge(plan["severity"] + " severity", plan["severity"])}</div>'
        f'<h1>{text(plan["client_name"])}</h1><p class="lead">{text(plan["title"])}</p>'
        + (_signature(plan) if plan["state"] == store.WATCHING else '') + '</header>'
        '<section class="pc-trigger"><h2>Trigger</h2>'
        f'<div class="trigger-expression">{text(trigger["variable"])} {text(trigger["operator"])} '
        f'{state_snapshot["level"]:.2f}</div>'
        f'<p class="caption">{text(trigger["unit"])} · Observed {state_snapshot["observed"]:.2f}'
        f' · Distance {distance_label} · {text(trigger["evaluated_by"])}</p>'
        f'<ol class="derivation">{derivation}</ol></section>'
        '<section class="pc-script"><h2>Client script</h2>'
        f'<blockquote>{text(script["opening"])}</blockquote>{bullets(script["key_points"])}'
        '<div class="script-pair"><div><h3>Likely objection</h3>'
        f'<p>{text(script["likely_objection"])}</p></div><div><h3>Response</h3>'
        f'<p>{text(script["response"])}</p></div></div></section>'
        '<section class="pc-conseq"><h2>Projected consequence</h2>'
        f'<p class="lead">{text(plan["projected_consequence"]["summary"])}</p>'
        f'{item_table(plan["projected_consequence"]["items"])}</section>'
        f'<section class="pc-actions"><h2>Ranked actions</h2>{actions}</section>'
        f'<section class="evidence-section"><h2>Evidence chain</h2>{render_evidence_chain(plan)}</section>'
        '<section class="pc-suit"><h2>Suitability</h2>'
        f'{badge(suitability["verdict"], verdict_kind)}<p>{text(suitability["objective_conflict"])}</p>'
        f'<table class="checks"><thead><tr><th>Check</th><th>Finding</th></tr></thead><tbody>{checks}</tbody></table></section>'
        '<section class="pc-assume"><h2>Assumptions</h2>'
        f'{bullets(plan["assumptions"])}<h3>Confidence {badge(confidence["level"], confidence["level"])}</h3>'
        f'<p>{text(confidence["basis"])}</p><h3>What we would check</h3>'
        f'{bullets(confidence["what_we_would_check"])}</section>'
        f'<details class="decision-log"><summary>Decision log</summary><ol>{log}</ol></details></article>'
    )
    # Markdown must receive a single uninterrupted HTML block, including multiline source prose.
    return ''.join(line.strip() for line in html.splitlines())


def render_board_row(plan, shocked) -> str:
    """shocked carries an observations map produced by engine.evaluate_trigger in app.py."""
    observation = shocked["observations"][plan["plan_id"]]
    distance = observation["distance_pct"]
    label = percent(distance, signed=True) if distance is not None else "Not available"
    # Magnitude is used only for presentation classification, never a financial calculation.
    near = distance is not None and abs(distance) < 10
    return (
        '<article class="board-row"><div class="board-row-top">'
        f'<h3>{text(plan["client_name"])}</h3><span class="distance {"negative" if near else ""}" '
        f'title="Signed distance to trigger">{text(label)}</span></div>'
        f'<p class="board-title" title="{text(plan["title"])}">{text(plan["title"])}</p>'
        f'<div class="plan-meta">{badge(plan["severity"] + " severity", plan["severity"])}'
        f' {badge(plan["state"])}</div></article>'
    )


def render_dial_strip(shocked) -> str:
    rows = ''.join(
        f'<tr><th scope="row">{text(f["facility_id"])}</th><td>{percent(f["ltv"])}</td>'
        f'<td>{percent(f["trigger_ltv"])}</td><td>{money(f["headroom"], f["ccy"], signed=True)}</td>'
        f'<td>{money(f["cure_cash"], f["ccy"])}</td>'
        f'<td>{badge("BREACH", "fail") if f["breached"] else badge("Within trigger", "n/a")}</td></tr>'
        for f in shocked["facilities"].values()
    )
    return (
        '<div class="dial-strip"><table class="facility-table"><thead><tr><th>Facility</th><th>LTV</th>'
        '<th>Trigger</th><th>Headroom</th><th>Cash cure</th><th>Status</th></tr></thead>'
        f'<tbody>{rows}</tbody></table></div>'
    )
