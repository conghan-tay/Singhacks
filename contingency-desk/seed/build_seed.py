#!/usr/bin/env python3
"""Seed the look-through graph. Hand-authored mapping + betas estimated from price history.

Look-through is REFERENCE DATA, not an engine. In a bank, product control maintains this
table. Every row carries a provenance string, and the UI shows it on every hop.
"""
import csv, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HERE = os.path.dirname(os.path.abspath(__file__))
facts = json.load(open(f"{HERE}/../out/facts.json"))
B = {k: v["beta"] for k, v in facts["betas"].items()}

RISK_FACTORS = [
    # id, name, category, observable, current_value, source
    ("BRENT",          "Brent crude USD/bbl",                "Commodity price", "Y", facts["market"]["brent"]["2026-08-26"], "market_context.BRENT_USD_BBL"),
    ("BARA",           "Bara Nusantara Energy Tbk",          "Single name",     "Y", 11340.0, "instruments.price_2026-08-26"),
    ("POS",            "Pacific Orient Shipping Ltd",        "Single name",     "Y", 31.9,    "instruments.price_2026-08-26"),
    ("GEM",            "Global Energy Majors",               "Sector",          "Y", 239.9,   "instruments.price_2026-08-26"),
    ("APAC_SHIPPING",  "Asia Pacific shipping & logistics",  "Sector",          "Y", 130.1,   "instruments.price_2026-08-26"),
    ("HELIOS",         "Helios Cloud Systems Inc",           "Single name",     "Y", 258.7,   "instruments.price_2026-08-26"),
    ("INDONESIAN_COAL","Indonesian coal & energy complex",   "Source of wealth","N", None,    "clients.source_of_wealth"),
    ("GULF_LOGISTICS", "Gulf logistics, ports & chartering", "Source of wealth","N", None,    "clients.source_of_wealth"),
    ("SGD_LOMBARD",    "SGD Lombard funding line",           "Funding",         "Y", None,    "credit_facilities"),
    ("USD_LOMBARD",    "USD Lombard funding line",           "Funding",         "Y", None,    "credit_facilities"),
    ("XAU",            "Gold",                               "Commodity price", "Y", 4622.6,  "market_context.GOLD_USD_OZ"),
    ("US_DURATION",    "US long duration rates",             "Rates",           "Y", 4.66,    "market_context.UST_10Y_PCT"),
]

P_UR   = "instruments.underlying_reference"
P_HOLD = "holdings.instrument_id"
P_SOW  = "clients.source_of_wealth"
P_CF   = "credit_facilities.collateral_portfolio_id"
P_SEC  = "instruments.sector + region (product control mapping)"
P_BETA = "estimated: OLS through origin, 4 snapshot returns vs BRENT"
P_RM   = "RM-authored"

EDGES = [
    # --- source of wealth -------------------------------------------------
    ("source_of_wealth", "CL-0001", "Hartono - inherited family coal mining and energy group", "INDONESIAN_COAL", 1.0, P_SOW,
     "Wealth outside the bank is the same factor as the wealth inside it."),
    ("source_of_wealth", "CL-0019", "Abdullah - Gulf logistics, port services, marine chartering", "GULF_LOGISTICS", 1.0, P_SOW,
     "Operating business benefits from exactly the conditions the portfolio is long."),
    # --- direct holdings --------------------------------------------------
    ("direct", "SYN-ST-0101", "Bara Nusantara Energy Tbk",           "BARA",          1.0, P_HOLD, ""),
    ("direct", "SYN-ST-0104", "Pacific Orient Shipping Ltd",          "POS",           1.0, P_HOLD, ""),
    ("direct", "SYN-ST-0103", "Helios Cloud Systems Inc",             "HELIOS",        1.0, P_HOLD, ""),
    # --- fund look-through ------------------------------------------------
    ("fund_sector", "SYN-EQ-0008", "Global Energy Majors Equity Fund",          "GEM",           1.0, P_SEC, "Sector fund treated as its sector factor."),
    ("fund_sector", "SYN-EQ-0025", "Asia Pacific Shipping and Logistics Fund",  "APAC_SHIPPING", 1.0, P_SEC, "Sector fund treated as its sector factor."),
    ("fund_sector", "SYN-CM-0402", "Gold Bullion ETF",                          "XAU",           1.0, P_SEC, ""),
    # --- structured product look-through ----------------------------------
    ("structured_underlying", "SYN-SP-0505", "FCN ref. Basket C, 9.20% p.a., 12M", "POS",   0.3333, P_UR,
     "Worst-of basket leg 1 of 3. Weights are NOTIONAL SHARE, not risk share - a worst-of pays on the weakest leg."),
    ("structured_underlying", "SYN-SP-0505", "FCN ref. Basket C, 9.20% p.a., 12M", "GEM",   0.3333, P_UR,
     "Worst-of basket leg 2 of 3."),
    ("structured_underlying", "SYN-SP-0505", "FCN ref. Basket C, 9.20% p.a., 12M", "BARA",  0.3333, P_UR,
     "Worst-of basket leg 3 of 3. This leg is also CL-0001's largest direct position and his collateral."),
    ("structured_underlying", "SYN-SP-0502", "ELN ref. Helios Cloud Systems, 11.00% p.a., 6M", "HELIOS", 1.0, P_UR,
     "Single underlying. CL-0002 also holds SYN-ST-0103 directly - same name, twice."),
    # --- collateral -------------------------------------------------------
    ("collateral", "CF-0005", "SGD 8.0m Lombard, margin call at 70% LTV", "SGD_LOMBARD", 1.0, P_CF,
     "Collateral portfolio PF-0002 is 98% Bara. The loan is secured on the concentration."),
    ("collateral", "CF-0001", "USD 6.5m Lombard, margin call at 75% LTV", "USD_LOMBARD", 1.0, P_CF,
     "Collateral portfolio PF-0003 is the technology book."),
    # --- factor -> observable --------------------------------------------
    ("factor", "BARA",            "Bara Nusantara Energy Tbk",             "BRENT", B["SYN-ST-0101"], P_BETA, ""),
    ("factor", "POS",             "Pacific Orient Shipping Ltd",           "BRENT", B["SYN-ST-0104"], P_BETA, ""),
    ("factor", "GEM",             "Global Energy Majors",                  "BRENT", B["SYN-EQ-0008"], P_BETA, ""),
    ("factor", "APAC_SHIPPING",   "Asia Pacific shipping & logistics",     "BRENT", B["SYN-EQ-0025"], P_BETA, ""),
    ("factor", "HELIOS",          "Helios Cloud Systems Inc",              "BRENT", B["SYN-ST-0103"], P_BETA,
     "Negative. Lower energy prices are mildly good for the technology complex - the book is not one-directional."),
    ("factor", "INDONESIAN_COAL", "Indonesian coal & energy complex",      "BRENT", B["SYN-ST-0101"], P_BETA,
     "Proxied by the listed family company. RM-reviewed."),
    ("factor", "GULF_LOGISTICS",  "Gulf logistics, ports & chartering",    "BRENT", B["SYN-ST-0104"], P_BETA,
     "Proxied by charter-rate-sensitive listed shipping. RM-reviewed, low confidence, flagged on screen."),
]

with open(f"{HERE}/risk_factors.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["risk_factor_id","name","category","observable","current_value","source"])
    for r in RISK_FACTORS: w.writerow(r)

with open(f"{HERE}/exposure_edges.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["edge_id","source_type","source_id","source_label","risk_factor_id","weight","provenance","note"])
    for i, e in enumerate(EDGES, 1):
        w.writerow([f"EDG-{i:03d}", e[0], e[1], e[2], e[3], round(e[4], 4), e[5], e[6]])

print(f"{len(RISK_FACTORS)} risk factors, {len(EDGES)} exposure edges")
print("\nHartono's evidence chain (the path the plan card renders):")
for hop in [
    "CL-0001 source_of_wealth -> INDONESIAN_COAL          [clients.source_of_wealth]",
    "  -> SYN-ST-0101 Bara, 41.42% of household, PF-0002  [holdings; CUSTODY - no mandate measures it]",
    "  -> SYN-SP-0505 FCN worst-of leg 3/3, PF-0001       [instruments.underlying_reference]",
    "  -> CF-0005 SGD 8.0m Lombard secured on PF-0002     [credit_facilities]",
    "  -> CN-001 SGD 9.0m property deposit, Mar-Jun 2027  [planned_cash_needs]",
    "  -> BARA beta %.3f to BRENT                          [%s]" % (B["SYN-ST-0101"], "4 snapshot returns"),
]:
    print("   " + hop)
