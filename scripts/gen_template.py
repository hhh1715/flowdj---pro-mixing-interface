#!/usr/bin/env python3
"""
Generate docs/hardware/templates/electrode-template.{svg,png}.

Layout (A4 portrait 210x297 mm, 1:1 for printing):
  - Jog wheel center (cx=85, cy=110), outer R=52, inner R=23.
    Central disc = CUE (M#1 Ch8). 8 annular sectors J0-J7.
    J0=0deg (3 o'clock), going clockwise on screen matches firmware
    JOG_ANGLES_DEG = [0, 45, 90, 135, 180, 225, 270, 315].
  - Tempo arc (M#2 Ch0-9) concentric with Jog on the right side,
    inner r=60, outer r=72, angles -50..+50 split into 10 wedges.
  - SYNC / Play as capsule buttons to the left of Jog.
  - PAD1..PAD4 in a horizontal row below.
  - Volume fader (M#3 Ch0-4) linear, 5 pads, bottom of page.
  - Calibration square top-right (10x10 mm). If printed 1:1 it measures 10 mm.
"""
from __future__ import annotations

import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_SVG = os.path.abspath(os.path.join(HERE, "..", "docs", "hardware", "templates", "electrode-template.svg"))
OUT_PNG = os.path.abspath(os.path.join(HERE, "..", "docs", "hardware", "templates", "electrode-template.png"))


def annular_sector(cx: float, cy: float, r1: float, r2: float, a1_deg: float, a2_deg: float) -> str:
    """SVG path for an annular sector from angle a1 to a2 (degrees, SVG convention: 0=right, +=CW)."""
    a1 = math.radians(a1_deg)
    a2 = math.radians(a2_deg)
    p1 = (cx + r1 * math.cos(a1), cy + r1 * math.sin(a1))
    p2 = (cx + r2 * math.cos(a1), cy + r2 * math.sin(a1))
    p3 = (cx + r2 * math.cos(a2), cy + r2 * math.sin(a2))
    p4 = (cx + r1 * math.cos(a2), cy + r1 * math.sin(a2))
    large_arc = 1 if abs(a2_deg - a1_deg) > 180 else 0
    return (
        f"M {p1[0]:.3f} {p1[1]:.3f} "
        f"L {p2[0]:.3f} {p2[1]:.3f} "
        f"A {r2:.3f} {r2:.3f} 0 {large_arc} 1 {p3[0]:.3f} {p3[1]:.3f} "
        f"L {p4[0]:.3f} {p4[1]:.3f} "
        f"A {r1:.3f} {r1:.3f} 0 {large_arc} 0 {p1[0]:.3f} {p1[1]:.3f} Z"
    )


def pol(cx: float, cy: float, r: float, a_deg: float) -> tuple[float, float]:
    a = math.radians(a_deg)
    return (cx + r * math.cos(a), cy + r * math.sin(a))


# ---------- 幾何參數 ----------

JOG_CX, JOG_CY = 85.0, 110.0
JOG_R_OUT, JOG_R_IN = 52.0, 23.0        # 8 顆 J0-J7 的內外徑
CUE_R = 20.0                              # 中心 CUE 圓半徑（< JOG_R_IN，中間留 3 mm 空環）
JOG_GAP_DEG = 8.0                         # 每片之間的空隙
JOG_SEG_DEG = (360.0 - 8 * JOG_GAP_DEG) / 8  # 每片弧寬

# 對應 firmware JOG_ANGLES_DEG = [0, 45, 90, 135, 180, 225, 270, 315]
JOG_CENTERS = [0, 45, 90, 135, 180, 225, 270, 315]

TEMPO_R_IN, TEMPO_R_OUT = 60.0, 72.0      # 同心於 Jog、在右側的弧形 slider
TEMPO_SPAN = 100.0                        # 總跨角度（-50 .. +50）
TEMPO_GAP_DEG = 1.0                       # 分片間隙
TEMPO_SEG_DEG = (TEMPO_SPAN - TEMPO_GAP_DEG * 9) / 10  # 每片弧寬

# SYNC / Play 兩顆膠囊按鈕，在 Jog 左邊
SYNC_X, SYNC_Y, SYNC_W, SYNC_H = 10.0, 72.0, 22.0, 28.0   # M#1 Ch10 Note 38
PLAY_X, PLAY_Y, PLAY_W, PLAY_H = 10.0, 108.0, 22.0, 28.0  # M#1 Ch9  Note 37

# PAD 四顆 — 橫排在 Jog 下方
PAD_W, PAD_H = 26.0, 26.0
PAD_Y = 180.0
PAD_XS = [14.0, 44.0, 74.0, 104.0]
PAD_META = [
    ("PAD1", "MPR#1 Ch11", "Note 40"),
    ("PAD2", "MPR#2 Ch10", "Note 41"),
    ("PAD3", "MPR#2 Ch11", "Note 42"),
    ("PAD4", "MPR#3 Ch5",  "Note 43"),
]

# Volume fader 5 片，置中於下方
VOL_N = 5
VOL_W, VOL_H = 18.0, 28.0
VOL_GAP = 4.0
VOL_TOTAL = VOL_N * VOL_W + (VOL_N - 1) * VOL_GAP
VOL_X0 = (210.0 - VOL_TOTAL) / 2  # 置中
VOL_Y = 228.0


# ---------- SVG 生成 ----------

def build_svg() -> str:
    parts: list[str] = []
    parts.append('<?xml version="1.0" encoding="UTF-8"?>')
    parts.append("<!--")
    parts.append("  FlowDJ 1:1 電極列印樣板（優化版）")
    parts.append("  A4 直向 210 x 297 mm，座標 mm。")
    parts.append("  Jog：中心 CUE 圓 + 8 顆環形扇區 J0-J7，弧間留 8° 剪縫。")
    parts.append("  Tempo slider：與 Jog 同心的右側弧形，10 片扇區。")
    parts.append("  SYNC / Play：膠囊型按鈕，在 Jog 左邊。")
    parts.append("  PAD1-4：Jog 下方橫排；Volume fader：頁尾置中。")
    parts.append("  印刷驗證：右上角校正方塊 = 10 × 10 mm。")
    parts.append("  channel 對應 firmware/tests/05_full_integration/05_full_integration.ino。")
    parts.append("-->")
    parts.append(
        '<svg xmlns="http://www.w3.org/2000/svg" width="210mm" height="297mm" '
        'viewBox="0 0 210 297" '
        'font-family="Noto Sans CJK TC, Noto Sans TC, PingFang TC, Microsoft JhengHei, Helvetica, Arial, sans-serif">'
    )
    parts.append('<rect x="0" y="0" width="210" height="297" fill="#ffffff" />')

    parts.append("""
  <style>
    .cut    { fill: none;       stroke: #000; stroke-width: 0.35; }
    .pad    { fill: #fff2cc;    stroke: #000; stroke-width: 0.35; }
    .pad-b  { fill: #d7e9ff;    stroke: #000; stroke-width: 0.35; }
    .pad-p  { fill: #ffd7d7;    stroke: #000; stroke-width: 0.35; }
    .pad-j  { fill: #eaeaea;    stroke: #000; stroke-width: 0.35; }
    .pad-cue{ fill: #c8e6c9;    stroke: #000; stroke-width: 0.45; }
    .tail   { fill: #f5f5f5;    stroke: #000; stroke-width: 0.25; stroke-dasharray: 0.6,0.4; }
    .frame  { fill: none;       stroke: #888; stroke-width: 0.2; }
    .calib  { fill: none;       stroke: #000; stroke-width: 0.4; }
    .hint   { stroke: #aaa;     stroke-width: 0.15; stroke-dasharray: 0.8,0.6; fill: none; }
    .lbl    { font-size: 2.6px; text-anchor: middle; fill: #000; font-weight: 600; }
    .lbl-sm { font-size: 1.8px; text-anchor: middle; fill: #444; }
    .title  { font-size: 4.2px; font-weight: 700; fill: #000; }
    .body   { font-size: 2.4px; fill: #222; }
    .legend-title { font-size: 3px; font-weight: 700; fill: #000; }
  </style>
""")

    # ---------- 標題 + 校正 ----------
    parts.append('<text class="title" x="8" y="10">FlowDJ 1:1 電極樣板（優化版 v2）</text>')
    parts.append(
        '<text class="body"  x="8" y="14.5">'
        '印刷前先驗：右上角校正方塊必須 = 10 × 10 mm。不準就改印 100% / 原始尺寸。'
        '</text>'
    )
    parts.append('<g id="calibration">')
    parts.append('  <rect class="calib" x="188" y="7" width="10" height="10" />')
    parts.append('  <line class="calib" x1="188" y1="7"  x2="198" y2="17" />')
    parts.append('  <line class="calib" x1="198" y1="7"  x2="188" y2="17" />')
    parts.append('  <text class="lbl-sm" x="193" y="20">10 × 10 mm</text>')
    parts.append('</g>')

    # ---------- Jog ----------
    parts.append('<g id="jog">')
    # 外輪廓（可選：虛線外框提示範圍）
    parts.append(
        f'  <circle class="hint" cx="{JOG_CX}" cy="{JOG_CY}" r="{JOG_R_OUT + 2}" />'
    )
    # 8 顆 J0-J7
    for i, center_deg in enumerate(JOG_CENTERS):
        half = JOG_SEG_DEG / 2
        a1 = center_deg - half
        a2 = center_deg + half
        path = annular_sector(JOG_CX, JOG_CY, JOG_R_IN, JOG_R_OUT, a1, a2)
        parts.append(f'  <path class="pad-j" d="{path}" />')
        # 焊線尾：從 r_out 再往外 3 mm 拉一小塊
        tail_mid = center_deg
        tail_r1 = JOG_R_OUT + 0.5
        tail_r2 = JOG_R_OUT + 4.0
        tail_a1 = tail_mid - 1.5
        tail_a2 = tail_mid + 1.5
        tail_path = annular_sector(JOG_CX, JOG_CY, tail_r1, tail_r2, tail_a1, tail_a2)
        parts.append(f'  <path class="tail" d="{tail_path}" />')
        # label 放電極中心
        r_mid = (JOG_R_IN + JOG_R_OUT) / 2
        lx, ly = pol(JOG_CX, JOG_CY, r_mid, center_deg)
        parts.append(f'  <text class="lbl"    x="{lx:.2f}" y="{ly - 0.2:.2f}">J{i}</text>')
        parts.append(f'  <text class="lbl-sm" x="{lx:.2f}" y="{ly + 2.4:.2f}">M#1 Ch{i}</text>')

    # 中心 CUE 圓
    parts.append(
        f'  <circle class="pad-cue" cx="{JOG_CX}" cy="{JOG_CY}" r="{CUE_R}" />'
    )
    parts.append(
        f'  <rect class="tail" x="{JOG_CX - 1.5:.2f}" y="{JOG_CY - CUE_R - 4:.2f}" '
        f'width="3" height="4" />'
    )
    parts.append(f'  <text class="lbl"    x="{JOG_CX}" y="{JOG_CY - 2:.2f}">CUE</text>')
    parts.append(f'  <text class="lbl-sm" x="{JOG_CX}" y="{JOG_CY + 0.8:.2f}">M#1 Ch8</text>')
    parts.append(f'  <text class="lbl-sm" x="{JOG_CX}" y="{JOG_CY + 3.2:.2f}">Note 36</text>')
    parts.append('</g>')

    # ---------- Tempo arc（Jog 同心、右側） ----------
    parts.append('<g id="tempo">')
    parts.append(
        f'  <text class="title" x="148" y="58">速度 Tempo</text>'
    )
    parts.append(
        f'  <text class="body" x="148" y="62">14-bit CC 14/46</text>'
    )
    parts.append(
        f'  <text class="body" x="148" y="65.5">MPR#2 Ch0–9（10 片）</text>'
    )
    start_a = -TEMPO_SPAN / 2  # -50
    for i in range(10):
        a1 = start_a + i * (TEMPO_SEG_DEG + TEMPO_GAP_DEG)
        a2 = a1 + TEMPO_SEG_DEG
        path = annular_sector(JOG_CX, JOG_CY, TEMPO_R_IN, TEMPO_R_OUT, a1, a2)
        parts.append(f'  <path class="pad" d="{path}" />')
        # 焊線尾向外
        tail_r1 = TEMPO_R_OUT + 0.5
        tail_r2 = TEMPO_R_OUT + 4.0
        mid = (a1 + a2) / 2
        tail_a1 = mid - 1.0
        tail_a2 = mid + 1.0
        tail_path = annular_sector(JOG_CX, JOG_CY, tail_r1, tail_r2, tail_a1, tail_a2)
        parts.append(f'  <path class="tail" d="{tail_path}" />')
        # label
        r_mid = (TEMPO_R_IN + TEMPO_R_OUT) / 2
        lx, ly = pol(JOG_CX, JOG_CY, r_mid, mid)
        parts.append(f'  <text class="lbl"    x="{lx:.2f}" y="{ly - 0.2:.2f}">T{i}</text>')
        parts.append(f'  <text class="lbl-sm" x="{lx:.2f}" y="{ly + 2.2:.2f}">C{i}</text>')
    parts.append('</g>')

    # ---------- SYNC 膠囊 ----------
    parts.append('<g id="sync">')
    rx = SYNC_W / 2
    parts.append(
        f'  <rect class="pad-b" x="{SYNC_X}" y="{SYNC_Y}" width="{SYNC_W}" height="{SYNC_H}" '
        f'rx="{rx}" ry="{rx}" />'
    )
    parts.append(
        f'  <rect class="tail" x="{SYNC_X + SYNC_W - 1:.2f}" y="{SYNC_Y + SYNC_H/2 - 1.5:.2f}" '
        f'width="4" height="3" />'
    )
    parts.append(
        f'  <text class="lbl"    x="{SYNC_X + SYNC_W/2:.2f}" y="{SYNC_Y + SYNC_H/2 - 1:.2f}">SYNC</text>'
    )
    parts.append(
        f'  <text class="lbl-sm" x="{SYNC_X + SYNC_W/2:.2f}" y="{SYNC_Y + SYNC_H/2 + 1.8:.2f}">'
        f'M#1 Ch10</text>'
    )
    parts.append(
        f'  <text class="lbl-sm" x="{SYNC_X + SYNC_W/2:.2f}" y="{SYNC_Y + SYNC_H/2 + 4.1:.2f}">'
        f'Note 38</text>'
    )
    parts.append('</g>')

    # ---------- Play 膠囊（含三角形圖示） ----------
    parts.append('<g id="play">')
    rx = PLAY_W / 2
    parts.append(
        f'  <rect class="pad-b" x="{PLAY_X}" y="{PLAY_Y}" width="{PLAY_W}" height="{PLAY_H}" '
        f'rx="{rx}" ry="{rx}" />'
    )
    parts.append(
        f'  <rect class="tail" x="{PLAY_X + PLAY_W - 1:.2f}" y="{PLAY_Y + PLAY_H/2 - 1.5:.2f}" '
        f'width="4" height="3" />'
    )
    # ▶ 小三角（hint 用，銅箔不剪這個，純標示）
    tri_cx = PLAY_X + PLAY_W / 2
    tri_cy = PLAY_Y + 7
    parts.append(
        f'  <polygon class="hint" points="'
        f'{tri_cx - 2.5:.2f},{tri_cy - 2.5:.2f} '
        f'{tri_cx - 2.5:.2f},{tri_cy + 2.5:.2f} '
        f'{tri_cx + 3:.2f},{tri_cy:.2f}" />'
    )
    parts.append(
        f'  <text class="lbl"    x="{PLAY_X + PLAY_W/2:.2f}" y="{PLAY_Y + PLAY_H/2 + 3:.2f}">Play</text>'
    )
    parts.append(
        f'  <text class="lbl-sm" x="{PLAY_X + PLAY_W/2:.2f}" y="{PLAY_Y + PLAY_H/2 + 5.8:.2f}">'
        f'M#1 Ch9</text>'
    )
    parts.append(
        f'  <text class="lbl-sm" x="{PLAY_X + PLAY_W/2:.2f}" y="{PLAY_Y + PLAY_H/2 + 8.1:.2f}">'
        f'Note 37</text>'
    )
    parts.append('</g>')

    # ---------- 4 PAD ----------
    parts.append('<g id="pads">')
    parts.append('  <text class="title" x="22" y="175">表演觸鍵 PAD1–4</text>')
    for (name, mpr, note), x in zip(PAD_META, PAD_XS):
        parts.append(
            f'  <rect class="pad-p" x="{x}" y="{PAD_Y}" width="{PAD_W}" height="{PAD_H}" '
            f'rx="2" ry="2" />'
        )
        parts.append(
            f'  <rect class="tail" x="{x + PAD_W - 1:.2f}" y="{PAD_Y + PAD_H/2 - 2:.2f}" '
            f'width="4" height="4" />'
        )
        parts.append(f'  <text class="lbl"    x="{x + PAD_W/2:.2f}" y="{PAD_Y + 12:.2f}">{name}</text>')
        parts.append(f'  <text class="lbl-sm" x="{x + PAD_W/2:.2f}" y="{PAD_Y + 16:.2f}">{mpr}</text>')
        parts.append(f'  <text class="lbl-sm" x="{x + PAD_W/2:.2f}" y="{PAD_Y + 19:.2f}">{note}</text>')
    parts.append('</g>')

    # ---------- Volume fader ----------
    parts.append('<g id="volume">')
    parts.append(
        f'  <text class="title" x="{VOL_X0:.2f}" y="{VOL_Y - 3:.2f}">'
        f'音量 Volume（CC 7 7-bit）— MPR#3 Ch0–4</text>'
    )
    for i in range(VOL_N):
        x = VOL_X0 + i * (VOL_W + VOL_GAP)
        parts.append(
            f'  <rect class="pad" x="{x:.2f}" y="{VOL_Y}" width="{VOL_W}" height="{VOL_H}" '
            f'rx="1.5" ry="1.5" />'
        )
        parts.append(
            f'  <rect class="tail" x="{x + VOL_W/2 - 1.5:.2f}" y="{VOL_Y + VOL_H + 0.5:.2f}" '
            f'width="3" height="4" />'
        )
        parts.append(
            f'  <text class="lbl"    x="{x + VOL_W/2:.2f}" y="{VOL_Y + VOL_H/2 - 1:.2f}">V{i}</text>'
        )
        parts.append(
            f'  <text class="lbl-sm" x="{x + VOL_W/2:.2f}" y="{VOL_Y + VOL_H/2 + 1.8:.2f}">'
            f'M#3 C{i}</text>'
        )
    parts.append('</g>')

    # ---------- 圖例 + 流程 ----------
    parts.append('<g id="legend" transform="translate(148,182)">')
    parts.append('  <text class="legend-title" x="0" y="0">圖例</text>')
    items = [
        ("pad-cue", "綠 = CUE（中央主鍵）"),
        ("pad-j",   "灰 = Jog 弧片 J0–J7"),
        ("pad-b",   "藍 = SYNC / Play 膠囊"),
        ("pad-p",   "紅 = PAD"),
        ("pad",     "黃 = Slider / Fader 片"),
    ]
    for i, (cls, text) in enumerate(items):
        y = 4 + i * 4.3
        parts.append(f'  <rect class="{cls}" x="0" y="{y:.2f}" width="5" height="3" />')
        parts.append(f'  <text class="body"  x="7" y="{y + 2.5:.2f}">{text}</text>')
    parts.append('  <rect class="tail" x="0" y="27" width="5" height="3" />')
    parts.append('  <text class="body"  x="7" y="29.5">虛線格 = 焊線尾（延伸銅箔 3–4 mm 當接點）</text>')
    parts.append('</g>')

    parts.append('<g id="flow" transform="translate(8,268)">')
    parts.append('  <text class="title" x="0" y="0">建議流程（詳見 docs/hardware/08-prototype-assembly.md）</text>')
    parts.append('  <text class="body" x="0" y="4">1. 印這張 → 量右上校正方塊 → 10 mm 才繼續。</text>')
    parts.append('  <text class="body" x="0" y="7.5">2. 銅箔膠帶覆貼在紙上每個電極形狀 → 美工刀沿實線連紙一起剪。</text>')
    parts.append('  <text class="body" x="0" y="11">3. 撕下貼到壓克力板；焊線尾朝外 → 焊或導電膠接杜邦線 → 接到對應 MPR121 腳。</text>')
    parts.append('  <text class="body" x="0" y="14.5">4. 30 點全接完 → 跑 06-testing-plan.md Phase 1–4。 '
                 'channel 對照：M#1 0x5A (Jog+CUE/Play/SYNC/PAD1)  M#2 0x5B (Tempo+PAD2/3)  M#3 0x5C (Volume+PAD4)</text>')
    parts.append('</g>')

    # ---------- 外框 ----------
    parts.append('<rect class="frame" x="5" y="5" width="200" height="287" />')
    parts.append('</svg>')
    return "\n".join(parts) + "\n"


def main() -> int:
    svg = build_svg()
    os.makedirs(os.path.dirname(OUT_SVG), exist_ok=True)
    with open(OUT_SVG, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote {OUT_SVG} ({len(svg)} bytes)")

    import cairosvg
    # 300 dpi ≈ 11.811 px/mm → 210*11.811 ≈ 2480 px wide
    cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=OUT_PNG, output_width=2480)
    size = os.path.getsize(OUT_PNG)
    print(f"wrote {OUT_PNG} ({size} bytes, ~300 dpi)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
