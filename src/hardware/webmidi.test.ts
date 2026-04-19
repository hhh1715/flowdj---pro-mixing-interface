import { describe, expect, it } from 'vitest';
import { FlowDjMidiMapper, parseMidiMessage } from './webmidi';

const bytes = (...xs: number[]) => new Uint8Array(xs);

describe('parseMidiMessage', () => {
  it('parses Note On', () => {
    expect(parseMidiMessage(bytes(0x90, 36, 127))).toEqual({
      type: 'noteOn',
      channel: 1,
      note: 36,
      velocity: 127,
    });
  });

  it('treats Note On velocity=0 as Note Off (MIDI 1.0 convention)', () => {
    expect(parseMidiMessage(bytes(0x90, 36, 0))).toEqual({
      type: 'noteOff',
      channel: 1,
      note: 36,
    });
  });

  it('parses explicit Note Off (status 0x80)', () => {
    expect(parseMidiMessage(bytes(0x80, 36, 0))).toEqual({
      type: 'noteOff',
      channel: 1,
      note: 36,
    });
  });

  it('parses Control Change', () => {
    expect(parseMidiMessage(bytes(0xb0, 7, 64))).toEqual({
      type: 'controlChange',
      channel: 1,
      cc: 7,
      value: 64,
    });
  });

  it('decodes channel nibble (0x91 = channel 2)', () => {
    const ev = parseMidiMessage(bytes(0x91, 36, 127));
    expect(ev).not.toBeNull();
    expect(ev!.channel).toBe(2);
  });

  it('decodes channel nibble (0xBF = channel 16)', () => {
    const ev = parseMidiMessage(bytes(0xbf, 7, 0));
    expect(ev!.channel).toBe(16);
  });

  it('returns null for unknown status (poly aftertouch 0xA0)', () => {
    expect(parseMidiMessage(bytes(0xa0, 36, 127))).toBeNull();
  });

  it('returns null for short packet', () => {
    expect(parseMidiMessage(bytes(0x90))).toBeNull();
    expect(parseMidiMessage(new Uint8Array())).toBeNull();
  });

  it('tolerates missing data2 byte on CC (treat as 0)', () => {
    expect(parseMidiMessage(bytes(0xb0, 7))).toEqual({
      type: 'controlChange',
      channel: 1,
      cc: 7,
      value: 0,
    });
  });
});

describe('FlowDjMidiMapper — buttons', () => {
  it('maps CUE Note On → button cue pressed', () => {
    const m = new FlowDjMidiMapper();
    expect(m.map({ type: 'noteOn', channel: 1, note: 36, velocity: 127 })).toEqual({
      type: 'button',
      button: 'cue',
      pressed: true,
    });
  });

  it('maps CUE Note Off → button cue released', () => {
    const m = new FlowDjMidiMapper();
    expect(m.map({ type: 'noteOff', channel: 1, note: 36 })).toEqual({
      type: 'button',
      button: 'cue',
      pressed: false,
    });
  });

  it('maps all documented notes (Play/SYNC/PAD1-4/JogTouch)', () => {
    const m = new FlowDjMidiMapper();
    const notes: Array<[number, string]> = [
      [37, 'play'],
      [38, 'sync'],
      [40, 'pad1'],
      [41, 'pad2'],
      [42, 'pad3'],
      [43, 'pad4'],
      [48, 'jogTouch'],
    ];
    for (const [note, button] of notes) {
      const ev = m.map({ type: 'noteOn', channel: 1, note, velocity: 127 });
      expect(ev).toEqual({ type: 'button', button, pressed: true });
    }
  });

  it('returns null for unmapped note (e.g. 50)', () => {
    const m = new FlowDjMidiMapper();
    expect(m.map({ type: 'noteOn', channel: 1, note: 50, velocity: 127 })).toBeNull();
  });
});

describe('FlowDjMidiMapper — volume (CC 7)', () => {
  it('emits normalized value 0 for CC 7 = 0', () => {
    const m = new FlowDjMidiMapper();
    expect(m.map({ type: 'controlChange', channel: 1, cc: 7, value: 0 })).toEqual({
      type: 'volume',
      value: 0,
      normalized: 0,
    });
  });

  it('emits normalized value 1 for CC 7 = 127', () => {
    const m = new FlowDjMidiMapper();
    const ev = m.map({ type: 'controlChange', channel: 1, cc: 7, value: 127 });
    expect(ev!.type).toBe('volume');
    expect((ev as { normalized: number }).normalized).toBe(1);
  });
});

describe('FlowDjMidiMapper — 14-bit tempo (CC 14 + 46)', () => {
  it('merges MSB + LSB into 14-bit tempo', () => {
    const m = new FlowDjMidiMapper();
    m.map({ type: 'controlChange', channel: 1, cc: 14, value: 64 }); // MSB
    const ev = m.map({ type: 'controlChange', channel: 1, cc: 46, value: 0 }); // LSB
    // 14-bit = (64 << 7) | 0 = 8192
    expect(ev).toEqual({
      type: 'tempo',
      value14bit: 8192,
      normalized: 8192 / 16383,
    });
  });

  it('emits 0 when both MSB and LSB are 0', () => {
    const m = new FlowDjMidiMapper();
    m.map({ type: 'controlChange', channel: 1, cc: 14, value: 0 });
    const ev = m.map({ type: 'controlChange', channel: 1, cc: 46, value: 0 });
    expect(ev).toEqual({ type: 'tempo', value14bit: 0, normalized: 0 });
  });

  it('emits 16383 when both MSB and LSB are 127 (full range)', () => {
    const m = new FlowDjMidiMapper();
    m.map({ type: 'controlChange', channel: 1, cc: 14, value: 127 });
    const ev = m.map({ type: 'controlChange', channel: 1, cc: 46, value: 127 });
    expect(ev).toEqual({ type: 'tempo', value14bit: 16383, normalized: 1 });
  });

  it('emits intermediate events during MSB-first sequence', () => {
    // 韌體送 MSB 先、LSB 後；中間那一步 UI 會收到半完整值 — 這是預期行為
    // 真實系統會靠後續 LSB 訊息立刻更新，UI 不會卡在錯值
    const m = new FlowDjMidiMapper();
    const afterMsb = m.map({ type: 'controlChange', channel: 1, cc: 14, value: 64 });
    expect(afterMsb!.type).toBe('tempo');
    // 僅 MSB = 64 時，尚無 LSB → raw = 64 << 7 = 8192
    expect((afterMsb as { value14bit: number }).value14bit).toBe(8192);
  });
});

describe('FlowDjMidiMapper — Jog CC 16 signed 7-bit', () => {
  it('emits delta 0 for value 64 (center / no motion)', () => {
    const m = new FlowDjMidiMapper();
    expect(m.map({ type: 'controlChange', channel: 1, cc: 16, value: 64 })).toEqual({
      type: 'jogDelta',
      delta: 0,
    });
  });

  it('emits positive delta for clockwise (value > 64)', () => {
    const m = new FlowDjMidiMapper();
    expect(m.map({ type: 'controlChange', channel: 1, cc: 16, value: 70 })).toEqual({
      type: 'jogDelta',
      delta: 6,
    });
  });

  it('emits negative delta for counter-clockwise (value < 64)', () => {
    const m = new FlowDjMidiMapper();
    expect(m.map({ type: 'controlChange', channel: 1, cc: 16, value: 58 })).toEqual({
      type: 'jogDelta',
      delta: -6,
    });
  });

  it('handles range extremes (127 and 1)', () => {
    const m = new FlowDjMidiMapper();
    expect(m.map({ type: 'controlChange', channel: 1, cc: 16, value: 127 })).toEqual({
      type: 'jogDelta',
      delta: 63,
    });
    expect(m.map({ type: 'controlChange', channel: 1, cc: 16, value: 1 })).toEqual({
      type: 'jogDelta',
      delta: -63,
    });
  });
});

describe('FlowDjMidiMapper — unknown', () => {
  it('returns null for unmapped CC (e.g. CC 99)', () => {
    const m = new FlowDjMidiMapper();
    expect(m.map({ type: 'controlChange', channel: 1, cc: 99, value: 64 })).toBeNull();
  });
});
