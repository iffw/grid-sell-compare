# -*- coding: utf-8 -*-
"""Generate a to-scale ladder comparison HTML: arithmetic vs geometric grid sell orders."""
import math

LO, HI, START, N = 90.0, 110.0, 100.0, 10

arith = [LO + (HI - LO) * k / N for k in range(N + 1)]
r = (HI / LO) ** (1 / N)
geo = [LO * r ** k for k in range(N + 1)]

def pct(p):
    return (p - LO) / (HI - LO) * 100.0

MODES = [
    # name, sell_nature, buy_nature, inv_arith, inv_geo, inv_label_fn
    ("做多网格", "平多", "开多"),
    ("做空网格", "开空", "平空"),
    ("中性网格", "开空", "开多"),
]

def inv_count(mode_name, levels):
    above = sum(1 for p in levels if p > START)
    below = sum(1 for p in levels if p < START)
    if mode_name == "做多网格":
        return above, f"开局库存：市价买入 {above} 份多仓（给上方卖单备货）"
    if mode_name == "做空网格":
        return below, f"开局库存：市价开 {below} 份空仓（给下方买单备平）"
    return 0, "开局库存：0（两边全是空挂的开仓单）"

def ladder(mode_name, sell_nat, buy_nat, levels, show_gaps):
    ticks = []
    # sell ticks above start, buy ticks below or at start line vicinity
    for p in levels:
        if abs(p - START) < 1e-9:
            continue  # the start line itself carries no order
        pos = pct(p)
        if p > START:
            ticks.append(
                f'<div class="tick sell close" style="bottom:{pos:.2f}%"><span class="tp">{p:.2f}</span><span class="tb">卖 · {sell_nat} ×1份</span></div>'
                if sell_nat == "平多" else
                f'<div class="tick sell open" style="bottom:{pos:.2f}%"><span class="tp">{p:.2f}</span><span class="tb">卖 · {sell_nat} ×1份</span></div>'
            )
        else:
            ticks.append(
                f'<div class="tick buy open" style="bottom:{pos:.2f}%"><span class="tp">{p:.2f}</span><span class="tb">买 · {buy_nat} ×1份</span></div>'
                if buy_nat == "开多" else
                f'<div class="tick buy close" style="bottom:{pos:.2f}%"><span class="tp">{p:.2f}</span><span class="tb">买 · {buy_nat} ×1份</span></div>'
            )
    gaps = ""
    if show_gaps:
        sell_levels = [p for p in levels if p > START]
        g = []
        # annotate gap between consecutive sell levels, plus the grid interval straddling start
        seq = []
        below = [p for p in levels if p < START]
        if below and sell_levels:
            seq.append((below[-1], sell_levels[0]))
        for a, b in zip(sell_levels, sell_levels[1:]):
            seq.append((a, b))
        for a, b in seq:
            mid = pct((a + b) / 2)
            g.append(f'<div class="gap" style="bottom:{mid:.2f}%">↕ {b - a:.2f}</div>')
        gaps = "".join(g)
    _, inv_label = inv_count(mode_name, levels)
    return f"""
    <div class="col">
      <h4>{mode_name}</h4>
      <div class="inv">{inv_label}</div>
      <div class="ladder">
        <div class="zone sellzone"></div>
        <div class="zone buyzone"></div>
        <div class="startline" style="bottom:{pct(START):.2f}%"><span>起始价 100</span></div>
        {''.join(ticks)}
        {gaps}
      </div>
      <div class="axis"><span>下沿 90</span><span>上沿 110</span></div>
    </div>"""

def section(title, subtitle, levels, first_show_gaps=True):
    cols = "".join(
        ladder(name, s, b, levels, show_gaps=(i == 0 and first_show_gaps))
        for i, (name, s, b) in enumerate(MODES)
    )
    return f"""
  <section>
    <h2>{title}</h2>
    <p class="sub">{subtitle}</p>
    <div class="cols">{cols}</div>
  </section>"""

arith_sub = "每格恒差 <b>2.00</b>：格线 90、92、…、110。起始价 100 正好压在格线上，上方 5 档卖单、下方 5 档买单。卖单间距标注在做多那台右侧（↕），三台完全相同。"
geo_sub = f"每格恒涨 <b>2.027%</b>（格比 r=(110÷90)<sup>1/10</sup>）：格线越往上越疏，卖单间距从 2.05 一路放大到 2.19。起始价 100 <b>不在格线上</b>（夹在 99.50 和 101.52 中间），上方只有 5 档格线、下方有 6 档，所以三台开局库存第一次出现不对称。"

html = f"""<style>
:root{{
  --ink: var(--hatch-widget-text, #191919);
  --muted: var(--hatch-widget-muted, #6b7280);
  --surface: var(--hatch-widget-surface, #ffffff);
  --soft: var(--hatch-widget-surface-muted, #f3f4f6);
  --border: var(--hatch-widget-border, #d4d4d8);
  --accent: var(--hatch-widget-accent, #b45309);
}}
*{{box-sizing:border-box}}
body,.wrap{{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;color:var(--ink);line-height:1.5}}
.wrap{{max-width:1060px;margin:0 auto;padding:8px 4px}}
h1{{font-size:21px;margin:4px 0 2px}}
.lede{{color:var(--muted);font-size:13.5px;margin:0 0 6px}}
.legend{{display:flex;gap:14px;flex-wrap:wrap;font-size:13px;margin:8px 0 2px}}
.sw{{display:inline-block;width:14px;height:14px;border-radius:4px;vertical-align:-2px;margin-right:5px}}
.sw.open{{background:rgba(59,130,246,.45);border:1px solid rgba(59,130,246,.8)}}
.sw.close{{background:rgba(245,158,11,.45);border:1px solid rgba(217,119,6,.85)}}
section{{margin-top:22px}}
h2{{font-size:17px;margin:0 0 2px}}
.sub{{color:var(--muted);font-size:13px;margin:0 0 10px}}
.cols{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}}
@media(max-width:680px){{.cols{{grid-template-columns:1fr}}}}
.col{{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:10px 10px 8px}}
.col h4{{margin:0 0 4px;text-align:center;font-size:15.5px}}
.inv{{text-align:center;font-size:12.5px;color:var(--muted);min-height:34px}}
.ladder{{position:relative;height:560px;border:1px solid var(--border);border-radius:8px;overflow:visible;margin-top:4px}}
.zone{{position:absolute;left:0;right:0}}
.sellzone{{top:0;height:50%;background:rgba(220,60,60,.055);border-radius:8px 8px 0 0}}
.buyzone{{bottom:0;height:50%;background:rgba(59,130,246,.055);border-radius:0 0 8px 8px}}
.startline{{position:absolute;left:0;right:0;border-top:2px dashed var(--accent);z-index:3}}
.startline span{{position:absolute;right:4px;top:-19px;font-size:11.5px;color:var(--accent);font-weight:700;background:var(--surface);padding:0 3px}}
.tick{{position:absolute;left:52px;right:8px;transform:translateY(50%);display:flex;align-items:center;z-index:2}}
.tick .tp{{position:absolute;left:-52px;width:46px;text-align:right;font-size:12px;font-weight:600}}
.tick .tb{{flex:1;text-align:center;font-size:12.5px;padding:3px 2px;border-radius:6px;white-space:nowrap}}
.tick.sell .tb{{font-weight:700}}
.tick.buy{{opacity:.62}}
.tick.buy .tb{{font-size:11.5px;padding:2px}}
.open .tb{{background:rgba(59,130,246,.28);border:1px solid rgba(59,130,246,.75)}}
.close .tb{{background:rgba(245,158,11,.30);border:1px solid rgba(217,119,6,.8)}}
.gap{{position:absolute;right:-2px;transform:translateY(50%);font-size:11px;color:#dc2626;font-weight:700;background:var(--surface);padding:0 2px;z-index:4}}
.tick.sell{{right:44px}}
.axis{{display:flex;justify-content:space-between;color:var(--muted);font-size:11.5px;margin-top:4px}}
.sum{{margin-top:20px;background:var(--soft);border-radius:10px;padding:12px 14px;font-size:13.5px}}
.sum b{{color:var(--accent)}}
table{{width:100%;border-collapse:collapse;font-size:13px;margin-top:12px}}
th,td{{border:1px solid var(--border);padding:6px 8px;text-align:left}}
th{{background:var(--soft);text-align:center}}
</style>
<div class="wrap">
<h1>10 格网格 · 卖单挂法对比（按真实价格比例绘制）</h1>
<p class="lede">统一条件：区间 90–110 · 起始价 100 · 10 格 · 单格 1 份 · 三台同保证金、同杠杆、同标的。梯子按价格等比例画：格线在图中的高度 = 真实价格位置，疏密就是真实疏密。</p>
<div class="legend">
  <span><span class="sw close"></span>平仓单（卖手里已有的仓 / 买回已开的仓）</span>
  <span><span class="sw open"></span>开仓单（新建仓位）</span>
  <span>卖单加粗高亮，买单半透明作对照</span>
</div>
{section("一、等差网格", arith_sub, arith)}
{section("二、等比网格", geo_sub, geo)}
<table>
<tr><th>对比</th><th>等差</th><th>等比</th></tr>
<tr><td><b>卖单价格表（三台相同）</b></td><td>102 / 104 / 106 / 108 / 110</td><td>101.52 / 103.57 / 105.67 / 107.81 / 110</td></tr>
<tr><td><b>卖单间距</b></td><td>恒为 2.00</td><td>2.05 → 2.10 → 2.14 → 2.19，越往上越大</td></tr>
<tr><td><b>每份套利（跨一格）</b></td><td>金额恒为 2.00；收益率从底部 2.22% 缩到顶部 1.85%</td><td>收益率恒为 2.027%；金额从底部 1.82 涨到顶部 2.19</td></tr>
<tr><td><b>开局库存（多 / 空 / 中性）</b></td><td>5 份多 / 5 份空 / 0</td><td>5 份多 / <b>6 份空</b> / 0（起始价不在格线上，下方多一档）</td></tr>
</table>
<div class="sum">看法：先横着看同一行——<b>三台的卖单价格永远对齐</b>，差异只在颜色（性质）和梯子顶上的那句开局库存。再竖着看两节——<b>等差的格子是均匀的方砖，等比的格子越往上越大</b>，这就是两种排法唯一的区别。多/空/中性决定卖单是平还是开，等差/等比决定卖单挂在哪些价格上，两件事互相独立。</div>
</div>
"""

out = "/home/hatch/workspace/grid_compare/grid-sell-compare.html"
with open(out, "w", encoding="utf-8") as f:
    f.write(html)
print("written", out, len(html))
print("arith levels:", arith)
print("geo levels:", [round(x, 2) for x in geo])
