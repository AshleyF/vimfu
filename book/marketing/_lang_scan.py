import json, os, re
from collections import Counter

EX_DIR = r'c:\source\vimfu\content\examples'
lang_hints = Counter()
samples = {}

def classify(text):
    if re.search(r'\bdef \w+\(|^\s*import \w', text, re.M): return 'python'
    if re.search(r'#include\s*<|^\s*int\s+main\b', text, re.M): return 'c'
    if re.search(r'function \w+\(|=>\s*\{|console\.log', text): return 'js'
    if re.search(r'^\s*\{\s*"\w+"\s*:', text, re.M): return 'json'
    if re.search(r'<html|<div|</\w+>', text): return 'html'
    if re.search(r'^#+ \w|^- \w', text, re.M): return 'md'
    return 'prose/other'

for fn in os.listdir(EX_DIR):
    if not fn.endswith('.json'): continue
    with open(os.path.join(EX_DIR, fn), encoding='utf-8') as f:
        ex = json.load(f)
    frames = ex.get('frames') or []
    if not frames: continue
    lines = (frames[0].get('compact') or {}).get('lines') or []
    text = '\n'.join(lines)
    k = classify(text)
    lang_hints[k] += 1
    samples.setdefault(k, fn)

for k, n in lang_hints.most_common():
    print(f'  {k:15} {n:4d}  e.g. {samples[k]}')
print(f'  TOTAL: {sum(lang_hints.values())}')
