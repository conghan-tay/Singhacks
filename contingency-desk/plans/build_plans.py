#!/usr/bin/env python3
"""Emit the DRAFTED plan objects. Numbers are computed from out/facts.json; prose is hand-written.

Nothing here runs at demo time - this is the frozen output of J0's overnight authoring pass.
Re-run after verify.py if the underlying data ever changes.
"""
import json, os, sys, hashlib, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
F = json.load(open(f"{HERE}/../out/facts.json"))
B0 = F["market"]["brent"]["2026-08-26"]
CF5 = F["facilities"]["CF-0005"]
H1 = F["clients"]["CL-0001"]; H19 = F["clients"]["CL-0019"]
BETA = {k: v["beta"] for k, v in F["betas"].items()}
AUTHORED = "2026-08-24T03:12:00+08:00"      # the overnight run, two days before today
ARMED_AT = "2026-08-24T08:52:00+08:00"      # Priscilla at her desk the same morning
RM = "priscilla.ong@juliusbaer.com"

# The event that put Brent where it is. event_log.csv is the authoritative record for anything that
# happened in 2026; the trigger is the REVERSAL of a logged event, not a forecast of a new one.
CLOSURE = "2026-03-04"

def brent_for_ltv(ltv_pct):
    lv = CF5["drawn"] / (ltv_pct / 100)
    return B0 * (1 + (lv - CF5["lending_value"]) / CF5["C"])

# Advance rates come from holdings.advance_rate_pct, never from a literal. A cure posted in one
# instrument needs a different amount of market value than the same cure posted in another, and the
# advance rate is the whole of that difference.
AR = {l["instrument_id"]: l["advance_rate"] for l in CF5["legs"]}          # CF-0005 collateral pool
AR.update({p["instrument_id"]: p["advance_rate_pct"] for p in F["positions"]
           if p["client_id"] == "CL-0001"})                                # everything Hartono holds
BARA_AR = AR["SYN-ST-0101"]
TOPUP_ID = "SYN-FI-0208"                  # the daily-liquid PF-0001 line proposed as the cure source
TOPUP = next(p for p in F["positions"] if p["instrument_id"] == TOPUP_ID
             and p["portfolio_id"] == "PF-0001")
TOPUP_AR = TOPUP["advance_rate_pct"]

def at_brent(B):
    """`lv_gap` is the shortfall in LENDING value. Market value needed depends on the advance rate."""
    m = B / B0 - 1
    lv = CF5["lending_value"] + CF5["C"] * m
    gap = CF5["drawn"] / 0.70 - lv
    return {"mult": m, "lending_value": lv, "ltv": 100 * CF5["drawn"] / lv,
            "cure_cash": CF5["drawn"] - 0.70 * lv,
            "lv_gap": gap,
            "topup_bara_mv": gap / (BARA_AR / 100),
            "topup_fi_mv": gap / (TOPUP_AR / 100)}

_PF1 = [p for p in F["positions"] if p["portfolio_id"] == "PF-0001"]
PF1_TOT = sum(p["market_value_base"] for p in _PF1)
PF1_FI = sum(p["market_value_base"] for p in _PF1 if p["asset_class"] == "Fixed Income")

def fi_weight_after(sold):
    """PF-0001 fixed income weight if `sold` of it is liquidated to cure the facility."""
    return 100 * (PF1_FI - sold) / (PF1_TOT - sold)

BARA = next(t for t in H1["top"] if t["instrument_id"] == "SYN-ST-0101")
TRIG = 79.00                      # armed level, rounded down from the derived 78.85
DERIVED = CF5["brent_trigger"]
S = at_brent(TRIG)
PRECONFLICT = F["market"]["brent"]["2026-02-27"]
P = at_brent(PRECONFLICT)
bara_move_79 = BETA["SYN-ST-0101"] * (TRIG / B0 - 1)

ASSUMPTIONS = [
    "Single factor: every move is driven by one Brent shock. Cross-asset and idiosyncratic risk is not modelled.",
    f"Betas are OLS through the origin on the four snapshot-to-snapshot returns (Bara beta {BETA['SYN-ST-0101']:.3f}, R2 {F['betas']['SYN-ST-0101']['r2']:.2f}). Four observations is an assumption, not a risk model.",
    "FX held at 2026-08-26. A Brent fall would plausibly move USDIDR, which moves the SGD value of the Bara collateral. Not modelled.",
    "instruments.csv gives no barrier or strike for SYN-SP-0505, so no knock-in is modelled and none is assumed.",
]

# ---------------------------------------------------------------- PLAN-001
plan1 = {
  "plan_id": "PLAN-001", "client_id": "CL-0001", "client_name": H1["name"],
  "portfolio_ids": ["PF-0001", "PF-0002"],
  "title": "Strait reopens: CF-0005 margin call on the Bara collateral",
  "severity": "high", "state": "DRAFTED",
  "authored": {"by": "contingency-desk-authoring-agent", "at": AUTHORED, "based_on_snapshot": "2026-08-26"},
  "trigger": {
    "expression": f"BRENT < {TRIG:.2f}", "variable": "BRENT", "operator": "<",
    "level": TRIG, "unit": "USD/bbl", "current_value": B0,
    "distance_pct": round(100 * (TRIG / B0 - 1), 2), "evaluated_by": "deterministic",
    "derivation": [
      {"step": "Facility CF-0005 drawn", "value": f"SGD {CF5['drawn']:,.0f}", "source": "credit_facilities.drawn_2026-08-26"},
      {"step": "Margin-call LTV", "value": f"{CF5['trigger_ltv']:.0f}%", "source": "credit_facilities.margin_call_ltv_pct"},
      {"step": "Lending value required at trigger", "value": f"SGD {CF5['drawn']:,.0f} / 0.70 = SGD {CF5['lending_value_at_trigger']:,.0f}", "source": "arithmetic"},
      {"step": "Lending value today", "value": f"SGD {CF5['lending_value']:,.0f}", "source": "holdings.lending_value_base, PF-0002"},
      {"step": "Collateral pool must fall", "value": f"{100*CF5['collateral_move_required']:.2f}%", "source": "arithmetic"},
      {"step": "Pool composition", "value": "Bara SGD 26,077,344 @ 50% advance + USD Call Deposit SGD 540,800 @ 90%", "source": "holdings.advance_rate_pct"},
      {"step": "Bara beta to Brent", "value": f"{BETA['SYN-ST-0101']:.3f} (R2 {F['betas']['SYN-ST-0101']['r2']:.2f}, 4 snapshot returns)", "source": "instruments price history"},
      {"step": "Implied Brent level", "value": f"USD {DERIVED:.2f}", "source": "arithmetic"},
      {"step": "Armed at", "value": f"USD {TRIG:.2f} (rounded down for margin)", "source": "RM"},
      {"step": "Reference: Brent before the conflict, 2026-02-27", "value": f"USD {PRECONFLICT:.2f}", "source": "market_context.BRENT_USD_BBL"},
    ]},
  "evidence_chain": [
    {"kind":"source_of_wealth","ref":"CL-0001","label":"Inherited - family coal mining and energy group",
     "detail":"Wealth outside the bank is the same factor as the wealth inside it.","provenance":"clients.source_of_wealth","source_file":"clients.csv","confidence":"high"},
    {"kind":"direct","ref":"SYN-ST-0101","label":f"Bara Nusantara Energy Tbk - USD {BARA['usd']:,.0f} = {BARA['pct_household']:.2f}% of household wealth",
     "detail":"Held in PF-0002, a CUSTODY account. Mandate bands do not measure custody accounts, so this concentration appears on no mandate report.","provenance":"holdings.instrument_id + portfolios.service_model","source_file":"holdings.csv","confidence":"high"},
    {"kind":"structured_underlying","ref":"SYN-SP-0505","label":"Worst-of leg 3 of 3 in the Fixed Coupon Note held in PF-0001",
     "detail":"USD 1,662,484 = 6.18% of PF-0001, and 100% of its Structured Products allocation. The other two legs, Pacific Orient Shipping and Global Energy Majors, are the same trade. A three-name basket that is one factor.","provenance":"instruments.underlying_reference","source_file":"instruments.csv","confidence":"high"},
    {"kind":"collateral","ref":"CF-0005","label":f"SGD {CF5['drawn']:,.0f} Lombard secured on PF-0002, margin call at {CF5['trigger_ltv']:.0f}%",
     "detail":f"LTV {CF5['ltv_now']:.2f}% today. It was 78.50% at 2025-12-31 - already through the trigger - and was cured by the energy rally, not by a decision.","provenance":"credit_facilities.collateral_portfolio_id","source_file":"credit_facilities.csv","confidence":"high"},
    {"kind":"cash_need","ref":"CN-001","label":"SGD 9,000,000 Singapore property deposit, 2027-03-01 to 2027-06-30, Likely",
     "detail":"Corroborated by the RM note of 2026-04-14. Any cure funded from PF-0001 competes with this.","provenance":"planned_cash_needs","source_file":"planned_cash_needs.csv","confidence":"high"},
    {"kind":"rm_note","ref":"N-002","label":"2026-04-14 - he asked what gives him more energy exposure; he subscribed the next day","detail":"The concentration is not drift. The bank sold him more of the factor he was already long, four months ago, and recorded the conversation that did it.","provenance":"rm_notes.json note_id N-002","source_file":"rm_notes.json","confidence":"high"},
    {"kind":"factor","ref":"BRENT","label":f"Bara beta {BETA['SYN-ST-0101']:.3f} to Brent",
     "detail":f"OLS through origin, 4 snapshot returns, R2 {F['betas']['SYN-ST-0101']['r2']:.2f}.","provenance":"estimated from instruments price history","source_file":"instruments.csv","confidence":"medium"},
    {"kind":"event","ref":CLOSURE,"label":"2026-03-04 - Strait of Hormuz effectively closed; Brent surges past USD 120","detail":"Brent is at 101.50 because of a logged event. The trigger is that event reversing, not a new one being forecast - which is why the level can be derived instead of predicted.","provenance":"event_log.csv event_date - the authoritative record for 2026","source_file":"event_log.csv","confidence":"high"},
  ],
  "projected_consequence": {
    "summary": (f"At Brent {TRIG:.0f}, Bara falls {100*bara_move_79:.1f}% and CF-0005 reaches "
                f"{S['ltv']:.2f}% LTV against a {CF5['trigger_ltv']:.0f}% trigger. The direct position loses "
                f"USD {abs(BARA['usd']*bara_move_79):,.0f}. The same move takes the note's three worst-of legs "
                f"down together, because they are one trade."),
    "household_delta_usd": round(F["scenario_brent_79"]["clients"]["CL-0001"]["usd_delta"], 0),
    "household_delta_pct": round(100 * F["scenario_brent_79"]["clients"]["CL-0001"]["usd_delta"] / H1["household_usd"], 2),
    "items": [
      {"label":"CF-0005 LTV","value":f"{CF5['ltv_now']:.2f}% -> {S['ltv']:.2f}% (trigger {CF5['trigger_ltv']:.0f}%)","basis":"lending value recomputed at the shocked Bara price"},
      {"label":"Lending value","value":f"SGD {CF5['lending_value']:,.0f} -> SGD {S['lending_value']:,.0f}","basis":"holdings.lending_value_base x beta shock"},
      {"label":"Bara direct position","value":f"{100*bara_move_79:.2f}% = USD {BARA['usd']*bara_move_79:,.0f}","basis":"beta x Brent move"},
      {"label":"Household impact","value":f"USD {F['scenario_brent_79']['clients']['CL-0001']['usd_delta']:,.0f} ({100*F['scenario_brent_79']['clients']['CL-0001']['usd_delta']/H1['household_usd']:.2f}% of wealth)","basis":"all positions revalued at their own Brent beta"},
      {"label":f"At the pre-conflict Brent level ({PRECONFLICT:.2f})","value":f"LTV {P['ltv']:.2f}%, cure = SGD {P['cure_cash']:,.0f} cash, or SGD {P['lv_gap']:,.0f} of additional lending value","basis":"same engine, dial set to the 2026-02-27 observation"},
      {"label":"What that cure costs in market value","value":f"SGD {P['topup_bara_mv']:,.0f} of Bara at its {BARA_AR:.0f}% advance rate, or SGD {P['topup_fi_mv']:,.0f} of {TOPUP_ID} at {TOPUP_AR:.0f}%","basis":"holdings.advance_rate_pct - the advance rate, not the shortfall, decides how much stock a cure costs"},
    ]},
  "actions": [
    {"rank":1,"action":f"Pre-agree a cure path now: earmark SGD {P['topup_fi_mv']:,.0f} of PF-0001 short-duration fixed income ({TOPUP_ID}, {TOPUP_AR:.0f}% advance rate) as the collateral top-up, documented before the trigger.",
     "rationale":"The cure is small if it is prepared and expensive if it is improvised. Deciding the source of funds while the client is calm is the entire point of arming a plan.",
     "second_order":f"The holding is SGD {TOPUP['market_value_base']:,.0f} and daily-liquid, so the earmark is covered. Pledging it does not move the mandate; liquidating it to cure takes PF-0001 fixed income from {100*PF1_FI/PF1_TOT:.2f}% to {fi_weight_after(P['topup_fi_mv']):.2f}%, still inside the 15-40% band. Either way it is the same liquidity CN-001 needs in March 2027.",
     "reversible":True,"requires":["Client acknowledgement","Credit desk note on CF-0005","Extension of the CF-0005 collateral pool from PF-0002 to PF-0001"]},
    {"rank":2,"action":"Reduce the FCN (SYN-SP-0505) position in PF-0001 at or before the next coupon.",
     "rationale":"It is the only holding that is simultaneously inside the mandate and referencing the collateral. Selling it lowers correlated exposure without touching the shareholding he will not discuss.",
     "second_order":"Forfeits the 9.20% coupon and crystallises against a note bought in April. He subscribed to it four months ago on his own view; expect resistance.",
     "reversible":False,"requires":["Advisory suitability sign-off","Secondary market bid"]},
    {"rank":3,"action":"Reduce the Bara shareholding in PF-0002 by SGD 3-4m.",
     "rationale":"The only action that addresses the 41.42% concentration itself rather than its symptoms.",
     "second_order":"He refused this on 2026-01-08 and said it would be read as a signal by his uncles. Raising it before a margin call is a different conversation from raising it during one - which is the argument for having it now.",
     "reversible":False,"requires":["Client mandate","Family governance discussion"]},
    {"rank":4,"action":"Do nothing and monitor.",
     "rationale":"Defensible: the facility has 10.85 points of headroom today and cured itself once already.",
     "second_order":"It cured by luck, not by decision. If Brent normalises before March 2027 the cure and the CN-001 deposit collide.",
     "reversible":True,"requires":[]},
  ],
  "client_script": {
    "opening":"When we spoke in April you asked what gives you more exposure to the energy rally. I want to show you what the same position does if the rally ends - because that is the case we have not talked about.",
    "key_points":[
      "Your mandate report is green in every band. That is accurate, and it is also incomplete: the Bara shareholding sits in the custody account, which no mandate measures. Across both accounts it is 41% of your wealth with us.",
      "The note you subscribed in April references three names. Two of them are shipping and energy, and the third is Bara. If the Strait reopens, all three move down together - the basket is one trade, not three.",
      "The loan is secured on the Bara shares. If Brent goes back to roughly where it was in February - 72, before any of this started - the facility goes to about 74% against a 70% margin call.",
      "I am not forecasting that. I am saying we should decide today where the money comes from if it happens, rather than deciding it in a phone call on the day.",
    ],
    "likely_objection":"He will say he is not selling the family shareholding, and that reducing it would be read as a signal by his uncles.",
    "response":"Then we do not touch it. We pre-agree the collateral top-up from the mandate portfolio and we take the correlated exposure down inside the mandate instead - which is the part he did not inherit and has no family view on.",
  },
  "suitability": {
    "mandate_code":"BALG","risk_profile":H1["risk_profile"],"risk_tolerance":H1["risk_tolerance"],
    "verdict":"conflicts_with_stated_objective",
    "objective_conflict":"Stated objective is to 'diversify away from the family operating business'. The 2026-04-15 FCN subscription increased exposure to it, and the loan is secured on it.",
    "checks":[
      {"check":"PF-0001 asset-class bands (BALG)","result":"pass","detail":"Equity 50.14% (40-65), FI 25.17% (15-40), Alt 7.19% (0-25), Comm 6.35% (0-10), SP 6.18% (0-15), Cash 4.95% (2-15)"},
      {"check":"Single-position limit 15% within PF-0001","result":"pass","detail":"Largest is SYN-EQ-0001 at 19.6% of PF-0001 - a diversified index fund, not a single name"},
      {"check":"Household single-name concentration","result":"not_measured","detail":"41.42% in SYN-ST-0101. PF-0002 is a custody account, so no mandate limit applies. This is the finding."},
      {"check":"Look-through concentration incl. structured products","result":"fail","detail":"Bara appears directly and as a worst-of leg of SYN-SP-0505"},
      {"check":"Liquidity vs planned cash needs","result":"fail","detail":"CN-001 SGD 9m due Mar-Jun 2027 competes with any collateral cure"},
      {"check":"Risk tolerance 6 of 10 vs single-name concentration","result":"fail","detail":"41% in one emerging-market single name is not a tolerance-6 exposure"},
    ]},
  "assumptions": ASSUMPTIONS,
  "confidence": {"level":"medium",
    "basis":"The LTV arithmetic, the advance rates and the look-through mapping are exact and come straight from the files. The Brent level depends on a single-factor beta estimated from four observations.",
    "what_we_would_check":[
      "USDIDR sensitivity - the collateral is IDR-denominated and reported in SGD, so FX moves the LTV independently of the Bara price",
      "The FCN barrier and strike, which the dataset does not provide",
      "Whether the 50% advance rate on Bara is reviewed if concentration rises",
      "Whether the family group has debt of its own secured on the same shares",
    ]},
  "governance": {"armed_by":None,"armed_at":None,"armed_signature":None,"armed_trigger_level":None,
    "fired_at":None,"fired_observation":None,"resolution":None,"resolution_reason":None,
    "decision_log":[{"at":AUTHORED,"actor":"contingency-desk-authoring-agent","from":None,"to":"DRAFTED","note":"Overnight scenario walk: Strait reopens"}]},
}

# ---------------------------------------------------------------- PLAN-002
LTV_WARN = 65.0
B_WARN = brent_for_ltv(LTV_WARN)
W = at_brent(B_WARN)
plan2 = {
  "plan_id":"PLAN-002","client_id":"CL-0001","client_name":H1["name"],"portfolio_ids":["PF-0001","PF-0002"],
  "title":"Early warning: protect the CN-001 property deposit before the facility tightens",
  "severity":"medium","state":"DRAFTED",
  "authored":{"by":"contingency-desk-authoring-agent","at":AUTHORED,"based_on_snapshot":"2026-08-26"},
  "trigger":{"expression":f"CF-0005.LTV > {LTV_WARN:.1f}","variable":"CF-0005.LTV","operator":">",
    "level":LTV_WARN,"unit":"%","current_value":round(CF5["ltv_now"],2),
    "distance_pct":round(100*(LTV_WARN/CF5["ltv_now"]-1),2),"evaluated_by":"deterministic",
    "derivation":[
      {"step":"Trigger is on a metric the bank already monitors daily","value":"facility LTV, not a market forecast","source":"credit_facilities"},
      {"step":"Current LTV","value":f"{CF5['ltv_now']:.2f}%","source":"credit_facilities.ltv_pct_2026-08-26"},
      {"step":"Warning level","value":f"{LTV_WARN:.0f}% - five points before the {CF5['trigger_ltv']:.0f}% margin call","source":"RM-set"},
      {"step":"Equivalent Brent level","value":f"USD {B_WARN:.2f}","source":"arithmetic, for context only"},
      {"step":"CN-001 window opens","value":"2027-03-01","source":"planned_cash_needs"},
    ]},
  "evidence_chain":[
    {"kind":"collateral","ref":"CF-0005","label":f"SGD {CF5['drawn']:,.0f} drawn, LTV {CF5['ltv_now']:.2f}%","detail":"Secured on PF-0002, which is 98% Bara.","provenance":"credit_facilities","source_file":"credit_facilities.csv","confidence":"high"},
    {"kind":"cash_need","ref":"CN-001","label":"SGD 9,000,000 property deposit, 2027-03-01 to 2027-06-30","detail":"Certainty: Likely. RM note 2026-04-14 confirms a Bukit Timah property, around SGD 9m.","provenance":"planned_cash_needs","source_file":"planned_cash_needs.csv","confidence":"high"},
    {"kind":"direct","ref":"PF-0001","label":"The only realistic source of both the deposit and any collateral cure","detail":"PF-0002 cannot fund either without selling the shareholding he has refused to reduce.","provenance":"holdings + portfolios.service_model","source_file":"holdings.csv","confidence":"high"},
  ],
  "projected_consequence":{
    "summary":(f"If the facility reaches {LTV_WARN:.0f}% LTV, the cure and the SGD 9m deposit draw on the same "
               f"portfolio within months of each other. Funding both from PF-0001 leaves the household MORE "
               f"concentrated in Bara, not less - the diversified assets are the ones that get sold."),
    "items":[
      {"label":"Deposit due","value":"SGD 9,000,000, Mar-Jun 2027","basis":"planned_cash_needs CN-001"},
      {"label":"Liquid mandate assets, PF-0001","value":"SGD 36.3m across daily-liquid funds and cash","basis":"holdings.liquidity_tier, PF-0001 at 2026-08-26"},
      {"label":"Concentration after funding both from PF-0001","value":"Bara rises above 41.42% of household wealth","basis":"numerator unchanged, denominator falls"},
    ]},
  "actions":[
    {"rank":1,"action":"Ring-fence SGD 9m of PF-0001 daily-liquid assets against CN-001 now, and exclude them from the CF-0005 cure path.",
     "rationale":"Two claims on one pool is the actual risk. Naming which assets serve which claim removes it.",
     "second_order":"Constrains rebalancing inside PF-0001 for six months.","reversible":True,"requires":["Client agreement"]},
    {"rank":2,"action":"Repay SGD 2m of CF-0005 from PF-0001 cash, taking LTV to roughly 44%.",
     "rationale":"Buys headroom ahead of both events.","second_order":"Gives up the leverage he took the facility for, and he is currently positive on energy.","reversible":True,"requires":["Client agreement"]},
    {"rank":3,"action":"Bring the deposit forward or fund it from outside the bank.",
     "rationale":"Removes the collision entirely.","second_order":"Outside our visibility; may not be available. Requires asking about family group liquidity, which touches the topic he closed down in January.","reversible":True,"requires":["Client disclosure"]},
  ],
  "client_script":{
    "opening":"You mentioned the Bukit Timah deposit in April - around SGD 9m, early next year. I want to make sure that money and the loan are not queuing for the same assets.",
    "key_points":[
      "The deposit and any top-up on the loan would both come out of the managed portfolio.",
      "If we fund both from there, the share of your wealth sitting in the family company goes up, not down - which is the opposite of what you asked this relationship to do.",
      "We can ring-fence the deposit now and it costs you nothing.",
    ],
    "likely_objection":"That the loan is comfortable today at 59%.","response":"It is. It was also 78.5% in December, and it came back down because coal prices rose, not because we did anything. I would rather not depend on that twice."},
  "suitability":{"mandate_code":"BALG","risk_profile":H1["risk_profile"],"risk_tolerance":H1["risk_tolerance"],
    "verdict":"consistent","objective_conflict":"",
    "checks":[
      {"check":"Liquidity coverage for CN-001","result":"pass","detail":"PF-0001 holds sufficient daily-liquid assets today"},
      {"check":"Liquidity coverage for CN-001 AND a CF-0005 cure","result":"fail","detail":"Both claims land within the same two quarters"},
      {"check":"Effect on stated objective","result":"fail","detail":"Funding both from PF-0001 increases relative concentration in the operating business"},
    ]},
  "assumptions":ASSUMPTIONS,
  "confidence":{"level":"high","basis":"Trigger is on a facility metric the bank computes daily. No market forecast is involved.",
    "what_we_would_check":["Whether CN-001 is contractually committed or still indicative","Whether the property purchase can be debt-financed separately"]},
  "governance":{"armed_by":None,"armed_at":None,"armed_signature":None,"armed_trigger_level":None,
    "fired_at":None,"fired_observation":None,"resolution":None,"resolution_reason":None,
    "decision_log":[{"at":AUTHORED,"actor":"contingency-desk-authoring-agent","from":None,"to":"DRAFTED","note":"Liquidity collision detected between CN-001 and the CF-0005 cure path"}]},
}

# ---------------------------------------------------------------- PLAN-003
blk = H19["shipping_energy_block"]
d19 = F["scenario_brent_79"]["clients"]["CL-0019"]
moves19 = {m["instrument_id"]: m for m in d19["moves"]}
plan3 = {
  "plan_id":"PLAN-003","client_id":"CL-0019","client_name":H19["name"],"portfolio_ids":["PF-0023"],
  "title":"Strait reopens: the Asia portfolio and the Gulf business fall together",
  "severity":"high","state":"DRAFTED",
  "authored":{"by":"contingency-desk-authoring-agent","at":AUTHORED,"based_on_snapshot":"2026-08-26"},
  "trigger":{"expression":f"BRENT < {TRIG:.2f}","variable":"BRENT","operator":"<","level":TRIG,"unit":"USD/bbl",
    "current_value":B0,"distance_pct":round(100*(TRIG/B0-1),2),"evaluated_by":"deterministic",
    "derivation":[
      {"step":"Same trigger as PLAN-001","value":f"BRENT < {TRIG:.2f}","source":"shared risk factor"},
      {"step":"Why the same level","value":"Both clients hold SYN-SP-0505. It is held by exactly two clients in the book.","source":"holdings.csv"},
      {"step":"Identified block","value":f"USD {blk['usd']:,.0f} = {blk['pct']:.2f}% of household wealth","source":"holdings, 4 instruments"},
    ]},
  "evidence_chain":[
    {"kind":"rm_note","ref":"N-026","label":"2026-08-12 - he asked what happens to his portfolio if the Strait reopens. Priscilla wrote: 'We have not modelled this.'","detail":"This plan is that answer. The client asked for it twelve days before it was authored.","provenance":"rm_notes.json note_id N-026","source_file":"rm_notes.json","confidence":"high"},
    {"kind":"source_of_wealth","ref":"CL-0019","label":"Entrepreneur - Gulf logistics, port services and marine chartering","detail":"Charter rates are elevated because the Strait is closed. The operating business is long the same event as the portfolio.","provenance":"clients.source_of_wealth","source_file":"clients.csv","confidence":"high"},
    {"kind":"direct","ref":"SYN-ST-0104","label":f"Pacific Orient Shipping Ltd - {[t for t in H19['top'] if t['instrument_id']=='SYN-ST-0104'][0]['pct_household']:.2f}% of household","detail":"Also a worst-of leg of the note below.","provenance":"holdings.instrument_id","source_file":"holdings.csv","confidence":"high"},
    {"kind":"fund_sector","ref":"SYN-EQ-0008","label":f"Global Energy Majors Equity Fund - {[t for t in H19['top'] if t['instrument_id']=='SYN-EQ-0008'][0]['pct_household']:.2f}% of household","detail":"Also a worst-of leg of the note below.","provenance":"instruments.sector (product control mapping)","source_file":"instruments.csv","confidence":"high"},
    {"kind":"structured_underlying","ref":"SYN-SP-0505","label":"FCN worst-of: Pacific Orient Shipping / Global Energy Majors / Bara Nusantara","detail":"Two of the three legs are positions he already holds outright. The note doubles them rather than diversifying.","provenance":"instruments.underlying_reference","source_file":"instruments.csv","confidence":"high"},
    {"kind":"factor","ref":"BRENT","label":"All four exposures load on one factor","detail":f"Betas: POS {BETA['SYN-ST-0104']:.2f}, GEM {BETA['SYN-EQ-0008']:.2f}, APAC Shipping {BETA['SYN-EQ-0025']:.2f}, FCN {BETA['SYN-SP-0505']:.2f}.","provenance":"estimated from instruments price history","source_file":"instruments.csv","confidence":"medium"},
    {"kind":"cash_need","ref":"CN-017","label":"USD 5,000,000 Singapore family office seed capital, 2027","detail":"Funded from the same portfolio.","provenance":"planned_cash_needs","source_file":"planned_cash_needs.csv","confidence":"high"},
    {"kind":"event","ref":CLOSURE,"label":"2026-03-04 - Strait of Hormuz effectively closed; Brent surges past USD 120","detail":"The same logged event is long his portfolio and long his operating business. Both sides of his balance sheet are one trade on one event.","provenance":"event_log.csv event_date - the authoritative record for 2026","source_file":"event_log.csv","confidence":"high"},
  ],
  "projected_consequence":{
    "summary":(f"At Brent {TRIG:.0f} the identified block falls about USD {abs(d19['usd_delta']):,.0f} "
               f"({abs(100*d19['usd_delta']/H19['household_usd']):.2f}% of wealth) at the same moment charter rates "
               f"normalise against the business that funds him. The loss size is not the point - the correlation is."),
    "household_delta_usd": round(d19["usd_delta"], 0),
    "household_delta_pct": round(100 * d19["usd_delta"] / H19["household_usd"], 2),
    "items":[
      {"label":"Shipping and energy block","value":f"USD {blk['usd']:,.0f} = {blk['pct']:.2f}% of household wealth","basis":"SYN-SP-0505, SYN-ST-0104, SYN-EQ-0008, SYN-EQ-0025"},
      {"label":"Pacific Orient Shipping","value":f"{moves19['SYN-ST-0104']['pct']:.2f}% = USD {moves19['SYN-ST-0104']['usd_delta']:,.0f}","basis":f"beta {BETA['SYN-ST-0104']:.2f}"},
      {"label":"Global Energy Majors","value":f"{moves19['SYN-EQ-0008']['pct']:.2f}% = USD {moves19['SYN-EQ-0008']['usd_delta']:,.0f}","basis":f"beta {BETA['SYN-EQ-0008']:.2f}"},
      {"label":"Asia Pacific Shipping and Logistics","value":f"{moves19['SYN-EQ-0025']['pct']:.2f}% = USD {moves19['SYN-EQ-0025']['usd_delta']:,.0f}","basis":f"beta {BETA['SYN-EQ-0025']:.2f}"},
      {"label":"FCN SYN-SP-0505","value":f"{moves19['SYN-SP-0505']['pct']:.2f}% = USD {moves19['SYN-SP-0505']['usd_delta']:,.0f}","basis":"measured beta only - no barrier is modelled because the dataset gives none"},
      {"label":"Operating business","value":"Charter rates normalise at the same time","basis":"Not quantified. Stated, not modelled."},
    ]},
  "actions":[
    {"rank":1,"action":"Model the reopening scenario and take it to him - he asked for exactly this on 2026-08-12.",
     "rationale":"His note says 'We have not modelled this.' The answer is the deliverable.","second_order":"It will show that the portfolio he asked to be uncorrelated is 42% one factor. That is a difficult conversation, and it is the one he requested.","reversible":True,"requires":[]},
    {"rank":2,"action":"Reduce SYN-ST-0104 and SYN-EQ-0008 - the two positions doubled by the note - by roughly a third.",
     "rationale":"Removes the doubling without unwinding the note or crystallising the coupon.","second_order":"Realises gains: both names are well up since February. Tax domicile UAE, so no capital gains drag.","reversible":False,"requires":["Advisory suitability sign-off"]},
    {"rank":3,"action":"Redirect the CN-017 family office seed capital away from the block on funding.",
     "rationale":"The next USD 5m is the cheapest diversification available - it has not been invested yet.","second_order":"Delays deployment while a target allocation is agreed.","reversible":True,"requires":["Client agreement"]},
    {"rank":4,"action":"Hold. He is positive on the sector and the note pays 9.20%.",
     "rationale":"His view has been right since February.","second_order":"Concentrates the household on the outcome of one geopolitical event, on both sides of his balance sheet.","reversible":True,"requires":[]},
  ],
  "client_script":{
    "opening":"You asked in August what happens to the portfolio if the Strait reopens. We have modelled it. The answer is that the portfolio and the business move the same way, at the same time.",
    "key_points":[
      "Four positions - the note, Pacific Orient, the energy fund and the shipping fund - are 42% of the portfolio and they are one bet.",
      "Two of them appear twice: you own them outright and the note references them again.",
      "The reopening is the good outcome for the world and a bad one for this portfolio, at the same moment your charter rates normalise.",
      "You told us in April that the point of this portfolio was to be uncorrelated with the Gulf business. Today it is not, and this is how we fix it.",
    ],
    "likely_objection":"That his view on charter rates has been right, and the note pays 9.20%.",
    "response":"It has been right. The issue is not the view, it is that you are expressing it three times - here, in the note, and in the business. We can keep the view and hold it once."},
  "suitability":{"mandate_code":"BALG","risk_profile":H19["risk_profile"],"risk_tolerance":H19["risk_tolerance"],
    "verdict":"conflicts_with_stated_objective",
    "objective_conflict":"Stated objective: 'Build wealth outside the Gulf region and outside the shipping sector.' 42.13% of the portfolio is shipping and energy, two names of it held twice.",
    "checks":[
      {"check":"PF-0023 asset-class bands (BALG)","result":"pass","detail":"Within bands at 2026-08-26"},
      {"check":"Single-position limit 15%","result":"pass","detail":"Largest single line is 13.30%"},
      {"check":"Look-through factor concentration","result":"fail","detail":"42.13% on one factor once the worst-of legs are unpacked"},
      {"check":"Correlation with source of wealth","result":"fail","detail":"Portfolio and operating business are long the same event"},
      {"check":"Alignment with stated objective","result":"fail","detail":"Directly contradicts the objective recorded in clients.csv and repeated in the RM note of 2026-04-15"},
    ]},
  "assumptions":ASSUMPTIONS,
  "confidence":{"level":"medium",
    "basis":"Holdings, weights and the worst-of composition are exact. The factor loadings are estimated from four observations. The operating-business link is qualitative and RM-authored, not modelled.",
    "what_we_would_check":["Actual charter-rate sensitivity of his business rather than a listed-shipping proxy","The FCN barrier, which the dataset does not provide","Whether the family office entity will hold assets correlated with the same factor"]},
  "governance":{"armed_by":None,"armed_at":None,"armed_signature":None,"armed_trigger_level":None,
    "fired_at":None,"fired_observation":None,"resolution":None,"resolution_reason":None,
    "decision_log":[{"at":AUTHORED,"actor":"contingency-desk-authoring-agent","from":None,"to":"DRAFTED","note":"Same scenario walk as PLAN-001; shared instrument SYN-SP-0505"}]},
}

# Hop numbers are derived from position, never hand-maintained. This has to happen BEFORE arming:
# the signature covers the whole body, so anything that touches it afterwards invalidates the record.
# (It did, the first time. The check caught it, which is the point of having one.)
for p in (plan1, plan2, plan3):
    for i, hop in enumerate(p["evidence_chain"], 1):
        hop["hop"] = i

# PLAN-003 ships already armed. PLAN-001 stays DRAFTED so the RM arms it live: one card proves the
# mechanism, the other proves the artefact - a signature written twelve days before the market moved.
sys.path.insert(0, os.path.dirname(HERE))
import store
plan3 = store.arm(plan3, RM, at=ARMED_AT,
                  note="Reviewed the overnight walk; armed unchanged at the drafted level")
assert store.verify_signature(plan3)["ok"], "the seeded arming record must verify as written"

for p in (plan1, plan2, plan3):
    with open(f"{HERE}/{p['plan_id']}.json", "w") as fh:
        json.dump(p, fh, indent=2)
    print(f"{p['plan_id']}  {p['state']:8s} {p['trigger']['expression']:22s} {p['title']}")
print(f"\nderived Brent trigger {DERIVED:.2f}, armed at {TRIG:.2f}; LTV at 79 = {S['ltv']:.2f}%, at pre-conflict 72.40 = {P['ltv']:.2f}%")
