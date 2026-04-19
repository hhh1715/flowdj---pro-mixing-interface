#!/usr/bin/env python3
"""
Generate docs/hardware/templates/electrode-template.{svg,png}.

v3: 參考 docs/hardware/images/deck-layout-target.png 的版型重構。

  - 中央：CUE 圓盤 + 8 片花瓣型 Jog lobes（stadium shape bent along arc）
  - 右上：Tempo 弧 T0-T9（10 片，與 Jog 同心）
  - 右下：Volume 弧 V0-V4（5 片，取代原本的線性 fader）
  - 左上：2×2 PAD 網格
  - 右側：SYNC 膠囊；左下：Play 圓角矩形 + ▶

Channel 對應（與 firmware/tests/05_full_integration/05_full_integration.ino 對齊）：
  MPR#1 0x5A  Ch0-7 Jog J0-J7       Ch8 CUE(Note36)  Ch9 Play(Note37)  Ch10 SYNC(Note38)  Ch11 PAD1(Note40)
  MPR#2 0x5B  Ch0-9 Tempo T0-T9     Ch10 PAD2(Note41)  Ch11 PAD3(Note42)
  MPR#3 0x5C  Ch0-4 Volume V0-V4    Ch5 PAD4(Note43)
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


def petal(cx: float, cy: float, r1: float, r2: float, a1: float, a2: float) -> str:
    """彎曲的 stadium（兩端圓帽）—— 像花瓣的 Jog lobe。"""
    cap_r = (r2 - r1) / 2.0
    p_in_start = pol(cx, cy, r1, a1)
    p_out_start = pol(cx, cy, r2, a1)
    p_out_end = pol(cx, cy, r2, a2)
    p_in_end = pol(cx, cy, r1, a2)
    return (
        f"M {p_in_start[0]:.3f} {p_in_start[1]:.3f} "
        # left cap：從 inner 點沿半圓往外到 outer 點（bulge 朝外、往 a1 那一側）
        f"A {cap_r:.3f} {cap_r:.3f} 0 0 0 {p_out_start[0]:.3f} {p_out_start[1]:.3f} "
        # outer arc
        f"A {r2:.3f} {r2:.3f} 0 0 1 {p_out_end[0]:.3f} {p_out_end[1]:.3f} "
        # right cap
        f"A {cap_r:.3f} {cap_r:.3f} 0 0 0 {p_in_end[0]:.3f} {p_in_end[1]:.3f} "
        # inner arc 回來
        f"A {r1:.3f} {r1:.3f} 0 0 0 {p_in_start[0]:.3f} {p_in_start[1]:.3f} Z"
    )


# ─── 全局幾何 ────────────────────────────────────────────────────────────
# Jog 中心：微偏左下，讓右側放 Tempo/Volume 雙弧、左上放 PAD 網格
JOG_CX, JOG_CY = 92.0, 138.0

# 中央 CUE 圓盤
CUE_R = 20.0

# Jog 8 片花瓣：內外半徑、間隙
JOG_R_IN, JOG_R_OUT = 28.0, 48.0          # 花瓣寬 20 mm（足以剪）
JOG_GAP_DEG = 7.0                          # 花瓣之間 ≈ 4.3 mm @ r=38，好剪
JOG_SEG_DEG = (360 - 8 * JOG_GAP_DEG) / 8
JOG_CENTERS = [0, 45, 90, 135, 180, 225, 270, 315]  # 對齊 firmware JOG_ANGLES_DEG

# Tempo 弧：右上方向（-70° 到 +10°），10 片
TEMPO_R_IN, TEMPO_R_OUT = 56.0, 68.0
TEMPO_START_DEG = -75.0
TEMPO_END_DEG = 5.0
TEMPO_GAP_DEG = 2.5                        # ≈ 2.7 mm @ r=62，手工剪可分
TEMPO_SPAN = TEMPO_END_DEG - TEMPO_START_DEG
TEMPO_SEG_DEG = (TEMPO_SPAN - 9 * TEMPO_GAP_DEG) / 10  # ≈ 5.75°

# Volume 弧：右下方向（+20° 到 +80°），5 片
VOL_R_IN, VOL_R_OUT = 56.0, 68.0
VOL_START_DEG = 20.0
VOL_END_DEG = 80.0
VOL_GAP_DEG = 3.0                          # ≈ 3.2 mm @ r=62
VOL_SPAN = VOL_END_DEG - VOL_START_DEG
VOL_SEG_DEG = (VOL_SPAN - 4 * VOL_GAP_DEG) / 5  # ≈ 9.6°

# 2x2 PAD 網格（左上）
PAD_W, PAD_H = 24.0, 24.0
PAD_GAP = 4.0
PAD_X0, PAD_Y0 = 14.0, 26.0
PAD_POSITIONS = [
    (PAD_X0, PAD_Y0),                               # PAD1 左上
    (PAD_X0 + PAD_W + PAD_GAP, PAD_Y0),             # PAD2 右上
    (PAD_X0, PAD_Y0 + PAD_H + PAD_GAP),             # PAD3 左下
    (PAD_X0 + PAD_W + PAD_GAP, PAD_Y0 + PAD_H + PAD_GAP),  # PAD4 右下
]
PAD_META = [
    ("PAD1", "M#1 Ch11", "Note 40"),
    ("PAD2", "M#2 Ch10", "Note 41"),
    ("PAD3", "M#2 Ch11", "Note 42"),
    ("PAD4", "M#3 Ch5",  "Note 43"),
]

# SYNC 膠囊（右側）— M#1 Ch10 Note 38
SYNC_X, SYNC_Y, SYNC_W, SYNC_H = 175.0, 115.0, 20.0, 46.0

# Play 圓角矩形 + ▶ 圖示（左下）— M#1 Ch9 Note 37
PLAY_X, PLAY_Y, PLAY_W, PLAY_H = 14.0, 198.0, 32.0, 30.0


def build_svg() -> str:
    out: list[str] = []
    out.append('<?xml version="1.0" encoding="UTF-8"?>')
    out.append('<!--')
    out.append('  FlowDJ 1:1 電極列印樣板 v3')
    out.append('  佈局參考 docs/hardware/images/deck-layout-target.png（花瓣 Jog / 雙弧 slider / 2x2 PAD）')
    out.append('  A4 直向 210 × 297 mm，座標 mm。印前先量右上校正方塊 = 10 × 10 mm。')
    out.append('-->')
    out.append(
        '<svg xmlns="http://www.w3.org/2000/svg" width="210mm" height="297mm" '
        'viewBox="0 0 210 297" '
        'font-family="Noto Sans CJK TC, Noto Sans TC, PingFang TC, Microsoft JhengHei, Helvetica, Arial, sans-serif">'
    )
    out.append('<rect x="0" y="0" width="210" height="297" fill="#ffffff"/>')

    out.append("""
  <style>
    .pad-cue  { fill: #ffb74d; stroke: #000; stroke-width: 0.5; }
    .pad-jog  { fill: #ffd180; stroke: #000; stroke-width: 0.4; }
    .pad-tempo{ fill: #fff2a8; stroke: #000; stroke-width: 0.4; }
    .pad-vol  { fill: #c8e6c9; stroke: #000; stroke-width: 0.4; }
    .pad-btn  { fill: #fff9c4; stroke: #000; stroke-width: 0.4; }
    .pad-play { fill: #a5d6a7; stroke: #000; stroke-width: 0.4; }
    .pad-p    { fill: #ffccbc; stroke: #000; stroke-width: 0.4; }
    .tail     { fill: #f5f5f5; stroke: #000; stroke-width: 0.25; stroke-dasharray: 0.6,0.4; }
    .frame    { fill: none;    stroke: #888; stroke-width: 0.2; }
    .calib    { fill: none;    stroke: #000; stroke-width: 0.4; }
    .hint     { fill: none;    stroke: #aaa; stroke-width: 0.15; stroke-dasharray: 0.8,0.6; }
    .lbl      { font-size: 2.7px; text-anchor: middle; fill: #000; font-weight: 700; }
    .lbl-sm   { font-size: 1.8px; text-anchor: middle; fill: #444; }
    .title    { font-size: 4.2px; font-weight: 700; fill: #000; }
    .body     { font-size: 2.4px; fill: #222; }
    .legend-title { font-size: 3px;   font-weight: 700; fill: #000; }
    .tri      { fill: #2e7d32; stroke: none; }
  </style>
""")

    # ── 標題 + 校正 ─────────────────────────────────────────
    out.append('<text class="title" x="8" y="10">FlowDJ 1:1 電極樣板（v3 · 貼近原型外觀）</text>')
    out.append('<text class="body"  x="8" y="14">印前先驗右上角校正方塊 = 10 × 10 mm；印表機若縮放就關閉「符合頁面」、改 100%。</text>')

    out.append('<g id="calibration">')
    out.append('  <rect class="calib" x="188" y="7" width="10" height="10"/>')
    out.append('  <line class="calib" x1="188" y1="7"  x2="198" y2="17"/>')
    out.append('  <line class="calib" x1="198" y1="7"  x2="188" y2="17"/>')
    out.append('  <text class="lbl-sm" x="193" y="20.5">10 × 10 mm</text>')
    out.append('</g>')

    # ── 2x2 PAD 網格（左上）─────────────────────────────────
    out.append('<g id="pads">')
    out.append(f'  <text class="title" x="{PAD_X0}" y="{PAD_Y0 - 3}">Sample PAD 1–4</text>')
    for (name, mpr, note), (x, y) in zip(PAD_META, PAD_POSITIONS):
        out.append(f'  <rect class="pad-p" x="{x}" y="{y}" width="{PAD_W}" height="{PAD_H}" rx="2.5" ry="2.5"/>')
        # tail：朝下方（接線往下走）
        out.append(f'  <rect class="tail" x="{x + PAD_W/2 - 2:.2f}" y="{y + PAD_H + 0.5:.2f}" width="4" height="4"/>')
        out.append(f'  <text class="lbl"    x="{x + PAD_W/2:.2f}" y="{y + 11:.2f}">{name}</text>')
        out.append(f'  <text class="lbl-sm" x="{x + PAD_W/2:.2f}" y="{y + 14.5:.2f}">{mpr}</text>')
        out.append(f'  <text class="lbl-sm" x="{x + PAD_W/2:.2f}" y="{y + 17.5:.2f}">{note}</text>')
    out.append('</g>')

    # ── Jog 8 花瓣 ─────────────────────────────────────────
    out.append('<g id="jog">')
    out.append(f'  <circle class="hint" cx="{JOG_CX}" cy="{JOG_CY}" r="{JOG_R_OUT + 3}"/>')
    for i, center in enumerate(JOG_CENTERS):
        half = JOG_SEG_DEG / 2
        a1 = center - half
        a2 = center + half
        d = petal(JOG_CX, JOG_CY, JOG_R_IN, JOG_R_OUT, a1, a2)
        out.append(f'  <path class="pad-jog" d="{d}"/>')
        # tail 從花瓣外弧中點往外延伸（徑向外）
        tail_mid = center
        tail_r1 = JOG_R_OUT + 1.0
        tail_r2 = JOG_R_OUT + 5.0
        tpath = annular_sector(JOG_CX, JOG_CY, tail_r1, tail_r2, tail_mid - 2, tail_mid + 2)
        out.append(f'  <path class="tail" d="{tpath}"/>')
        # label 放花瓣中心
        r_mid = (JOG_R_IN + JOG_R_OUT) / 2
        lx, ly = pol(JOG_CX, JOG_CY, r_mid, center)
        out.append(f'  <text class="lbl"    x="{lx:.2f}" y="{ly - 0.2:.2f}">J{i}</text>')
        out.append(f'  <text class="lbl-sm" x="{lx:.2f}" y="{ly + 2.4:.2f}">M#1 Ch{i}</text>')

    # 中央 CUE 圓盤
    out.append(f'  <circle class="pad-cue" cx="{JOG_CX}" cy="{JOG_CY}" r="{CUE_R}"/>')
    # CUE 焊線尾（朝上、穿過 Jog 最近的 gap）
    out.append(f'  <rect class="tail" x="{JOG_CX - 1.5:.2f}" y="{JOG_CY - CUE_R - 4.5:.2f}" width="3" height="4"/>')
    out.append(f'  <text class="lbl"    x="{JOG_CX}" y="{JOG_CY - 1.5:.2f}" font-size="4">CUE</text>')
    out.append(f'  <text class="lbl-sm" x="{JOG_CX}" y="{JOG_CY + 1.5:.2f}">M#1 Ch8</text>')
    out.append(f'  <text class="lbl-sm" x="{JOG_CX}" y="{JOG_CY + 4:.2f}">Note 36</text>')
    out.append('</g>')

    # ── Tempo 弧（右上）────────────────────────────────────
    out.append('<g id="tempo">')
    label_xy = pol(JOG_CX, JOG_CY, TEMPO_R_OUT + 14, (TEMPO_START_DEG + TEMPO_END_DEG) / 2 - 10)
    out.append(f'  <text class="title" x="{label_xy[0]:.2f}" y="{label_xy[1]:.2f}">速度 Tempo</text>')
    out.append(f'  <text class="body"  x="{label_xy[0]:.2f}" y="{label_xy[1] + 4:.2f}">14-bit CC 14/46 · M#2 Ch0–9</text>')
    for i in range(10):
        a1 = TEMPO_START_DEG + i * (TEMPO_SEG_DEG + TEMPO_GAP_DEG)
        a2 = a1 + TEMPO_SEG_DEG
        d = annular_sector(JOG_CX, JOG_CY, TEMPO_R_IN, TEMPO_R_OUT, a1, a2)
        out.append(f'  <path class="pad-tempo" d="{d}"/>')
        mid = (a1 + a2) / 2
        tpath = annular_sector(JOG_CX, JOG_CY, TEMPO_R_OUT + 0.5, TEMPO_R_OUT + 4, mid - 1.2, mid + 1.2)
        out.append(f'  <path class="tail" d="{tpath}"/>')
        r_mid = (TEMPO_R_IN + TEMPO_R_OUT) / 2
        lx, ly = pol(JOG_CX, JOG_CY, r_mid, mid)
        out.append(f'  <text class="lbl"    x="{lx:.2f}" y="{ly - 0.2:.2f}">T{i}</text>')
        out.append(f'  <text class="lbl-sm" x="{lx:.2f}" y="{ly + 2.2:.2f}">C{i}</text>')
    out.append('</g>')

    # ── Volume 弧（右下，取代原線性 fader）─────────────────
    out.append('<g id="volume">')
    # 標題放到弧外下方、避開右側圖例與 Play
    out.append(f'  <text class="title" x="62" y="238">音量 Volume</text>')
    out.append(f'  <text class="body"  x="62" y="242">7-bit CC 7 · M#3 Ch0–4（弧形 5 片）</text>')
    for i in range(5):
        a1 = VOL_START_DEG + i * (VOL_SEG_DEG + VOL_GAP_DEG)
        a2 = a1 + VOL_SEG_DEG
        d = annular_sector(JOG_CX, JOG_CY, VOL_R_IN, VOL_R_OUT, a1, a2)
        out.append(f'  <path class="pad-vol" d="{d}"/>')
        mid = (a1 + a2) / 2
        tpath = annular_sector(JOG_CX, JOG_CY, VOL_R_OUT + 0.5, VOL_R_OUT + 4, mid - 1.2, mid + 1.2)
        out.append(f'  <path class="tail" d="{tpath}"/>')
        r_mid = (VOL_R_IN + VOL_R_OUT) / 2
        lx, ly = pol(JOG_CX, JOG_CY, r_mid, mid)
        out.append(f'  <text class="lbl"    x="{lx:.2f}" y="{ly - 0.2:.2f}">V{i}</text>')
        out.append(f'  <text class="lbl-sm" x="{lx:.2f}" y="{ly + 2.2:.2f}">C{i}</text>')
    out.append('</g>')

    # ── SYNC 膠囊（右側）──────────────────────────────────
    out.append('<g id="sync">')
    rx = SYNC_W / 2
    out.append(f'  <rect class="pad-btn" x="{SYNC_X}" y="{SYNC_Y}" width="{SYNC_W}" height="{SYNC_H}" rx="{rx}" ry="{rx}"/>')
    out.append(f'  <rect class="tail" x="{SYNC_X + SYNC_W/2 - 1.5:.2f}" y="{SYNC_Y + SYNC_H + 0.5:.2f}" width="3" height="4"/>')
    out.append(f'  <text class="lbl"    x="{SYNC_X + SYNC_W/2:.2f}" y="{SYNC_Y + SYNC_H/2 - 2:.2f}" font-size="3.5">SYNC</text>')
    out.append(f'  <text class="lbl-sm" x="{SYNC_X + SYNC_W/2:.2f}" y="{SYNC_Y + SYNC_H/2 + 1:.2f}">M#1 Ch10</text>')
    out.append(f'  <text class="lbl-sm" x="{SYNC_X + SYNC_W/2:.2f}" y="{SYNC_Y + SYNC_H/2 + 3.3:.2f}">Note 38</text>')
    out.append('</g>')

    # ── Play 圓角矩形 + ▶（左下）──────────────────────────
    out.append('<g id="play">')
    out.append(f'  <rect class="pad-play" x="{PLAY_X}" y="{PLAY_Y}" width="{PLAY_W}" height="{PLAY_H}" rx="4" ry="4"/>')
    out.append(f'  <rect class="tail" x="{PLAY_X + PLAY_W/2 - 1.5:.2f}" y="{PLAY_Y + PLAY_H + 0.5:.2f}" width="3" height="4"/>')
    tri_cx = PLAY_X + PLAY_W / 2
    tri_cy = PLAY_Y + 10
    out.append(
        f'  <polygon class="tri" points="'
        f'{tri_cx - 3:.2f},{tri_cy - 3.5:.2f} '
        f'{tri_cx - 3:.2f},{tri_cy + 3.5:.2f} '
        f'{tri_cx + 3.5:.2f},{tri_cy:.2f}"/>'
    )
    out.append(f'  <text class="lbl"    x="{PLAY_X + PLAY_W/2:.2f}" y="{PLAY_Y + 20:.2f}" font-size="3.5">Play</text>')
    out.append(f'  <text class="lbl-sm" x="{PLAY_X + PLAY_W/2:.2f}" y="{PLAY_Y + 23.5:.2f}">M#1 Ch9 / Note 37</text>')
    out.append('</g>')

    # ── 圖例（右下角、避開 Volume 弧與 SYNC）──────────────
    out.append('<g id="legend" transform="translate(160,175)">')
    out.append('  <text class="legend-title" x="0" y="0">圖例</text>')
    items = [
        ("pad-cue",   "CUE（中央主鍵）"),
        ("pad-jog",   "Jog 花瓣 J0–J7"),
        ("pad-tempo", "Tempo 弧 T0–T9"),
        ("pad-vol",   "Volume 弧 V0–V4"),
        ("pad-btn",   "SYNC"),
        ("pad-play",  "Play"),
        ("pad-p",     "PAD1–4"),
    ]
    for i, (cls, text) in enumerate(items):
        y = 4 + i * 4
        out.append(f'  <rect class="{cls}" x="0" y="{y:.2f}" width="5" height="3" rx="0.6"/>')
        out.append(f'  <text class="body"  x="7" y="{y + 2.5:.2f}">{text}</text>')
    out.append('  <rect class="tail" x="0" y="34" width="5" height="3"/>')
    out.append('  <text class="body"  x="7" y="36.5">虛線 = 焊線尾（延伸 3–4 mm）</text>')
    out.append('</g>')

    # ── 流程備忘 ──────────────────────────────────────────
    out.append('<g id="flow" transform="translate(8,260)">')
    out.append('  <text class="title" x="0" y="0">建議流程（詳見 docs/hardware/08-prototype-assembly.md）</text>')
    out.append('  <text class="body" x="0" y="5">1. 印這張（100% 比例）→ 量右上校正方塊 = 10 mm → 才往下做。</text>')
    out.append('  <text class="body" x="0" y="9">2. 銅箔膠帶覆貼每個電極 → 美工刀沿黑實線連紙一起剪。</text>')
    out.append('  <text class="body" x="0" y="13">3. 撕下貼到壓克力板；焊線尾（虛線片）朝板邊 → 焊 / 導電膠接杜邦線 → 拉到對應 MPR121 腳。</text>')
    out.append('  <text class="body" x="0" y="17">4. 30 點全接完 → 跑 06-testing-plan.md Phase 1–4 驗通道。</text>')
    out.append('  <text class="body" x="0" y="22" font-weight="700">M#1 0x5A: Jog+CUE+Play+SYNC+PAD1 · M#2 0x5B: Tempo+PAD2/3 · M#3 0x5C: Volume+PAD4</text>')
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
