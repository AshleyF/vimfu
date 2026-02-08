"""Pre-cache TTS audio clips for a lesson script.

Usage: python3.13 precache_tts.py curriculum/0002_opening_a_file.py

Runs the TTS generation in isolation, retrying failed clips.
Once cached, the lesson script will start instantly.
"""

import sys
import importlib.util
from pathlib import Path

if len(sys.argv) < 2:
    print("Usage: python precache_tts.py <lesson_script.py>")
    sys.exit(1)

script = Path(sys.argv[1]).resolve()
if not script.exists():
    print(f"File not found: {script}")
    sys.exit(1)

# Add shellpilot to path
sys.path.insert(0, str(script.parent.parent / "shellpilot"))
sys.path.insert(0, str(script.parent))

# Load the module to get the Demo object
spec = importlib.util.spec_from_file_location("lesson", script)
mod = importlib.util.module_from_spec(spec)
# Prevent the lesson from auto-running
sys.argv = [str(script)]  # Reset argv so Demo.run() path derivation works

# We need to extract the Demo without running it
# Import the module source and find the Demo
import ast
source = script.read_text()
tree = ast.parse(source)

# Quick approach: just import the module but monkey-patch Demo.run
from dsl import Demo, Say
_original_run = Demo.run
Demo.run = lambda self, **kw: None  # no-op
spec.loader.exec_module(mod)
Demo.run = _original_run

# Find the Demo instance
demo_obj = None
for name in dir(mod):
    obj = getattr(mod, name)
    if isinstance(obj, Demo):
        demo_obj = obj
        break

if not demo_obj:
    print("No Demo instance found in script")
    sys.exit(1)

# Collect Say texts
texts = []
for step in demo_obj.setup + demo_obj.steps + demo_obj.teardown:
    if isinstance(step, Say):
        texts.append(step.text)

print(f"Found {len(texts)} TTS clips in {script.name}")

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
