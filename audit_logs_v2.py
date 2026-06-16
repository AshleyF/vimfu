"""Expanded audit: check all logs 246+ for narration vs screen mismatches."""
import os, re, json, glob

word_to_num = {
    'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
    'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
    'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14,
    'fifteen': 15, 'sixteen': 16, 'seventeen': 17, 'eighteen': 18,
    'nineteen': 19, 'twenty': 20, 'thirty': 30, 'forty': 40,
    'fifty': 50, 'sixty': 60, 'seventy': 70, 'eighty': 80, 'ninety': 90,
}

def parse_spoken_number(text):
    parts = text.lower().replace('-', ' ').split()
    total = 0
    for p in parts:
        if p in word_to_num:
            total += word_to_num[p]
        elif p.isdigit():
            total = int(p)
        else:
            return None
    return total if total > 0 else None

issues = []

for f in sorted(glob.glob('curriculum/shorts/*.json')):
    base = os.path.splitext(os.path.basename(f))[0]
    num_match = re.match(r'^(\d+)', base.split('_')[0])
    if not num_match:
        continue
    num = int(num_match.group(1))
    if num < 246:
        continue
    
    log_path = f'videos/{base}/{base}.log'
    if not os.path.exists(log_path):
        continue
    
    with open(log_path, 'r', encoding='utf-8', errors='replace') as lf:
        log_content = lf.read()
        log_lines = log_content.split('\n')
    
    # Load the JSON to cross-reference
    with open(f, 'r', encoding='utf-8') as jf:
        script = json.load(jf)
    
    # Build a map of all screen snapshots with cursor positions
    # Format: row | linenum text | cursor (r,c)
    screens = []  # list of (line_idx, nvim_line, cursor_row, cursor_col, line_text)
    for i, line in enumerate(log_lines):
        cm = re.search(r'cursor \((\d+),(\d+)\)', line)
        if cm:
            lm = re.search(r'\|\s*(\d+)\s+(.+?)\s*\|.*cursor', line)
            if lm:
                screens.append({
                    'log_idx': i,
                    'nvim_line': int(lm.group(1)),
                    'text': lm.group(2).strip(),
                    'row': int(cm.group(1)),
                    'col': int(cm.group(2)),
                })

    # Build list of SAY + KEYS sequences
    events = []
    for i, line in enumerate(log_lines):
        line = line.rstrip()
        if line.startswith('[SAY]'):
            events.append({'type': 'SAY', 'text': line[5:].strip(), 'idx': i})
        elif line.startswith('[KEYS]'):
            km = re.match(r"\[KEYS\]\s*'(.+)'", line)
            if km:
                events.append({'type': 'KEYS', 'text': km.group(1), 'idx': i})
        elif line.startswith('[CTRL]'):
            cm = re.match(r"\[CTRL\]\s*(\S+)", line)
            if cm:
                events.append({'type': 'CTRL', 'text': cm.group(1), 'idx': i})

    # ---- Check 1: SAY mentions "line N" then KEYS has "MG" where M != N ----
    for ei, ev in enumerate(events):
        if ev['type'] != 'SAY':
            continue
        say = ev['text']
        
        # Find spoken line number references
        for m in re.finditer(r'\bline\s+([\w\s-]+?)(?:\.|,|;|\s+(?:the|and|is|near|at|to|of|end|it|has|move|now)\b)', say, re.IGNORECASE):
            ref = m.group(1).strip()
            spoken_num = parse_spoken_number(ref)
            if not spoken_num:
                continue
            
            # Look for the next KEYS event that has a G command
            for ej in range(ei+1, min(ei+5, len(events))):
                if events[ej]['type'] == 'KEYS':
                    keys_text = events[ej]['text']
                    gm = re.match(r'(\d+)G', keys_text)
                    if gm:
                        keys_line = int(gm.group(1))
                        if keys_line != spoken_num:
                            issues.append(f'[LINE_VS_KEYS] {base}: SAY "line {spoken_num}" but KEYS "{keys_line}G"  |  {say[:80]}')
                    break
    
    # ---- Check 2: SAY mentions function/class/method name, cursor not on it ----
    for ei, ev in enumerate(events):
        if ev['type'] != 'SAY':
            continue
        say = ev['text']
        
        # "the Foo class" / "the bar method" / "the baz function"
        for m in re.finditer(r'\bthe\s+(\w+)\s+(class|method|function)\b', say, re.IGNORECASE):
            claimed = m.group(1).lower()
            if claimed in ('first', 'last', 'next', 'same', 'other', 'entire', 'new', 'this', 'that', 'each', 'whole', 'inner', 'outer'):
                continue
            
            # Find the next cursor position after this SAY
            for s in screens:
                if s['log_idx'] > ev['idx']:
                    if claimed not in s['text'].lower():
                        issues.append(f'[NAME_MISMATCH] {base}: SAY "the {claimed}" but cursor on "{s["text"][:40]}"  |  {say[:80]}')
                    break
    
    # ---- Check 3: KEYS "NG" but cursor lands on unexpected line ----
    for ei, ev in enumerate(events):
        if ev['type'] != 'KEYS':
            continue
        gm = re.match(r'(\d+)G(.*)', ev['text'])
        if not gm:
            continue
        target_line = int(gm.group(1))
        
        # Find next cursor position
        for s in screens:
            if s['log_idx'] > ev['idx']:
                if s['nvim_line'] != target_line:
                    issues.append(f'[KEYS_LANDING] {base}: KEYS "{ev["text"]}" expected line {target_line}, cursor on line {s["nvim_line"]}: "{s["text"][:40]}"')
                break
    
    # ---- Check 4: SAY describes cursor position but screen doesn't match ----
    for ei, ev in enumerate(events):
        if ev['type'] != 'SAY':
            continue
        say = ev['text'].lower()
        
        # "cursor is on line N" or "you're on line N"
        for m in re.finditer(r"(?:cursor|you.re|we.re)\s+(?:is\s+)?on\s+line\s+([\w\s-]+?)(?:\.|,|;|\s)", say):
            ref = m.group(1).strip()
            spoken_num = parse_spoken_number(ref)
            if not spoken_num:
                continue
            
            # Find most recent cursor position
            for s in reversed(screens):
                if s['log_idx'] < ev['idx']:
                    if s['nvim_line'] != spoken_num:
                        issues.append(f'[POSITION_CLAIM] {base}: SAY "on line {spoken_num}" but cursor on line {s["nvim_line"]}: "{s["text"][:40]}"  |  {ev["text"][:80]}')
                    break

    # ---- Check 5: WaitForScreen timeout in log ----
    if '[WAIT] TIMEOUT' in log_content:
        issues.append(f'[TIMEOUT] {base}: WaitForScreen timed out during recording')

    # ---- Check 6: Very few screen snapshots (possible failed recording) ----
    if len(screens) < 2 and '[VIDEO] Recording saved' in log_content:
        issues.append(f'[FEW_SCREENS] {base}: Only {len(screens)} screen snapshots captured')


# Deduplicate
seen = set()
unique = []
for iss in issues:
    if iss not in seen:
        seen.add(iss)
        unique.append(iss)

print(f'Scanned all logs from 0246+')
print(f'Found {len(unique)} potential issues:')
print()
for iss in unique:
    print(f'  {iss}')
    print()
