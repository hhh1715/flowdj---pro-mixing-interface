/**
 * MidiMonitor — webmidi.ts 的 smoke-test UI
 *
 * 兩個 entry point：
 *   - <MidiMonitorToggle />：行內小膠囊，顯示 ● 燈號 + "MIDI"，點開 / 收。
 *   - <MidiMonitor />：展開時的浮動 panel（fixed 右下，列出最近事件）。
 *
 * 兩者透過 localStorage + 'midi-monitor-toggle' custom event 同步狀態，
 * 不需要 lift state up 到 App.tsx。
 */

import type { CSSProperties } from 'react';
import { useEffect, useState } from 'react';
import { useMidi, FlowDjEvent, MidiRawEvent } from './webmidi';

const COLLAPSED_KEY = 'midi-monitor-collapsed';
const TOGGLE_EVENT = 'midi-monitor-toggle';

// ── 共用：collapsed 狀態跟 localStorage 同步 + 跨元件廣播 ─────────────────────
function useCollapsedState(): [boolean, (next: boolean) => void] {
  const [collapsed, setCollapsedState] = useState<boolean>(() => {
    if (typeof window === 'undefined') return false;
    return window.localStorage.getItem(COLLAPSED_KEY) === '1';
  });

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const onToggle = (e: Event) => {
      const next = (e as CustomEvent<boolean>).detail;
      setCollapsedState(next);
    };
    window.addEventListener(TOGGLE_EVENT, onToggle);
    return () => window.removeEventListener(TOGGLE_EVENT, onToggle);
  }, []);

  const setCollapsed = (next: boolean) => {
    if (typeof window === 'undefined') return;
    window.localStorage.setItem(COLLAPSED_KEY, next ? '1' : '0');
    window.dispatchEvent(new CustomEvent(TOGGLE_EVENT, { detail: next }));
  };

  return [collapsed, setCollapsed];
}

// ── 共用：把 status 轉成色票 ─────────────────────────────────────────────────
const STATUS_COLORS = {
  idle: '#888',
  connecting: '#fbbf24',
  ready: '#22c55e',
  unsupported: '#ef4444',
  error: '#ef4444',
} as const;

function formatEvent(e: FlowDjEvent): string {
  switch (e.type) {
    case 'button':
      return `button:${e.button} ${e.pressed ? 'DOWN' : 'UP'}`;
    case 'tempo':
      return `tempo: ${e.value14bit} (${(e.normalized * 100).toFixed(1)}%)`;
    case 'volume':
      return `volume: ${e.value} (${(e.normalized * 100).toFixed(0)}%)`;
    case 'jogDelta':
      return `jog: ${e.delta > 0 ? '+' : ''}${e.delta}`;
  }
}

function formatRaw(e: MidiRawEvent): string {
  if (e.type === 'controlChange') return `CC ${e.cc}=${e.value} ch${e.channel}`;
  return `${e.type} note=${e.note}${e.type === 'noteOn' ? ` vel=${e.velocity}` : ''} ch${e.channel}`;
}

// ── 行內按鈕：樣式對齊 CUE / Play 等 transport secondary 鈕 ────────────────────
const TRANSPORT_SECONDARY_CLASS =
  "px-4 [@media(hover:none)_and_(pointer:coarse)_and_(min-width:820px)_and_(max-width:1180px)_and_(max-height:900px)]:px-3 " +
  "h-10 [@media(hover:none)_and_(pointer:coarse)_and_(min-width:820px)_and_(max-width:1180px)_and_(max-height:900px)]:h-8 " +
  "rounded-xl flex items-center justify-center gap-1.5 transition-all " +
  "shadow-[2px_2px_4px_#2a2a2a,-2px_-2px_4px_#4e4e4e] " +
  "active:shadow-[inset_2px_2px_4px_#2a2a2a,inset_-2px_-2px_4px_#4e4e4e] active:scale-95 " +
  "border border-white/10 bg-[#D0D0D0] text-[#3C3C3C]";

export function MidiMonitorToggle() {
  const { status } = useMidi({ logSize: 1 });
  const [collapsed, setCollapsed] = useCollapsedState();
  const statusColor = STATUS_COLORS[status];

  return (
    <button
      type="button"
      onClick={() => setCollapsed(!collapsed)}
      aria-label={collapsed ? 'Expand MIDI Monitor' : 'Collapse MIDI Monitor'}
      aria-expanded={!collapsed}
      title={`MIDI: ${status}`}
      className={TRANSPORT_SECONDARY_CLASS}
    >
      <span style={{ color: statusColor, fontSize: 11, lineHeight: 1 }}>●</span>
      <span className="text-[10px] [@media(hover:none)_and_(pointer:coarse)_and_(min-width:820px)_and_(max-width:1180px)_and_(max-height:900px)]:text-[9px] font-bold tracking-widest">
        MIDI
      </span>
    </button>
  );
}

// ── 展開時的浮動 panel ───────────────────────────────────────────────────────
export function MidiMonitor() {
  const { status, error, inputNames, lastRawEvent, eventLog } = useMidi({ logSize: 10 });
  const [collapsed, setCollapsed] = useCollapsedState();

  if (collapsed) return null;

  const statusColor = STATUS_COLORS[status];

  const baseStyle: CSSProperties = {
    position: 'fixed',
    right: 12,
    bottom: 12,
    width: 340,
    maxHeight: 280,
    background: 'rgba(15, 15, 20, 0.92)',
    color: '#e5e5e5',
    fontFamily: 'ui-monospace, Menlo, monospace',
    fontSize: 11,
    padding: 10,
    borderRadius: 8,
    border: '1px solid rgba(255,255,255,0.1)',
    zIndex: 9999,
    overflow: 'hidden',
    display: 'flex',
    flexDirection: 'column',
    gap: 6,
  };

  return (
    <div style={baseStyle}>
      <button
        type="button"
        onClick={() => setCollapsed(true)}
        aria-label="Collapse MIDI Monitor"
        style={{
          all: 'unset',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          cursor: 'pointer',
        }}
      >
        <strong style={{ fontSize: 12 }}>MIDI Monitor</strong>
        <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ color: statusColor }}>● {status}</span>
          <span style={{ color: '#888', fontSize: 14, lineHeight: 1 }}>−</span>
        </span>
      </button>

      {error && (
        <div style={{ color: '#fca5a5' }}>error: {error.message}</div>
      )}

      <div style={{ color: '#a3a3a3' }}>
        inputs: {inputNames.length === 0 ? '(none)' : inputNames.join(', ')}
      </div>

      {lastRawEvent && (
        <div style={{ color: '#93c5fd' }}>raw: {formatRaw(lastRawEvent)}</div>
      )}

      <div style={{ borderTop: '1px solid rgba(255,255,255,0.08)', paddingTop: 4, overflowY: 'auto' }}>
        {eventLog.length === 0 ? (
          <div style={{ color: '#666' }}>(waiting for events…)</div>
        ) : (
          eventLog
            .slice()
            .reverse()
            .map((e, i) => (
              <div key={eventLog.length - i} style={{ lineHeight: 1.4 }}>
                {formatEvent(e)}
              </div>
            ))
        )}
      </div>
    </div>
  );
}
