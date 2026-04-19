#!/usr/bin/env python3
"""
Generate docs/hardware/templates/electrode-template.{svg,png}.

v4：簡單實用導向。銅箔膠帶 + 美工刀剪得動的形狀優先。

  - Jog：8 片環形扇區（無花瓣彎曲）+ 中央 CUE 圓盤
  - Tempo：頁面中間一排 10 個長條
  - Volume：頁面下方一排 5 個長條
  - SYNC / Play：Jog 左邊兩顆圓角方塊
  - PAD1–4：Jog 右邊 2×2 方塊
  - 校正方塊右上、流程備忘最下

Channel 對應（firmware/tests/05_full_integration/05_full_integration.ino）：
  MPR#1 0x5A  Ch0–7 Jog J0–J7  Ch8 CUE(N36)  Ch9 Play(N37)  Ch10 SYNC(N38)  Ch11 PAD1(N40)
  MPR#2 0x5B  Ch0–9 Tempo T0–T9  Ch10 PAD2(N41)  Ch11 PAD3(N42)
  MPR#3 0x5C  Ch0–4 Volume V0–V4  Ch5 PAD4(N43)
"""
from __future__ import annotations

import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_SVG = os.path.abspath(os.path.join(HERE, "..", "docs", "hardware", "templates", "electrode-template.svg"))
OUT_PNG = os.path.abspath(os.path.join(HERE, "..", "docs", "hardware", "templates", "electrode-template.png"))


def pol(cx: float, cy: float, r: float, a_deg: float) -> tuple[float, float]:
    a = math.radians(a_deg)
    return (cx + r * math.cos(a), cy + r * math.sin(a))


def annular_sector(cx: float, cy: float, r1: float, r2: float, a1: float, a2: float) -> str:
    p1 = pol(cx, cy, r1, a1)
    p2 = pol(cx, cy, r2, a1)
    p3 = pol(cx, cy, r2, a2)
    p4 = pol(cx, cy, r1, a2)
    la = 1 if abs(a2 - a1) > 180 else 0
    return (
        f"M {p1[0]:.3f} {p1[1]:.3f} "
        f"L {p2[0]:.3f} {p2[1]:.3f} "
        f"A {r2:.3f} {r2:.3f} 0 {la} 1 {p3[0]:.3f} {p3[1]:.3f} "
        f"L {p4[0]:.3f} {p4[1]:.3f} "
        f"A {r1:.3f} {r1:.3f} 0 {la} 0 {p1[0]:.3f} {p1[1]:.3f} Z"
    )


# ─── 幾何 ─────────────────────────────────────────────────────────────
# Jog 置中偏上
JOG_CX, JOG_CY = 105.0, 70.0
CUE_R = 18.0
JOG_R_IN, JOG_R_OUT = 22.0, 45.0
JOG_GAP_DEG = 8.0
JOG_SEG_DEG = (360 - 8 * JOG_GAP_DEG) / 8
JOG_CENTERS = [0, 45, 90, 135, 180, 225, 270, 315]

# Tempo 直排：10 片長條，中段
TEMPO_PAD_W, TEMPO_PAD_H = 14.0, 25.0
TEMPO_GAP = 3.0
TEMPO_N = 10
TEMPO_TOTAL = TEMPO_N * TEMPO_PAD_W + (TEMPO_N - 1) * TEMPO_GAP
TEMPO_X0 = (210 - TEMPO_TOTAL) / 2
TEMPO_Y = 140.0

# Volume 直排：5 片長條，下段
VOL_PAD_W, VOL_PAD_H = 22.0, 30.0
VOL_GAP = 5.0
VOL_N = 5
VOL_TOTAL = VOL_N * VOL_PAD_W + (VOL_N - 1) * VOL_GAP
VOL_X0 = (210 - VOL_TOTAL) / 2
VOL_Y = 195.0

# SYNC / Play：Jog 左邊
SYNC_X, SYNC_Y, SYNC_W, SYNC_H = 12.0, 42.0, 22.0, 22.0
PLAY_X, PLAY_Y, PLAY_W, PLAY_H = 12.0, 80.0, 22.0, 22.0

# PAD1–4：Jog 右邊 2×2
PAD_W, PAD_H = 22.0, 22.0
PAD_GAP = 4.0
PAD_X0, PAD_Y0 = 176.0 - PAD_W, 42.0
PAD_POSITIONS = [
    (PAD_X0,              PAD_Y0),
    (PAD_X0 + PAD_W + PAD_GAP, PAD_Y0),
    (PAD_X0,              PAD_Y0 + PAD_H + PAD_GAP),
    (PAD_X0 + PAD_W + PAD_GAP, PAD_Y0 + PAD_H + PAD_GAP),
]
PAD_META = [
    ("PAD1", "M#1 Ch11", "N40"),
    ("PAD2", "M#2 Ch10", "N41"),
    ("PAD3", "M#2 Ch11", "N42"),
    ("PAD4", "M#3 Ch5",  "N43"),
]


def build_svg() -> str:
    out: list[str] = []
    out.append('<?xml version="1.0" encoding="UTF-8"?>')
    out.append('<!-- FlowDJ 1:1 電極樣板 v4（簡單實用版）· A4 直 210 × 297 mm · 印前量右上校正方塊 = 10 × 10 mm。 -->')
    out.append(
        '<svg xmlns="http://www.w3.org/2000/svg" width="210mm" height="297mm" viewBox="0 0 210 297" '
        'font-family="Noto Sans CJK TC, Noto Sans TC, PingFang TC, Microsoft JhengHei, Helvetica, Arial, sans-serif">'
    )
    out.append('<rect x="0" y="0" width="210" height="297" fill="#ffffff"/>')

    out.append("""
  <style>
    .pad     { fill: #fff2cc; stroke: #000; stroke-width: 0.4; }
    .pad-j   { fill: #e8e8e8; stroke: #000; stroke-width: 0.4; }
    .pad-cue { fill: #ffe0b2; stroke: #000; stroke-width: 0.5; }
    .pad-b   { fill: #d7e9ff; stroke: #000; stroke-width: 0.4; }
    .pad-p   { fill: #ffd7d7; stroke: #000; stroke-width: 0.4; }
    .tail    { fill: #f5f5f5; stroke: #000; stroke-width: 0.25; stroke-dasharray: 0.6,0.4; }
    .frame   { fill: none;    stroke: #888; stroke-width: 0.2; }
    .calib   { fill: none;    stroke: #000; stroke-width: 0.4; }
    .hint    { fill: none;    stroke: #aaa; stroke-width: 0.15; stroke-dasharray: 0.8,0.6; }
    .lbl     { font-size: 2.7px; text-anchor: middle; fill: #000; font-weight: 700; }
    .lbl-sm  { font-size: 1.8px; text-anchor: middle; fill: #444; }
    .title   { font-size: 4px;   font-weight: 700; fill: #000; }
    .body    { font-size: 2.3px; fill: #222; }
  </style>
""")

    # ── 標題 + 校正方塊 ────────────────────────────────────
    out.append('<text class="title" x="8" y="10">FlowDJ 1:1 電極樣板（v4 · 簡單實用）</text>')
    out.append('<text class="body"  x="8" y="14">印前量右上校正方塊 = 10 × 10 mm（印表機縮放請關閉）。</text>')

    out.append('<g id="calibration">')
    out.append('  <rect class="calib" x="188" y="7" width="10" height="10"/>')
    out.append('  <line class="calib" x1="188" y1="7"  x2="198" y2="17"/>')
    out.append('  <line class="calib" x1="198" y1="7"  x2="188" y2="17"/>')
    out.append('  <text class="lbl-sm" x="193" y="20.5">10 × 10 mm</text>')
    out.append('</g>')

    # ── Jog 8 扇區 + 中央 CUE ──────────────────────────────
    out.append('<g id="jog">')
    out.append(f'  <circle class="hint" cx="{JOG_CX}" cy="{JOG_CY}" r="{JOG_R_OUT + 2}"/>')
    for i, center in enumerate(JOG_CENTERS):
        half = JOG_SEG_DEG / 2
        a1 = center - half
        a2 = center + half
        d = annular_sector(JOG_CX, JOG_CY, JOG_R_IN, JOG_R_OUT, a1, a2)
        out.append(f'  <path class="pad-j" d="{d}"/>')
        # tail 徑向外 3 mm
        tpath = annular_sector(JOG_CX, JOG_CY, JOG_R_OUT + 0.5, JOG_R_OUT + 3.5, center - 1.8, center + 1.8)
        out.append(f'  <path class="tail" d="{tpath}"/>')
        r_mid = (JOG_R_IN + JOG_R_OUT) / 2
        lx, ly = pol(JOG_CX, JOG_CY, r_mid, center)
        out.append(f'  <text class="lbl"    x="{lx:.2f}" y="{ly - 0.2:.2f}">J{i}</text>')
        out.append(f'  <text class="lbl-sm" x="{lx:.2f}" y="{ly + 2.3:.2f}">M#1 C{i}</text>')

    out.append(f'  <circle class="pad-cue" cx="{JOG_CX}" cy="{JOG_CY}" r="{CUE_R}"/>')
    out.append(f'  <rect class="tail" x="{JOG_CX - 1.5:.2f}" y="{JOG_CY + CUE_R + 0.5:.2f}" width="3" height="4"/>')
    out.append(f'  <text class="lbl"    x="{JOG_CX}" y="{JOG_CY - 1:.2f}" font-size="3.5">CUE</text>')
    out.append(f'  <text class="lbl-sm" x="{JOG_CX}" y="{JOG_CY + 2:.2f}">M#1 C8 · N36</text>')
    out.append('</g>')

    # ── SYNC 方塊（Jog 左上）─────────────────────────────
    out.append('<g id="sync">')
    out.append(f'  <rect class="pad-b" x="{SYNC_X}" y="{SYNC_Y}" width="{SYNC_W}" height="{SYNC_H}" rx="2.5"/>')
    out.append(f'  <rect class="tail" x="{SYNC_X + SYNC_W - 1:.2f}" y="{SYNC_Y + SYNC_H/2 - 1.5:.2f}" width="4" height="3"/>')
    out.append(f'  <text class="lbl"    x="{SYNC_X + SYNC_W/2:.2f}" y="{SYNC_Y + SYNC_H/2 - 1:.2f}">SYNC</text>')
    out.append(f'  <text class="lbl-sm" x="{SYNC_X + SYNC_W/2:.2f}" y="{SYNC_Y + SYNC_H/2 + 2:.2f}">M#1 C10</text>')
    out.append(f'  <text class="lbl-sm" x="{SYNC_X + SYNC_W/2:.2f}" y="{SYNC_Y + SYNC_H/2 + 4.3:.2f}">Note 38</text>')
    out.append('</g>')

    # ── Play 方塊（Jog 左下）─────────────────────────────
    out.append('<g id="play">')
    out.append(f'  <rect class="pad-b" x="{PLAY_X}" y="{PLAY_Y}" width="{PLAY_W}" height="{PLAY_H}" rx="2.5"/>')
    out.append(f'  <rect class="tail" x="{PLAY_X + PLAY_W - 1:.2f}" y="{PLAY_Y + PLAY_H/2 - 1.5:.2f}" width="4" height="3"/>')
    tri_cx = PLAY_X + PLAY_W / 2
    tri_cy = PLAY_Y + 6
    out.append(
        f'  <polygon class="hint" points="'
        f'{tri_cx - 2.5:.2f},{tri_cy - 2.5:.2f} '
        f'{tri_cx - 2.5:.2f},{tri_cy + 2.5:.2f} '
        f'{tri_cx + 3:.2f},{tri_cy:.2f}"/>'
    )
    out.append(f'  <text class="lbl"    x="{PLAY_X + PLAY_W/2:.2f}" y="{PLAY_Y + PLAY_H/2 + 2:.2f}">Play</text>')
    out.append(f'  <text class="lbl-sm" x="{PLAY_X + PLAY_W/2:.2f}" y="{PLAY_Y + PLAY_H/2 + 4.5:.2f}">M#1 C9</text>')
    out.append(f'  <text class="lbl-sm" x="{PLAY_X + PLAY_W/2:.2f}" y="{PLAY_Y + PLAY_H/2 + 6.8:.2f}">Note 37</text>')
    out.append('</g>')

    # ── 2×2 PAD（Jog 右邊）──────────────────────────────
    out.append('<g id="pads">')
    for (name, mpr, note), (x, y) in zip(PAD_META, PAD_POSITIONS):
        out.append(f'  <rect class="pad-p" x="{x}" y="{y}" width="{PAD_W}" height="{PAD_H}" rx="2"/>')
        out.append(f'  <rect class="tail" x="{x - 4:.2f}" y="{y + PAD_H/2 - 1.5:.2f}" width="4" height="3"/>')
        out.append(f'  <text class="lbl"    x="{x + PAD_W/2:.2f}" y="{y + PAD_H/2 - 1:.2f}">{name}</text>')
        out.append(f'  <text class="lbl-sm" x="{x + PAD_W/2:.2f}" y="{y + PAD_H/2 + 2:.2f}">{mpr}</text>')
        out.append(f'  <text class="lbl-sm" x="{x + PAD_W/2:.2f}" y="{y + PAD_H/2 + 4.3:.2f}">{note}</text>')
    out.append('</g>')

    # ── Tempo 直排（10 片長條）───────────────────────────
    out.append('<g id="tempo">')
    out.append(f'  <text class="title" x="{TEMPO_X0}" y="{TEMPO_Y - 3}">速度 Tempo — 14-bit CC 14/46 · M#2 Ch0–9</text>')
    for i in range(TEMPO_N):
        x = TEMPO_X0 + i * (TEMPO_PAD_W + TEMPO_GAP)
        out.append(f'  <rect class="pad" x="{x:.2f}" y="{TEMPO_Y}" width="{TEMPO_PAD_W}" height="{TEMPO_PAD_H}" rx="1.5"/>')
        out.append(f'  <rect class="tail" x="{x + TEMPO_PAD_W/2 - 1.5:.2f}" y="{TEMPO_Y + TEMPO_PAD_H + 0.5:.2f}" width="3" height="4"/>')
        out.append(f'  <text class="lbl"    x="{x + TEMPO_PAD_W/2:.2f}" y="{TEMPO_Y + TEMPO_PAD_H/2 - 1:.2f}">T{i}</text>')
        out.append(f'  <text class="lbl-sm" x="{x + TEMPO_PAD_W/2:.2f}" y="{TEMPO_Y + TEMPO_PAD_H/2 + 2:.2f}">M#2 C{i}</text>')
    out.append('</g>')

    # ── Volume 直排（5 片長條）──────────────────────────
    out.append('<g id="volume">')
    out.append(f'  <text class="title" x="{VOL_X0}" y="{VOL_Y - 3}">音量 Volume — 7-bit CC 7 · M#3 Ch0–4</text>')
    for i in range(VOL_N):
        x = VOL_X0 + i * (VOL_PAD_W + VOL_GAP)
        out.append(f'  <rect class="pad" x="{x:.2f}" y="{VOL_Y}" width="{VOL_PAD_W}" height="{VOL_PAD_H}" rx="1.5"/>')
        out.append(f'  <rect class="tail" x="{x + VOL_PAD_W/2 - 1.5:.2f}" y="{VOL_Y + VOL_PAD_H + 0.5:.2f}" width="3" height="4"/>')
        out.append(f'  <text class="lbl"    x="{x + VOL_PAD_W/2:.2f}" y="{VOL_Y + VOL_PAD_H/2 - 1:.2f}">V{i}</text>')
        out.append(f'  <text class="lbl-sm" x="{x + VOL_PAD_W/2:.2f}" y="{VOL_Y + VOL_PAD_H/2 + 2:.2f}">M#3 C{i}</text>')
    out.append('</g>')

    # ── 流程 ─────────────────────────────────────────────
    out.append('<g id="flow" transform="translate(8,245)">')
    out.append('  <text class="title" x="0" y="0">建議流程（詳見 docs/hardware/08-prototype-assembly.md）</text>')
    out.append('  <text class="body" x="0" y="5">1. 印 100%（非縮放）→ 量校正方塊 = 10 mm → 才繼續。</text>')
    out.append('  <text class="body" x="0" y="9">2. 銅箔膠帶貼在紙上每個形狀 → 美工刀沿實線連紙一起剪。</text>')
    out.append('  <text class="body" x="0" y="13">3. 撕下貼到壓克力板，虛線「焊線尾」朝板邊 → 接杜邦線到對應 MPR121 腳。</text>')
    out.append('  <text class="body" x="0" y="17">4. 30 點全接完 → 跑 06-testing-plan.md Phase 1–4 驗通道。</text>')
    out.append('  <text class="body" x="0" y="22" font-weight="700">'
               'M#1 0x5A: Jog + CUE + Play + SYNC + PAD1  ·  M#2 0x5B: Tempo + PAD2/3  ·  M#3 0x5C: Volume + PAD4</text>')
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
