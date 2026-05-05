"""Audit all video logs from 0246+ for narration/screen mismatches."""
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
    """Convert spoken number like 'twenty three' to 23."""
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
    
    log_path = f'shellpilot/videos/{base}/{base}.log'
    if not os.path.exists(log_path):
        continue
    
    with open(log_path, 'r', encoding='utf-8', errors='replace') as lf:
        log_lines = lf.readlines()
    
    # ---- Check 1: Line number claims vs actual cursor position ----
    for i, line in enumerate(log_lines):
        line = line.rstrip()
        if not line.startswith('[SAY]'):
            continue
        say_text = line[5:].strip()
        
        # Find "line <number>" references
        for m in re.finditer(r'\bline\s+([\w\s-]+?)(?:\.|,|;|\b(?:the|and|is|near|at|to|of|end|it|has)\b)', say_text, re.IGNORECASE):
            ref = m.group(1).strip()
            spoken_num = parse_spoken_number(ref)
            if not spoken_num:
                continue
            
            # Look ahead for the next cursor position after this SAY
            for j in range(i+1, min(i+20, len(log_lines))):
                next_line = log_lines[j].rstrip()
                cursor_match = re.search(r'cursor \((\d+),(\d+)\)', next_line)
                if cursor_match:
                    ln_match = re.search(r'\|\s*(\d+)\s+(.+?)\s*\|.*cursor', next_line)
                    if ln_match:
                        actual_line = int(ln_match.group(1))
                        actual_text = ln_match.group(2).strip()
                        if actual_line != spoken_num:
                            issues.append({
                                'file': base,
                                'type': 'LINE_MISMATCH',
                                'say': say_text,
                                'spoken_line': spoken_num,
                                'actual_line': actual_line,
                                'actual_text': actual_text,
                            })
                    break
    
    # ---- Check 2: Claims about what function/class cursor is on ----
    for i, line in enumerate(log_lines):
        line = line.rstrip()
        if not line.startswith('[SAY]'):
            continue
        say_text = line[5:].strip()
        
        # Look for patterns like "the X function" or "the X class" or "the X method"
        for m in re.finditer(r'\bthe\s+(\w+)\s+(function|class|method|def)\b', say_text, re.IGNORECASE):
            claimed_name = m.group(1).lower()
            kind = m.group(2).lower()
            
            # Look ahead for the next cursor position
            for j in range(i+1, min(i+20, len(log_lines))):
                next_line = log_lines[j].rstrip()
                cursor_match = re.search(r'cursor \((\d+),(\d+)\)', next_line)
                if cursor_match:
                    ln_match = re.search(r'\|\s*(\d+)\s+(.+?)\s*\|.*cursor', next_line)
                    if ln_match:
                        actual_text = ln_match.group(2).strip()
                        # Check if the claimed name appears on the cursor line
                        if claimed_name not in actual_text.lower():
                            issues.append({
                                'file': base,
                                'type': 'NAME_MISMATCH',
                                'say': say_text,
                                'claimed': f'{claimed_name} {kind}',
                                'actual_text': actual_text,
                            })
                    break
        
        # Also check "Jump to ... the X class/method/function"
        for m in re.finditer(r'(?:jump to|go to|move to).*?\bthe\s+(\w+)\s+(class|method|function)\b', say_text, re.IGNORECASE):
            claimed_name = m.group(1).lower()
            kind = m.group(2).lower()
            
            for j in range(i+1, min(i+20, len(log_lines))):
                next_line = log_lines[j].rstrip()
                cursor_match = re.search(r'cursor \((\d+),(\d+)\)', next_line)
                if cursor_match:
                    ln_match = re.search(r'\|\s*(\d+)\s+(.+?)\s*\|.*cursor', next_line)
                    if ln_match:
                        actual_text = ln_match.group(2).strip()
                        if claimed_name not in actual_text.lower():
                            issues.append({
                                'file': base,
                                'type': 'JUMP_NAME_MISMATCH',
                                'say': say_text,
                                'claimed': f'{claimed_name} {kind}',
                                'actual_text': actual_text,
                            })
                    break

    # ---- Check 3: "cursor is on the X" claims ----
    for i, line in enumerate(log_lines):
        line = line.rstrip()
        if not line.startswith('[SAY]'):
            continue
        say_text = line[5:].strip()
        
        for m in re.finditer(r'cursor\s+(?:is\s+)?on\s+(?:the\s+)?(?:letter\s+|word\s+)?(\w+)', say_text, re.IGNORECASE):
            claimed_word = m.group(1).lower()
            if claimed_word in ('the', 'a', 'it', 'line', 'first', 'last', 'top', 'bottom', 'that', 'this'):
                continue
            
            # Find the most recent cursor line (before this SAY, since it describes current state)
            for j in range(i-1, max(i-30, 0), -1):
                prev_line = log_lines[j].rstrip()
                cursor_match = re.search(r'cursor \((\d+),(\d+)\)', prev_line)
                if cursor_match:
                    ln_match = re.search(r'\|\s*(\d+)\s+(.+?)\s*\|.*cursor', prev_line)
                    if ln_match:
                        actual_text = ln_match.group(2).strip()
                        if claimed_word not in actual_text.lower():
                            issues.append({
                                'file': base,
                                'type': 'CURSOR_ON_MISMATCH',
                                'say': say_text,
                                'claimed_word': claimed_word,
                                'actual_text': actual_text,
                            })
                    break

# Deduplicate
seen = set()
unique_issues = []
for iss in issues:
    key = (iss['file'], iss['type'], iss.get('say', '')[:50])
    if key not in seen:
        seen.add(key)
        unique_issues.append(iss)

print(f'Scanned logs from 0246+')
print(f'Found {len(unique_issues)} potential issues:')
print()
for iss in unique_issues:
    print(f'  [{iss["type"]}] {iss["file"]}:')
    print(f'    SAY: {iss["say"][:120]}')
    if iss['type'] == 'LINE_MISMATCH':
        print(f'    Claimed line {iss["spoken_line"]}, actual line {iss["actual_line"]}: {iss["actual_text"]}')
    elif 'claimed' in iss:
        print(f'    Claimed: {iss["claimed"]}, actual: {iss["actual_text"]}')
    elif 'claimed_word' in iss:
        print(f'    Claimed word: {iss["claimed_word"]}, actual line: {iss["actual_text"]}')
    print()
