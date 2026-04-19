/**
 * MidiMonitor — webmidi.ts 的 smoke-test UI
 *
 * 用法：import 進 App.tsx 任一地方，會顯示 fixed 右下角小 panel，列出：
 *   - MIDI 連線狀態 / 錯誤訊息
 *   - 偵測到的 MIDI 輸入裝置名稱
 *   - 最近 10 筆解析後的 FlowDjEvent
 *   - 最近 1 筆 raw MIDI（cc/note/channel）
 *
 * 可用 ?midi=1 當啟用條件，或直接無條件渲染。
 */

import { useMidi, FlowDjEvent, MidiRawEvent } from './webmidi';

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

export function MidiMonitor() {
  const { status, error, inputNames, lastRawEvent, eventLog } = useMidi({ logSize: 10 });

  const statusColor = {
    idle: '#888',
    connecting: '#fbbf24',
    ready: '#22c55e',
    unsupported: '#ef4444',
    error: '#ef4444',
  }[status];

  return (
    <div
      style={{
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
        pointerEvents: 'none', // smoke test only, 不擋 UI 點擊
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <strong style={{ fontSize: 12 }}>MIDI Monitor</strong>
        <span style={{ color: statusColor }}>● {status}</span>
      </div>

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
