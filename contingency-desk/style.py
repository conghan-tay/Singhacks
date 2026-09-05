"""Design tokens and local styling from docs/design.md. No external assets."""

CSS = """
:root{
  --ink:#14161a; --ink-2:#4a5058; --ink-3:#878d96;
  --paper:#faf9f6; --surface:#ffffff; --rule:#e4e2dc; --rule-soft:#f0eee9;
  --accent:#0b4f6c; --accent-soft:#eaf1f4;
  --alert:#8c2f21; --alert-soft:#fbeeea;
  --warn:#8a6100; --warn-soft:#fdf4e3;
  --ok:#2d572c; --ok-soft:#edf3ec;
  --mute:#6b7280; --mute-soft:#f2f3f4;
  --serif:Georgia,'Iowan Old Style','Times New Roman',serif;
  --sans:-apple-system,BlinkMacSystemFont,'Segoe UI',Inter,Helvetica,Arial,sans-serif;
  --mono:'SF Mono',ui-monospace,Menlo,Consolas,monospace;
  --s1:4px; --s2:8px; --s3:12px; --s4:16px; --s6:24px; --s8:32px;
}
#MainMenu,footer,[data-testid="stHeader"]{visibility:hidden}
.stApp{background:var(--paper);color:var(--ink-2);font-family:var(--sans)}
.block-container{padding-top:var(--s8);padding-bottom:var(--s8);max-width:1180px}
.stApp *{font-variant-numeric:tabular-nums;font-feature-settings:'tnum' 1}
.stApp h1,.stApp h2{font-family:var(--serif);color:var(--ink);font-weight:400;padding:0}
.stApp h1{font-size:26px;line-height:1.3;margin:0 0 var(--s2)}
.stApp h2{font-size:19px;line-height:1.4;margin:0 0 var(--s4)}
.stApp h3{font:600 15px/1.45 var(--sans);color:var(--ink);padding:0;margin:0 0 var(--s2)}
.stApp p,.stApp li,.stApp td,.stApp th{font-size:13px;line-height:1.55}
.stApp p{margin:0 0 var(--s3);max-width:78ch}
.stApp .lead{font-size:15px;line-height:1.55}
.stApp small,.stApp .caption{display:block;font:11px/1.5 var(--sans);color:var(--ink-3)}
.stApp code{font-family:var(--mono);color:inherit}
.stApp ul,.stApp ol{margin:var(--s3) 0;padding-left:var(--s6)}
.stApp li{padding-left:var(--s1);margin-bottom:var(--s3)}
.desk-masthead{display:flex;justify-content:space-between;align-items:baseline;border-bottom:1px solid var(--rule);padding-bottom:var(--s4)}
.desk-masthead>span{font:19px/1.4 var(--serif);color:var(--ink)}
.st-key-desk-navigation{max-width:440px;margin-bottom:var(--s4)}
.session-notice{border-left:1px solid var(--accent);padding:var(--s2) var(--s3);background:var(--accent-soft);color:var(--accent)}
.stApp .badge{display:inline-block;padding:var(--s1) var(--s2);font:11px/1.4 var(--sans);border:1px solid transparent;border-radius:3px;letter-spacing:.06em;text-transform:uppercase;vertical-align:middle;white-space:normal}
.badge.pass,.badge.ARMED{background:var(--ok-soft);color:var(--ok)}
.badge.fail,.badge.FIRED{background:var(--alert-soft);color:var(--alert)}
.badge.not_measured{background:var(--warn-soft);color:var(--warn);border:1px dashed var(--warn)}
.badge[class~="n/a"],.badge.DRAFTED,.badge.DISMISSED{background:var(--mute-soft);color:var(--mute)}
.badge.DISMISSED{text-decoration:line-through}
.badge.WATCHING{background:var(--accent-soft);color:var(--accent)}
.badge.ACTIONED{background:var(--ok);color:var(--surface)}
.badge.high,.badge.critical{color:var(--alert);background:var(--alert-soft)}
.badge.medium,.badge.low{color:var(--warn);background:var(--warn-soft)}
.pc-assume .badge.high{color:var(--ok);background:var(--ok-soft)}
.number{font-family:var(--mono);text-align:right}
.negative{color:var(--alert)!important}.positive{color:var(--ink)}
.plan-meta{font:11px/1.5 var(--sans);color:var(--ink-3);margin-bottom:var(--s3)}
.plan-card{max-width:860px;margin:0 auto;background:var(--surface);padding:var(--s6);border:1px solid var(--rule);border-radius:3px}
.plan-card>.pc-head{visibility:visible}
.plan-card>section{margin-top:var(--s6);padding-top:var(--s6);border-top:1px solid var(--rule)}
.pc-head h1{font:26px/1.3 var(--serif)}
.trigger-expression{font:40px/1.25 var(--mono);color:var(--accent);margin-bottom:var(--s2);overflow-wrap:anywhere}
.stApp .derivation{margin-top:var(--s6)}
.derivation li{padding-bottom:var(--s3);border-bottom:1px solid var(--rule-soft)}
.derivation-row{display:grid;grid-template-columns:1fr 1fr;gap:var(--s4)}
.derivation small{margin-top:var(--s1);overflow-wrap:anywhere}
.stApp .pc-chain{list-style:none;margin:0;padding:0;position:relative}
.pc-chain:before{content:"";position:absolute;left:9px;top:14px;bottom:14px;width:1px;background:var(--rule)}
.stApp .hop{position:relative;padding:0 0 var(--s6) var(--s8);margin:0}
.hop:last-child{padding-bottom:0}
.hop:before{content:"";position:absolute;left:5px;top:6px;width:9px;height:9px;border-radius:50%;background:var(--surface);border:1px solid var(--accent);z-index:1}
.hop[data-conf="medium"]:before{border-color:var(--warn);border-style:dashed}
.hop[data-conf="low"]:before{border-color:var(--warn);background:var(--warn-soft)}
.hop-kind{display:block;font:11px/1.4 var(--sans);text-transform:uppercase;letter-spacing:.06em;color:var(--ink-3);margin-bottom:var(--s1)}
.hop[data-conf="medium"] .hop-kind,.hop[data-conf="low"] .hop-kind{color:var(--warn)}
.hop-label{font:600 15px/1.45 var(--sans);color:var(--ink)}
.hop-detail{font:13px/1.55 var(--sans);color:var(--ink-2);margin-top:var(--s1);max-width:70ch}
.hop-prov{font:11px/1.4 var(--mono);color:var(--ink-3);margin-top:var(--s2);overflow-wrap:anywhere}
.hop-prov code{background:var(--rule-soft);padding:1px 4px;border-radius:2px}
.stApp table{width:100%;border-collapse:collapse;margin:var(--s3) 0}
.stApp th,.stApp td{padding:var(--s3) var(--s2);vertical-align:top;border:0;border-bottom:1px solid var(--rule-soft)}
.stApp th{font-weight:400;text-align:left}
.stApp thead th{font:11px/1.5 var(--sans);color:var(--ink-3);text-transform:uppercase}
.value-table td{text-align:right;font-family:var(--mono);width:50%;overflow-wrap:normal}
.value-table small{margin-top:var(--s1);font-family:var(--sans)}
.ranked-action{margin-bottom:var(--s6)}
.action-heading{display:flex;gap:var(--s3);align-items:baseline}
.rank{font:13px/1.5 var(--mono);color:var(--accent);background:var(--accent-soft);padding:var(--s1) var(--s2);border-radius:3px;flex-shrink:0}
.action-cost{padding:var(--s3) var(--s4);background:var(--warn-soft);color:var(--ink-2);border-left:1px solid var(--warn)}
.action-cost>strong{font:600 11px/1.5 var(--sans);text-transform:uppercase;color:var(--warn)}
.action-cost p{margin:var(--s1) 0 0}
.requirements{margin-top:var(--s2)!important}
.pc-script blockquote{border-left:1px solid var(--accent);margin:0;padding:var(--s2) var(--s4);font:italic 15px/1.6 var(--serif);color:var(--ink)}
.script-pair{display:grid;grid-template-columns:1fr 1fr;gap:var(--s6);margin-top:var(--s4)}
.script-pair>div:last-child{border-left:1px solid var(--rule);padding-left:var(--s6)}
.checks th p{margin:var(--s1) 0;color:var(--ink-2)}
.checks td{text-align:right;white-space:nowrap}
.pc-suit>.badge{margin-bottom:var(--s3)}
.pc-assume h3{margin-top:var(--s6)}
.pc-fired-band{border-top:1px solid var(--alert);background:var(--alert-soft);padding:var(--s4);margin-bottom:var(--s6)}
.comparison{display:grid;grid-template-columns:1fr 1fr;gap:var(--s6)}
.comparison>section{min-width:0}
.comparison .value-table th,.comparison .value-table td{display:block;width:100%;padding:var(--s2) 0}
.comparison .value-table th{border-bottom:0;padding-bottom:0}
.comparison .value-table td{padding-top:var(--s1)}
.signature{margin-top:var(--s3);padding-top:var(--s3);border-top:1px solid var(--rule);font:11px/1.5 var(--mono);overflow-wrap:anywhere}
.signature small{margin-top:var(--s2)}
.decision-log{margin-top:var(--s6);border-top:1px solid var(--rule);padding-top:var(--s4)}
.decision-log summary{font:13px/1.5 var(--sans);cursor:pointer;color:var(--accent)}
.decision-log p{margin:var(--s1) 0;overflow-wrap:anywhere}
.st-key-plan-navigation{max-width:860px;margin:0 auto}
.st-key-plan-action-bar{position:sticky;bottom:0;z-index:10;max-width:860px;margin:0 auto;background:var(--paper);border:1px solid var(--rule);border-top-color:var(--accent);padding:var(--s3) var(--s6)}
/* A tall HTML card keeps the bar in normal flow below the viewport; pin its container for review. */
.stApp:has(.plan-card) .block-container{padding-bottom:320px}
.stApp:has(.plan-card) .st-key-plan-action-bar{position:fixed;bottom:0;left:50%;transform:translateX(-50%);width:calc(100% - 64px);max-height:45vh;overflow:auto}
.bar-heading{font:11px/1.5 var(--sans);text-transform:uppercase;color:var(--accent);display:flex;justify-content:space-between;gap:var(--s3)}
.bar-heading small{text-transform:none}
.chosen-action{font-size:13px!important;margin:0!important}
.board-heading{font:11px/1.5 var(--sans);text-transform:uppercase;letter-spacing:.06em;color:var(--ink-3);border-bottom:1px solid var(--rule);padding:var(--s3) 0;display:flex;justify-content:space-between}
.board-row{padding:var(--s3);border:1px solid var(--rule);border-radius:3px;background:var(--surface);margin-top:var(--s2)}
.board-row-top{display:flex;justify-content:space-between;align-items:baseline;gap:var(--s2)}
.board-row h3{font:15px/1.4 var(--serif);margin:0}
.distance{font:13px/1.4 var(--mono);white-space:nowrap;color:var(--ink-2);text-align:right}
.stApp .board-title{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin:var(--s2) 0}
.board-row .plan-meta{margin:0}
.board-row .badge{padding:0 var(--s1);letter-spacing:0}
.empty-column{color:var(--ink-3);padding-top:var(--s4)}
.brent-value{font:26px/1.5 var(--mono);color:var(--accent);margin:var(--s6) 0 var(--s3)}
.brent-value span{font:11px/1.5 var(--sans);color:var(--ink-3);margin-left:var(--s2)}
.dial-ticks{display:flex;justify-content:space-between;gap:var(--s4);font:11px/1.5 var(--mono);color:var(--ink-3)}
.st-key-dial-presets{margin:var(--s3) 0 var(--s6)}
.dial-strip{overflow-x:auto;margin-bottom:var(--s6)}
.facility-table td,.facility-table thead th:not(:first-child){text-align:right;white-space:nowrap}
.facility-table td{font-family:var(--mono)}
.stApp [data-testid="stButton"] button{border:1px solid var(--rule);border-radius:3px;box-shadow:none;background:var(--surface);color:var(--accent);font:13px/1.5 var(--sans);min-height:40px;transition:none}
.stApp [data-testid="stButton"] button p{font-size:13px;margin:0}
.stApp [data-testid="stButton"] button[kind="primary"]{background:var(--accent);color:var(--surface);border-color:var(--accent)}
.stApp [data-testid="stButton"] button:hover{border-color:var(--accent)}
.stApp [data-testid="stButton"] button:disabled{background:var(--mute-soft);color:var(--mute);border-color:var(--rule)}
.stApp button:focus-visible,.stApp input:focus-visible,.stApp summary:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.stApp [data-testid="stTextInput"] input,.stApp [data-testid="stNumberInput"] input{font:13px/1.5 var(--sans);color:var(--ink);background:var(--surface)}
.stApp [data-testid="stTextInputRootElement"],.stApp [data-testid="stNumberInputContainer"]{border-radius:3px;border-color:var(--rule)}
.stApp [data-testid="stWidgetLabel"] p{font-size:13px}
.stApp [data-testid="stSlider"] [role="slider"]{background:var(--accent)}
.stApp [data-testid="stSlider"] [data-testid="stThumbValue"]{color:var(--accent)}
.stApp [data-testid="stSlider"] [data-baseweb="slider"]>div>div{background:var(--accent-soft)}
@media(max-width:720px){
  .block-container{padding-left:var(--s4);padding-right:var(--s4)}
  .desk-masthead{display:block}.desk-masthead small{margin-top:var(--s2)}
  .plan-card{padding:var(--s4)}
  .derivation-row,.comparison,.script-pair{grid-template-columns:1fr}
  .script-pair>div:last-child{padding-left:0;border-left:0}
  .trigger-expression{overflow-wrap:anywhere}
  .value-table th,.value-table td{display:block;width:100%;padding:var(--s2) 0}
  .value-table th{border-bottom:0}
  .checks td{white-space:normal}
  .bar-heading{display:block}
  .stApp:has(.plan-card) .st-key-plan-action-bar{width:calc(100% - 32px);padding:var(--s3);max-height:45vh}
  .dial-ticks{flex-wrap:wrap}
}
"""
