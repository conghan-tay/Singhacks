==============================================================================
FILES LOADED
==============================================================================
  clients                   20 rows   25 columns
  portfolios                24 rows   15 columns
  holdings                1015 rows   26 columns
  instruments               62 rows   16 columns
  mandates                  48 rows    8 columns
  transactions             393 rows   13 columns
  credit_facilities          5 rows   34 columns
  commitments                5 rows    9 columns
  planned_cash_needs        20 rows    9 columns
  market_context           115 rows    7 columns
  event_log                 16 rows    6 columns
  rm_notes                  28 notes

  Snapshot dates: 2025-12-31, 2026-02-27, 2026-03-31, 2026-06-30, 2026-08-26
  'Today' in this dataset: 2026-08-26

==============================================================================
THE BOOK  (20 clients, one relationship manager)
==============================================================================
ID       Client                       AUM USDm  Band  Ctr Life stage
------------------------------------------------------------------------------
CL-0017  Fong Enterprises Family Of       87.9  UHNW  Ho  Multi-generational - G2 and G3
CL-0002  Ravi Chandrasekaran              46.7  UHNW  Si  Pre-liquidity event
CL-0001  Hartono Wijaya Kusuma            46.6  UHNW  Si  Wealth accumulation - second g
CL-0007  Alistair Pemberton-Hale          40.0  UHNW  Si  Retired - legacy and philanthr
CL-0013  Zhang Meiling                    37.0  UHNW  Ho  Wealth accumulation
CL-0011  Tan Boon Huat                    35.3  UHNW  Si  Succession and estate planning
CL-0004  Chalermchai Suphanburi           33.5  UHNW  Si  Pre-retirement
CL-0019  Abdullah Al-Mansoori             32.2  UHNW  Ho  Peak earning years
CL-0009  Andreas Lindqvist                31.6  UHNW  Si  Post-liquidity event
CL-0012  Cheung Kwok Wing                 28.0  UHNW  Ho  Retired
CL-0014  Lau Chi Ming                     26.5  UHNW  Ho  Peak earning years
CL-0018  Elena Marchetti-Wong             22.6  HNW   Ho  Peak earning years
CL-0003  Margarethe Voss-Brenner          22.2  HNW   Si  Recently inherited - transitio
CL-0005  Aishah binti Rahman              19.4  HNW   Si  Peak earning years
CL-0020  Grace Adeyemi-Lim                19.1  HNW   Ho  Wealth accumulation
CL-0006  Nguyen Thi Bao Tran              18.1  HNW   Si  Wealth accumulation
CL-0015  Kim Do-Yoon                      15.0  HNW   Ho  Wealth accumulation
CL-0016  Yamamoto Kenji                   14.5  HNW   Ho  Pre-retirement
CL-0008  Chen Wei Ling                    12.0  HNW   Si  Peak earning years
CL-0010  Priya Nair Menon                  8.2  HNW   Si  Early career - next generation
------------------------------------------------------------------------------
         TOTAL                           596.2

==============================================================================
WHAT HAPPENED IN 2026  (event_log.csv is the authoritative source)
==============================================================================
  2025-12-31  [High  ] Gold closes 2025 up roughly 64% for the year after breaching USD 3,000 and USD 4,000 for
  2026-01-26  [High  ] Spot gold trades above USD 5,000 per ounce for the first time.
  2026-01-28  [High  ] Gold prints an intraday all-time high near USD 5,589 per ounce, then begins a multi-mont
  2026-02-28  [Severe] United States and Israel commence military operations against Iran.
  2026-03-02  [High  ] Brent crude rises 10-13% to around USD 80-82 per barrel as tanker traffic in the Strait 
  2026-03-04  [Severe] Strait of Hormuz effectively closed. Brent surges past USD 120. QatarEnergy declares for
  2026-03-11  [High  ] IEA member countries agree to release 400 million barrels from emergency reserves.
  2026-03-12  [Severe] IEA characterises the conflict as the largest supply disruption in the history of the gl
  2026-04-30  [Medium] European Central Bank and several other central banks raise policy rates in response to 
  2026-05-04  [High  ] Brent crude peaks at approximately USD 114 per barrel.
  2026-06-05  [High  ] Megacap technology complex briefly sheds around USD 2 trillion in market value on AI cap
  2026-06-17  [High  ] Federal Reserve holds the target range at 3.50-3.75% at the first meeting under new Chai
  2026-06-19  [High  ] US 10-year Treasury yield rises to about 4.46%, near its highest level in more than a ye
  2026-06-30  [Medium] Half-year close. US equities near record levels on narrow, technology-led leadership. No
  2026-07-29  [High  ] Federal Reserve holds again at 3.50-3.75% with three dissents. US 10-year yield reaches 
  2026-08-05  [Severe] United States reimposes a naval blockade following renewed Iranian attacks on commercial

==============================================================================
MARKET CONTEXT AT EACH SNAPSHOT
==============================================================================
snapshot_date  2025-12-31  2026-02-27  2026-03-31  2026-06-30  2026-08-26
series_id                                                                
SPX               6902.00     7180.00    7050.000    7410.000    7530.000
GOLD_USD_OZ       4310.00     5050.00    5240.000    4780.000    4622.600
BRENT_USD_BBL       69.00       72.40     104.000      96.000     101.500
UST_10Y_PCT          4.05        3.95       4.350       4.520       4.660
USDSGD               1.29        1.31       1.335       1.345       1.352
VIX                 15.20       17.80      31.400      22.600      25.100

==============================================================================
EXAMPLE: ONE CLIENT THROUGH TIME
==============================================================================
Client CL-0017 - Fong Enterprises Family Office

  PF-0019  Family Office Core Mandate  (Discretionary, Balanced, USD)
  PF-0020  Alternatives Sleeve  (Advisory, Alternatives Sleeve, USD)
  PF-0021  Next Generation Account  (Custody, Growth, USD)

  Largest positions today, as a share of everything this client holds:
     13.7%  Meridian Private Equity Fund VII                           USD  12.06m
     10.9%  Orchard Private Credit Fund II                             USD   9.56m
     10.8%  Global Developed Equity Index Fund                         USD   9.52m
      6.8%  US Large Cap Core Fund                                     USD   5.98m
      6.6%  Global Investment Grade Corporate Bond Fund                USD   5.84m

  What Priscilla wrote about this client:
    2026-02-10 (Email): Capital call of USD 3.2m met from the sleeve's cash. Flagged to the family office CFO that between the remaining commitments and the gated private cre...
    2026-06-30 (Meeting): Investment committee review. G2 wants to keep the core mandate conservative. G3 representatives pushed for more technology and venture exposure in the...

==============================================================================
NOW GO AND READ clients.csv, rm_notes.json AND event_log.csv YOURSELF.
Twenty clients is small enough to actually read. Start there, not here.
==============================================================================