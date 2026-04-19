/**
 * FlowDJ Web MIDI 層
 *
 * 對應 docs/hardware/04-midi-protocol.md 的訊息表：
 *   按鈕（Note On/Off）     : CUE=36, Play=37, SYNC=38, PAD1-4=40-43, JogTouch=48
 *   音量 fader（CC 7）      : 0–127 → 0.0–1.0
 *   速度 slider（CC 14+46） : 14-bit = (MSB << 7) | LSB → 0–16383 → 0.0–1.0
 *   Jog 相對速度（CC 16）   : signed 7-bit, 64 = 靜止, 值 - 64 = delta
 *
 * 瀏覽器支援：Chrome/Edge/Opera、Firefox 134+；Safari 不支援。
 */

import { useCallback, useEffect, useRef, useState } from 'react';

// ─── 原始 MIDI 事件（去掉 status byte 的編碼細節） ────────────────────────────
export type MidiRawEvent =
  | { type: 'noteOn'; channel: number; note: number; velocity: number }
  | { type: 'noteOff'; channel: number; note: number }
  | { type: 'controlChange'; channel: number; cc: number; value: number };

// ─── FlowDJ 高階事件（已轉成 UI 層語意） ──────────────────────────────────────
export type FlowDjButton =
  | 'cue' | 'play' | 'sync' | 'pad1' | 'pad2' | 'pad3' | 'pad4' | 'jogTouch';

export type FlowDjEvent =
  | { type: 'button'; button: FlowDjButton; pressed: boolean }
  | { type: 'tempo'; value14bit: number; normalized: number } // 0–16383, 0–1
  | { type: 'volume'; value: number; normalized: number }     // 0–127, 0–1
  | { type: 'jogDelta'; delta: number };                       // -63…+63

const NOTE_TO_BUTTON: Record<number, FlowDjButton> = {
  36: 'cue',
  37: 'play',
  38: 'sync',
  40: 'pad1',
  41: 'pad2',
  42: 'pad3',
  43: 'pad4',
  48: 'jogTouch',
};

// ─── Raw parser：Uint8Array → MidiRawEvent ────────────────────────────────────
export function parseMidiMessage(data: Uint8Array): MidiRawEvent | null {
  if (data.length < 2) return null;
  const status = data[0] & 0xf0;
  const channel = (data[0] & 0x0f) + 1; // 1-based（跟 Teensy usbMIDI API 一致）

  if (status === 0x90) {
    // Note On，但 velocity=0 依 MIDI 1.0 視為 Note Off
    const velocity = data[2] ?? 0;
    if (velocity === 0) return { type: 'noteOff', channel, note: data[1] };
    return { type: 'noteOn', channel, note: data[1], velocity };
  }
  if (status === 0x80) {
    return { type: 'noteOff', channel, note: data[1] };
  }
  if (status === 0xb0) {
    return { type: 'controlChange', channel, cc: data[1], value: data[2] ?? 0 };
  }
  return null;
}

// ─── Mapper：MidiRawEvent → FlowDjEvent（有狀態，為了 14-bit CC 合併） ────────
export class FlowDjMidiMapper {
  private tempoMsb = 0;
  private tempoLsb = 0;

  map(event: MidiRawEvent): FlowDjEvent | null {
    if (event.type === 'noteOn') {
      const btn = NOTE_TO_BUTTON[event.note];
      if (btn) return { type: 'button', button: btn, pressed: true };
      return null;
    }
    if (event.type === 'noteOff') {
      const btn = NOTE_TO_BUTTON[event.note];
      if (btn) return { type: 'button', button: btn, pressed: false };
      return null;
    }
    if (event.type === 'controlChange') {
      if (event.cc === 7) {
        return { type: 'volume', value: event.value, normalized: event.value / 127 };
      }
      if (event.cc === 14) {
        this.tempoMsb = event.value;
        return this.makeTempoEvent();
      }
      if (event.cc === 46) {
        this.tempoLsb = event.value;
        return this.makeTempoEvent();
      }
      if (event.cc === 16) {
        return { type: 'jogDelta', delta: event.value - 64 };
      }
    }
    return null;
  }

  private makeTempoEvent(): FlowDjEvent {
    const raw = (this.tempoMsb << 7) | this.tempoLsb;
    return { type: 'tempo', value14bit: raw, normalized: raw / 16383 };
  }
}

// ─── 低層：initMidi（回傳 cleanup 函式） ──────────────────────────────────────
export interface InitMidiOptions {
  onEvent?: (event: FlowDjEvent) => void;
  onRawEvent?: (event: MidiRawEvent) => void;
  onInputsChanged?: (names: string[]) => void;
}

export interface MidiHandle {
  cleanup: () => void;
  inputNames: string[];
}

export async function initMidi(options: InitMidiOptions = {}): Promise<MidiHandle> {
  if (typeof navigator === 'undefined' || !navigator.requestMIDIAccess) {
    throw new Error('Web MIDI API not supported — use Chrome/Edge or Firefox 134+');
  }

  const access = await navigator.requestMIDIAccess();
  const mapper = new FlowDjMidiMapper();

  const handler = (e: Event) => {
    const msg = e as MIDIMessageEvent;
    if (!msg.data) return;
    const raw = parseMidiMessage(msg.data);
    if (!raw) return;
    options.onRawEvent?.(raw);
    const mapped = mapper.map(raw);
    if (mapped) options.onEvent?.(mapped);
  };

  const attached: MIDIInput[] = [];
  for (const input of access.inputs.values()) {
    input.addEventListener('midimessage', handler);
    attached.push(input);
  }

  const inputNames = attached.map((i) => i.name ?? '(unnamed)');
  options.onInputsChanged?.(inputNames);

  return {
    cleanup: () => {
      for (const input of attached) {
        input.removeEventListener('midimessage', handler);
      }
    },
    inputNames,
  };
}

// ─── React hook ────────────────────────────────────────────────────────────────
export type MidiStatus = 'idle' | 'connecting' | 'ready' | 'unsupported' | 'error';

export interface UseMidiResult {
  status: MidiStatus;
  error: Error | null;
  inputNames: string[];
  lastEvent: FlowDjEvent | null;
  lastRawEvent: MidiRawEvent | null;
  eventLog: FlowDjEvent[]; // 保留最近 N 筆，方便 smoke test
  /**
   * 手動送一個事件。
   * - mock 模式（`useMidi({ mock: true })`）：觸發跟真硬體一樣的 state 更新
   * - 正常模式：no-op（呼叫不會有事，方便整合期的暫時填充）
   */
  emit: (event: FlowDjEvent) => void;
}

export interface UseMidiOptions {
  logSize?: number; // eventLog 容量，預設 50
  onEvent?: (event: FlowDjEvent) => void; // 即時回呼（不受 logSize 限制）
  /**
   * 若為 true，完全跳過 navigator.requestMIDIAccess，不連實體硬體。
   * 狀態會立刻變 'ready'、inputNames=['(mock)']。用 `emit()` 手動注入事件。
   * 用途：設計系 UI 還沒接到實體控制器前，先驗證整合邏輯。
   */
  mock?: boolean;
}

export function useMidi(options: UseMidiOptions = {}): UseMidiResult {
  const { logSize = 50, mock = false } = options;
  const [status, setStatus] = useState<MidiStatus>('idle');
  const [error, setError] = useState<Error | null>(null);
  const [inputNames, setInputNames] = useState<string[]>([]);
  const [lastEvent, setLastEvent] = useState<FlowDjEvent | null>(null);
  const [lastRawEvent, setLastRawEvent] = useState<MidiRawEvent | null>(null);
  const [eventLog, setEventLog] = useState<FlowDjEvent[]>([]);

  const onEventRef = useRef(options.onEvent);
  onEventRef.current = options.onEvent;

  // emit() 要能從 hook 外部叫到，但 pushEvent 的邏輯住在 useEffect 裡為了 cleanup。
  // 用 ref 橋接：effect 建好 pushEvent 後放進 ref；emit 從 ref 讀。
  const pushEventRef = useRef<((event: FlowDjEvent) => void) | null>(null);

  useEffect(() => {
    let cancelled = false;
    let handle: MidiHandle | null = null;

    const pushEvent = (e: FlowDjEvent) => {
      if (cancelled) return;
      setLastEvent(e);
      setEventLog((prev) => {
        const next = prev.length >= logSize ? prev.slice(prev.length - logSize + 1) : prev;
        return [...next, e];
      });
      onEventRef.current?.(e);
    };
    pushEventRef.current = pushEvent;

    if (mock) {
      setStatus('ready');
      setInputNames(['(mock)']);
      setError(null);
      return () => {
        cancelled = true;
        pushEventRef.current = null;
      };
    }

    setStatus('connecting');
    initMidi({
      onEvent: pushEvent,
      onRawEvent: (e) => {
        if (cancelled) return;
        setLastRawEvent(e);
      },
      onInputsChanged: (names) => {
        if (cancelled) return;
        setInputNames(names);
      },
    })
      .then((h) => {
        if (cancelled) {
          h.cleanup();
          return;
        }
        handle = h;
        setStatus('ready');
      })
      .catch((err: Error) => {
        if (cancelled) return;
        const isUnsupported = /not supported/i.test(err.message);
        setStatus(isUnsupported ? 'unsupported' : 'error');
        setError(err);
      });

    return () => {
      cancelled = true;
      pushEventRef.current = null;
      handle?.cleanup();
    };
  }, [logSize, mock]);

  const emit = useCallback((event: FlowDjEvent) => {
    pushEventRef.current?.(event);
  }, []);

  return { status, error, inputNames, lastEvent, lastRawEvent, eventLog, emit };
}
