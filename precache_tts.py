"""Pre-cache TTS audio clips for a lesson.

Usage: python precache_tts.py curriculum/shorts/0042_example.json
       python precache_tts.py curriculum/shorts/0042_example.py   (resolves .json)

Runs the TTS generation in isolation, retrying failed clips.
Once cached, the lesson script will start instantly.
"""

import sys
from pathlib import Path

if len(sys.argv) < 2:
    print("Usage: python precache_tts.py <lesson.json>")
    sys.exit(1)

target = Path(sys.argv[1]).resolve()
# Accept .py and auto-resolve to .json
if target.suffix == ".py":
    target = target.with_suffix(".json")
if not target.exists():
    print(f"File not found: {target}")
    sys.exit(1)

# Add shellpilot to path
sys.path.insert(0, str(target.parent.parent / "shellpilot"))

from player import load_lesson, Say

demo_obj = load_lesson(target)

# Collect Say texts
texts = []
for step in demo_obj.setup + demo_obj.steps + demo_obj.teardown:
    if isinstance(step, Say):
        texts.append(step.text)

print(f"Found {len(texts)} TTS clips in {target.name}")

from tts import TextToSpeech, get_cache_path

tts = TextToSpeech(voice=demo_obj.tts_voice, enabled=True)
uncached = [t for t in texts if not get_cache_path(t, tts.voice, tts.model).exists()]

if not uncached:
    print("All clips already cached!")
    sys.exit(0)

print(f"Need to generate {len(uncached)} clips...")
for i, text in enumerate(uncached, 1):
    print(f"  [{i}/{len(uncached)}] {text[:60]}...")
    for attempt in range(5):
        try:
            from tts import generate_speech
            generate_speech(text=text, voice=tts.voice, model=tts.model, api_key=tts.api_key)
            print(f"    OK")
            break
        except KeyboardInterrupt:
            print("\nAborted by user")
            sys.exit(1)
        except Exception as e:
            if attempt < 4:
                import time
                print(f"    Retry {attempt+1}: {e}")
                time.sleep(3)
            else:
                print(f"    FAILED: {e}")

# Final check
still_missing = [t for t in texts if not get_cache_path(t, tts.voice, tts.model).exists()]
if still_missing:
    print(f"\n{len(still_missing)} clips still missing")
else:
    print(f"\nAll {len(texts)} clips cached successfully!")
