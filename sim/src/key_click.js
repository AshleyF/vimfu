// ── Key-click sound player ──
// Decodes embedded MP3 base64 data on first use and plays short
// click sounds through the Web Audio API for minimal latency.

import { SOUND_DATA } from './key_sounds.js';

const STORAGE_KEY = 'vimfu-sound';
const POOL_SIZE   = 4;          // pre-decoded copies per sound for overlap

let _ctx   = null;              // AudioContext (created lazily)
let _pool  = {};                // name → AudioBuffer[]
let _idx   = {};                // name → round-robin index
let _ready = false;
let _enabled = localStorage.getItem(STORAGE_KEY) !== '0'; // on by default

// ── Public API ──

/** Is sound currently enabled? */
function isSoundEnabled() { return _enabled; }

/** Toggle sound on/off, persists to localStorage. */
function setSoundEnabled(on) {
  _enabled = on;
  localStorage.setItem(STORAGE_KEY, on ? '1' : '0');
}

/** Warm up the AudioContext (call on first user gesture). */
async function initAudio() {
  if (_ctx) return;
  _ctx = new (window.AudioContext || window.webkitAudioContext)();
  // Decode all sounds in parallel
  const entries = Object.entries(SOUND_DATA);
  const decoded = await Promise.all(
    entries.map(async ([name, b64]) => {
      const bin = Uint8Array.from(atob(b64), c => c.charCodeAt(0));
      const buf = await _ctx.decodeAudioData(bin.buffer.slice(0));
      return [name, buf];
    })
  );
  for (const [name, buf] of decoded) {
    _pool[name] = Array.from({ length: POOL_SIZE }, () => buf);
    _idx[name]  = 0;
  }
  _ready = true;
}

/** Play the click sound for a given key name (e.g. 'a', 'Enter', ' '). */
function playKey(key) {
  if (!_enabled || !_ready) return;

  const soundName = mapKeyToSound(key);
  const buffers = _pool[soundName];
  if (!buffers) return;

  const buf  = buffers[_idx[soundName] % POOL_SIZE];
  _idx[soundName] = (_idx[soundName] + 1) % POOL_SIZE;

  const src  = _ctx.createBufferSource();
  src.buffer = buf;
  src.connect(_ctx.destination);
  src.start(0);
}

// ── Key → sound mapping ──
// Letters and special keys map directly; everything else gets a
// random letter sound for variety.

const LETTER_KEYS = new Set('ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split(''));
const SPECIAL_MAP = {
  'Backspace': 'BACKSPACE',
  'Enter':     'ENTER',
  ' ':         'SPACE',
  'Tab':       'SPACE',      // reuse space sound
  'Escape':    'BACKSPACE',  // reuse backspace sound
};

function mapKeyToSound(key) {
  // Direct letter match
  const upper = key.length === 1 ? key.toUpperCase() : '';
  if (LETTER_KEYS.has(upper)) return upper;

  // Special keys
  if (SPECIAL_MAP[key]) return SPECIAL_MAP[key];

  // Ctrl-X → use the letter
  if (key.startsWith('Ctrl-') && key.length === 6) {
    const letter = key[5].toUpperCase();
    if (LETTER_KEYS.has(letter)) return letter;
  }

  // Digits and symbols → pick a pseudo-random letter based on char code
  if (key.length === 1) {
    const code = key.charCodeAt(0);
    const letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    return letters[code % 26];
  }

  // Arrow keys, etc. → use a generic click
  return 'SPACE';
}

export { initAudio, playKey, isSoundEnabled, setSoundEnabled };
