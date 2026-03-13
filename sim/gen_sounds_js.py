"""Generate key_sounds.js with base64-embedded MP3 click sounds."""
import base64, os

sounds_dir = r'c:\source\vimfu\shellpilot\sounds'
out = {}
for f in sorted(os.listdir(sounds_dir)):
    if not f.endswith('.mp3'):
        continue
    name = f[:-4]  # strip .mp3
    path = os.path.join(sounds_dir, f)
    with open(path, 'rb') as fp:
        b64 = base64.b64encode(fp.read()).decode('ascii')
    out[name] = b64
    print(f'{name}: {len(b64)} chars')

# Write JS module
lines = [
    '// Auto-generated key click sounds (base64-encoded MP3)',
    '// Source: shellpilot/sounds/ — recorded by Glarses',
    '// https://www.youtube.com/watch?v=P_9vXJZVT54',
    '//',
    '// To regenerate: python gen_sounds_js.py',
    '',
    'const SOUND_DATA = {',
]
for name, b64 in out.items():
    safe_name = name.replace(' ', '_')
    lines.append(f'  {safe_name}: "{b64}",')
lines.append('};')
lines.append('')
lines.append('export { SOUND_DATA };')

with open(r'c:\source\vimfu\sim\src\key_sounds.js', 'w', encoding='utf-8') as fp:
    fp.write('\n'.join(lines) + '\n')

total_b64 = sum(len(v) for v in out.values())
print(f'---')
print(f'Wrote src/key_sounds.js: {len(out)} sounds, {total_b64} base64 chars ({total_b64/1024:.0f} KB)')
