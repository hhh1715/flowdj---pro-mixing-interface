#!/usr/bin/env python3
"""
Generate docs/hardware/templates/electrode-template-overlay.{svg,png}.

Route C：把 docs/hardware/images/deck-layout-target.png 當作「印出來就是最終外
觀」的底圖，疊上 FlowDJ demo 版要用的 channel 標註 + 校正方塊 + 流程備忘。

重要前提：
  - 底圖 PNG 是設計系同學的構圖稿，「沒有固定的 mm 尺寸」。這個 script 預設
    把底圖擺成 180 mm 寬（DJ deck 左半邊約此尺寸），列印後使用者必須依右上
    角 10 × 10 mm 校正方塊實測，若歪掉就調整 DECK_WIDTH_MM 再重新輸出。
  - 原圖 1–7 編號對應到 FlowDJ 的 channel，在圖例裡對照：
       ① Jog 花瓣 J0–J7  (M#1 Ch0–7)
       ② Tempo 弧 T0–T9  (M#2 Ch0–9, 14-bit CC 14/46)
       ③ CUE              (M#1 Ch8,  Note 36)
       ④ Play             (M#1 Ch9,  Note 37)
       ⑤ Sample PAD 1–4   (M#1 Ch11 / M#2 Ch10–11 / M#3 Ch5)
       ⑥ SYNC             (M#1 Ch10, Note 38)
       ⑦ Volume 弧 V0–V4  (M#3 Ch0–4, 7-bit CC 7)
"""
from __future__ import annotations

import base64
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REF_IMG = os.path.abspath(os.path.join(HERE, "..", "docs", "hardware", "images", "deck-layout-target.png"))
OUT_SVG = os.path.abspath(os.path.join(HERE, "..", "docs", "hardware", "templates", "electrode-template-overlay.svg"))
OUT_PNG = os.path.abspath(os.path.join(HERE, "..", "docs", "hardware", "templates", "electrode-template-overlay.png"))

# ─── 可調旋鈕 ────────────────────────────────────────────────────────────
# 列印後用校正方塊實測：如果底圖各電極尺寸不對，改 DECK_WIDTH_MM 後重跑。
DECK_WIDTH_MM = 180.0

# 原圖 542 × 563 px，比例為 563/542 ≈ 1.0387；高度隨寬度比例放大
REF_PX_W, REF_PX_H = 542, 563
DECK_HEIGHT_MM = DECK_WIDTH_MM * REF_PX_H / REF_PX_W

# 底圖在頁面上的左上角
DECK_X = (210 - DECK_WIDTH_MM) / 2   # 置中
DECK_Y = 28.0


def build_svg() -> str:
    # 用 data URI 內嵌底圖，SVG 單檔可攜
    with open(REF_IMG, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    img_href = f"data:image/png;base64,{b64}"

    out: list[str] = []
    out.append('<?xml version="1.0" encoding="UTF-8"?>')
    out.append('<!--')
    out.append('  FlowDJ 1:1 電極樣板 — Overlay 版（Route C）')
    out.append('  底圖：docs/hardware/images/deck-layout-target.png（設計系同學構圖稿）')
    out.append('  疊加：channel 標註、校正方塊、流程備忘。')
    out.append(f'  底圖預設 {DECK_WIDTH_MM:.0f} mm 寬；印出來量不對就改 scripts/gen_overlay.py 的 DECK_WIDTH_MM。')
    out.append('-->')
    out.append(
        '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        'width="210mm" height="297mm" viewBox="0 0 210 297" '
        'font-family="Noto Sans CJK TC, Noto Sans TC, PingFang TC, Microsoft JhengHei, Helvetica, Arial, sans-serif">'
    )
    out.append('<rect x="0" y="0" width="210" height="297" fill="#ffffff"/>')

    out.append("""
  <style>
    .frame   { fill: none;    stroke: #888; stroke-width: 0.2; }
    .calib   { fill: none;    stroke: #000; stroke-width: 0.4; }
    .title   { font-size: 4.2px; font-weight: 700; fill: #000; }
    .body    { font-size: 2.4px; fill: #222; }
    .warn    { font-size: 2.4px; fill: #b00; font-weight: 700; }
    .legend-title { font-size: 3px; font-weight: 700; fill: #000; }
    .num     { font-size: 2.8px; font-weight: 700; fill: #000; }
    .num-sm  { font-size: 2.0px; fill: #333; }
    .num-bg  { fill: #fff; fill-opacity: 0.85; stroke: #000; stroke-width: 0.25; }
  </style>
""")

    # ── 標題 + 校正 ─────────────────────────────────────
    out.append('<text class="title" x="8" y="10">FlowDJ 1:1 電極樣板 — Overlay 版（Route C · 底圖 = 設計原稿）</text>')
    out.append('<text class="body"  x="8" y="14">印出來先量右上角校正方塊 = 10 × 10 mm；若底圖元素尺寸不合你的壓克力板，改 gen_overlay.py 的 DECK_WIDTH_MM 重輸出。</text>')
    out.append(f'<text class="warn"  x="8" y="17.5">⚠ 底圖非工程圖；目前設 deck 寬 = {DECK_WIDTH_MM:.0f} mm（高度會依比例 = {DECK_HEIGHT_MM:.1f} mm）。實際剪裁請以你量到的尺寸為主。</text>')

    out.append('<g id="calibration">')
    out.append('  <rect class="calib" x="188" y="7" width="10" height="10"/>')
    out.append('  <line class="calib" x1="188" y1="7"  x2="198" y2="17"/>')
    out.append('  <line class="calib" x1="198" y1="7"  x2="188" y2="17"/>')
    out.append('  <text class="body" x="193" y="20.5" text-anchor="middle">10 × 10 mm</text>')
    out.append('</g>')

    # ── 底圖 ─────────────────────────────────────────────
    out.append(
        f'<image x="{DECK_X:.3f}" y="{DECK_Y:.3f}" '
        f'width="{DECK_WIDTH_MM:.3f}" height="{DECK_HEIGHT_MM:.3f}" '
        f'xlink:href="{img_href}" preserveAspectRatio="none"/>'
    )

    # ── 圖例：①–⑦ → channel 對照 ──────────────────────
    # 放在底圖下方空白處（底圖 y 終點 = DECK_Y + DECK_HEIGHT_MM ≈ 28 + 187 = 215）
    legend_y = DECK_Y + DECK_HEIGHT_MM + 6
    out.append(f'<g id="legend" transform="translate(12,{legend_y:.2f})">')
    out.append('  <text class="title" x="0" y="0">底圖 ①–⑦ 對應 FlowDJ channel</text>')
    rows = [
        ("①", "Jog 花瓣 J0–J7",     "MPR#1 Ch0–7（向量和演算法算方向與速度）"),
        ("②", "Tempo 弧 T0–T9",     "MPR#2 Ch0–9（14-bit CC 14 MSB / CC 46 LSB）"),
        ("③", "CUE",                "MPR#1 Ch8 · Note 36"),
        ("④", "Play",               "MPR#1 Ch9 · Note 37"),
        ("⑤", "Sample PAD 1–4",     "PAD1=M#1 Ch11 N40 · PAD2=M#2 Ch10 N41 · PAD3=M#2 Ch11 N42 · PAD4=M#3 Ch5 N43"),
        ("⑥", "SYNC",               "MPR#1 Ch10 · Note 38"),
        ("⑦", "Volume 弧 V0–V4",    "MPR#3 Ch0–4（7-bit CC 7）"),
    ]
    for i, (num, name, desc) in enumerate(rows):
        y = 5 + i * 5
        out.append(f'  <text class="num"   x="0"  y="{y:.2f}">{num}</text>')
        out.append(f'  <text class="num"   x="6"  y="{y:.2f}">{name}</text>')
        out.append(f'  <text class="num-sm" x="44" y="{y:.2f}">{desc}</text>')
    out.append('</g>')

    # ── 流程備忘 ────────────────────────────────────────
    out.append('<g id="flow" transform="translate(12,275)">')
    out.append('  <text class="body" x="0" y="0">流程：印 100% → 量校正方塊 → 銅箔覆貼每個電極 → 沿底圖輪廓剪 → 撕下貼到壓克力板 → 杜邦線接 MPR121。</text>')
    out.append('  <text class="body" x="0" y="4">Channel：M#1 0x5A (Jog+CUE+Play+SYNC+PAD1) · M#2 0x5B (Tempo+PAD2/3) · M#3 0x5C (Volume+PAD4)。驗通道跑 06-testing-plan.md Phase 1–4。</text>')
    out.append('  <text class="body" x="0" y="8">若要精準版（非底圖、純向量）請改用 scripts/gen_template.py（Route A，sibling 檔案 electrode-template.svg）。</text>')
    out.append('</g>')

    out.append('<rect class="frame" x="5" y="5" width="200" height="287"/>')
    out.append('</svg>')
    return "\n".join(out) + "\n"


def main() -> int:
    svg = build_svg()
    os.makedirs(os.path.dirname(OUT_SVG), exist_ok=True)
    with open(OUT_SVG, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote {OUT_SVG} ({len(svg)} bytes)")

    import cairosvg
    cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=OUT_PNG, output_width=2480)
    print(f"wrote {OUT_PNG} ({os.path.getsize(OUT_PNG)} bytes, ~300 dpi)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
