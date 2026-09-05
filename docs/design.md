# Design spec

For the UI agent. Concrete on purpose — every token below is a value to use, not a direction to
interpret. If something is unspecified, copy the nearest pattern here rather than inventing one.

## The one idea

This is a private bank, not a consumer app. The design job is to make **numbers and provenance**
legible at a glance, and to make the RM feel that everything on screen can be opened and checked.
Restraint reads as trustworthy. Decoration reads as a demo.

Concretely, that means: one accent colour, hairline rules instead of boxes, generous whitespace,
tabular figures, and no chart on the plan card at all. The evidence chain is the only element that
gets to be visually distinctive, because it is the argument.

**Banned:** emoji, gradients, drop shadows on more than one element, coloured progress rings,
rounded corners above 4px, icon fonts, animated transitions longer than 120ms, any purple, any
"AI sparkle" motif.

## Tokens

```css
:root{
  /* ink */
  --ink:        #14161a;   /* headings, primary numbers */
  --ink-2:      #4a5058;   /* body */
  --ink-3:      #878d96;   /* provenance, captions, units */

  /* ground */
  --paper:      #faf9f6;   /* app background */
  --surface:    #ffffff;   /* cards */
  --rule:       #e4e2dc;   /* hairlines - 1px, never 2 */
  --rule-soft:  #f0eee9;

  /* accent - exactly one */
  --accent:     #0b4f6c;
  --accent-soft:#eaf1f4;

  /* semantic - muted, never saturated */
  --alert:      #8c2f21;  --alert-soft: #fbeeea;   /* breach, fail, FIRED */
  --warn:       #8a6100;  --warn-soft:  #fdf4e3;   /* not_measured, medium confidence */
  --ok:         #2d572c;  --ok-soft:    #edf3ec;   /* pass, ARMED */
  --mute:       #6b7280;  --mute-soft:  #f2f3f4;   /* DRAFTED, DISMISSED, n/a */

  /* type */
  --serif: Georgia, 'Iowan Old Style', 'Times New Roman', serif;
  --sans:  -apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, Helvetica, Arial, sans-serif;
  --mono:  'SF Mono', ui-monospace, Menlo, Consolas, monospace;

  /* space - use these six, nothing between */
  --s1:4px; --s2:8px; --s3:12px; --s4:16px; --s6:24px; --s8:32px;
}
```

**Type scale.** 11px provenance/caption · 13px body · 15px lead · 19px section heading ·
26px card title · 40px the trigger expression, and nothing else at 40.
Headings use `--serif`. Everything else `--sans`. All numerals:
`font-variant-numeric: tabular-nums; font-feature-settings:'tnum' 1;`

**Numbers.** Right-aligned in tables. Never abbreviate a currency figure — write
`USD 19,287,977`, not `USD 19.3m`. Percentages to 2dp. Always show the sign on a delta.
Negative deltas take `--alert`; positive take `--ink`, not green — this is a bank, gains are not
a celebration.

**Density.** Card padding `--s6`. Section gap `--s6`. Row gap `--s3`. Max text measure 78ch.
The plan card is 720–860px wide in a centred column; the board is full width.

## Plan card anatomy

Top to bottom, and this order is not negotiable — it is the order the RM reasons in.

| # | Block | Class | Note |
|---|---|---|---|
| 1 | Header: client, title, state chip, severity | `.pc-head` | Client name in serif 26px; plan title 15px `--ink-2` |
| 2 | Trigger | `.pc-trigger` | Expression at 40px mono in `--accent`. Below it, `trigger.derivation` as a numbered list, `step` left, `value` right, `source` at 11px `--ink-3` |
| 3 | Evidence chain | `.pc-chain` | See worked example below. Give this the most care |
| 4 | Projected consequence | `.pc-conseq` | `summary` at 15px, then `items` as label/value rows with `basis` at 11px underneath |
| 5 | Actions | `.pc-actions` | Rank badge, action in 15px, `rationale` 13px, `second_order` on a `--warn-soft` inset labelled **Cost** |
| 6 | Client script | `.pc-script` | Left-rule in `--accent`, `opening` in serif italic 15px, key points as a list, objection/response as a two-cell grid |
| 7 | Suitability | `.pc-suit` | `verdict` chip, `objective_conflict` prose, `checks` table with badges |
| 8 | Assumptions + confidence | `.pc-assume` | Always visible. Never a toggle, never a collapsed accordion |
| 9 | Action bar | `.pc-bar` | Sticky bottom. Streamlit buttons, styled minimally |

When `state == "FIRED"`, a `.pc-fired-band` sits above the header: **projected at arming** and
**actual now** side by side, with the armed signature (first 16 chars, mono, 11px), who armed it
and when. That band is the payoff of the whole product — it must look deliberate, not like an
alert toast.

### Badges

```
pass          --ok-soft bg,    --ok text
fail          --alert-soft bg, --alert text
not_measured  --warn-soft bg,  --warn text,  1px dashed --warn border
n/a           --mute-soft bg,  --mute text
```

`not_measured` **must be visually distinct from both pass and fail.** It is the finding — the
household concentration nobody measures — not an error and not a success. The dashed border is
what carries that. Do not collapse it into a grey "n/a".

### State chips

`DRAFTED` mute · `ARMED` ok · `WATCHING` accent · `FIRED` alert · `ACTIONED` ok, filled ·
`DISMISSED` mute, strikethrough label. 11px, uppercase, 0.06em letter-spacing, 3px radius.

## Worked example — the evidence chain

Copy this. It is the element judges will look at longest.

```html
<ol class="pc-chain">
  <li class="hop" data-conf="high">
    <span class="hop-kind">source of wealth</span>
    <div class="hop-body">
      <div class="hop-label">Inherited — family coal mining and energy group</div>
      <div class="hop-detail">Wealth outside the bank is the same factor as the wealth inside it.</div>
      <div class="hop-prov"><code>clients.source_of_wealth</code> · clients.csv</div>
    </div>
  </li>
  <li class="hop" data-conf="medium"> … </li>
</ol>
```

```css
.pc-chain{list-style:none;margin:0;padding:0;position:relative}
.pc-chain:before{content:"";position:absolute;left:9px;top:14px;bottom:14px;
  width:1px;background:var(--rule)}
.hop{position:relative;padding:0 0 var(--s6) var(--s8);}
.hop:before{content:"";position:absolute;left:5px;top:6px;width:9px;height:9px;
  border-radius:50%;background:var(--surface);border:1px solid var(--accent);z-index:1}
.hop[data-conf="medium"]:before{border-color:var(--warn);border-style:dashed}
.hop[data-conf="low"]:before{border-color:var(--warn);background:var(--warn-soft)}
.hop-kind{display:block;font:11px/1.4 var(--sans);text-transform:uppercase;
  letter-spacing:.06em;color:var(--ink-3);margin-bottom:var(--s1)}
.hop-label{font:15px/1.45 var(--sans);color:var(--ink);font-weight:600}
.hop-detail{font:13px/1.55 var(--sans);color:var(--ink-2);margin-top:var(--s1);max-width:70ch}
.hop-prov{font:11px/1.4 var(--mono);color:var(--ink-3);margin-top:var(--s2)}
.hop-prov code{background:var(--rule-soft);padding:1px 4px;border-radius:2px}
```

A `medium` or `low` confidence hop is marked on the node itself, not with a warning icon. The RM
should be able to scan the spine and see where the chain is estimated rather than measured.

## Board

Four columns, equal width, `--rule` hairline between. Column heading 11px uppercase `--ink-3`
with a count. Rows are `--surface` cards, `--s3` padding, 1px `--rule`, 3px radius, `--s2` gap.

Each row: client name (serif 15px), plan title (13px `--ink-2`, one line, ellipsis), and on the
right a distance-to-trigger figure — `13px` mono, `--alert` when under 10%, `--ink-2` otherwise.
Nothing else. This screen is on stage for five seconds.

## Dial

One slider, full width, `--accent` track. Above it, the current Brent value at 26px mono.
Below the track, two fixed tick labels: `72.40 · pre-conflict, 2026-02-27` and `101.50 · today`.
On change, the affected facility LTVs update in a compact strip beneath — facility id, LTV,
trigger, and a `BREACH` badge in `--alert` when crossed.

No animation on the numbers. They should snap. A counting animation looks like a toy.

## Streamlit specifics

```python
st.set_page_config(page_title="Contingency Desk", layout="wide")
st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)
st.markdown("<style>#MainMenu,footer,header{visibility:hidden}"
            ".block-container{padding-top:2rem;max-width:1180px}</style>", unsafe_allow_html=True)
```

Build blocks 1–8 of the plan card as **one HTML string** via
`st.markdown(html, unsafe_allow_html=True)`. Only block 9 (the action bar), the trigger-level
input and the dial are real Streamlit widgets. Stacking `st.columns` and `st.metric` will not
give you this density and will look like every other hackathon submission.

Escape any text interpolated into HTML with `html.escape` — the plan prose contains quotes.

**The trap that will cost you an hour.** `st.markdown(..., unsafe_allow_html=True)` runs the string
through a Markdown parser first. A blank line inside your HTML splits it into two blocks, and any
line indented four spaces becomes a `<pre>` code block — your card renders as visible tag soup.
Emit the card as one string with **no blank lines and no leading indentation**, and smoke-test one
small block through `st.markdown` before you build the rest.

## Accessibility floor

Body text ≥ 13px. All text/background pairs above 4.5:1 (the tokens are chosen to satisfy this).
Never rely on colour alone: every badge carries a word, every low-confidence hop carries the label
as well as the dashed node.
