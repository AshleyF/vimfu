"""Deep audit: For every script 246+ that uses NG jump, verify the target line
actually contains what the narration claims it does, by checking the writeFile content."""
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
    
    with open(f, 'r', encoding='utf-8') as jf:
        script = json.load(jf)
    
    # Extract the writeFile content to know what's on each line
    file_lines = {}  # filename -> list of lines (1-indexed)
    for step in script.get('setup', []):
        if isinstance(step, dict) and 'writeFile' in step:
            content = step['content']
            lines = content.split('\n')
            file_lines[step['writeFile']] = {i+1: l for i, l in enumerate(lines)}
    
    if not file_lines:
        continue
    
    # Get all the lines (use first file)
    first_file = list(file_lines.values())[0]
    
    # Now check each step: find SAY + KEYS pairs where SAY mentions a name and KEYS has NG
    steps = script.get('steps', [])
    for si, step in enumerate(steps):
        if not isinstance(step, dict):
            continue
        
        # Check for SAY that mentions a class/method/function name with a line number
        say_text = step.get('say', '')
        if not say_text:
            continue
        
        # Pattern: "line N, the X class/method/function" or "line N. The X"
        for m in re.finditer(
            r'line\s+([\w\s-]+?)\s*[,.]?\s*(?:the|where)\s+(\w+)\s*(class|method|function|variable|constant|is)',
            say_text, re.IGNORECASE
        ):
            ref = m.group(1).strip().rstrip(',.')
            claimed_name = m.group(2).lower()
            spoken_num = parse_spoken_number(ref)
            if not spoken_num:
                continue
            
            # Check what's actually on that line
            if spoken_num in first_file:
                actual = first_file[spoken_num]
                if claimed_name not in actual.lower():
                    issues.append(f'{base}: SAY mentions "line {spoken_num}, the {claimed_name}" but line {spoken_num} is: "{actual.strip()}"')
                    # Find correct line
                    for ln, txt in sorted(first_file.items()):
                        if claimed_name in txt.lower():
                            issues[-1] += f'  (found "{claimed_name}" on line {ln}: "{txt.strip()}")'
                            break
        
        # Also check: KEYS has NG, find nearby SAY that names something
        keys_text = step.get('keys', '')
        gm = re.match(r'(\d+)G', keys_text)
        if gm:
            target = int(gm.group(1))
            if target in first_file:
                actual_line = first_file[target].strip()
                
                # Look backward for the SAY that describes this jump
                for sj in range(si-1, max(si-5, 0), -1):
                    prev = steps[sj]
                    if isinstance(prev, dict) and 'say' in prev:
                        prev_say = prev['say']
                        # Check for class/method/function name claims
                        for nm in re.finditer(r'\bthe\s+(\w+)\s+(class|method|function)\b', prev_say, re.IGNORECASE):
                            claimed = nm.group(1).lower()
                            if claimed in ('first', 'last', 'next', 'same', 'other', 'entire', 'new', 'inner', 'outer', 'this', 'that'):
                                continue
                            if claimed not in actual_line.lower():
                                msg = f'{base}: Jump {target}G lands on "{actual_line}" but SAY claims "{claimed} {nm.group(2)}"'
                                for ln, txt in sorted(first_file.items()):
                                    if claimed in txt.lower():
                                        msg += f'  (should be {ln}G: "{txt.strip()}")'
                                        break
                                issues.append(msg)
                        break

    # ---- Also check the log for cursor position vs screen content ----
    log_path = f'videos/{base}/{base}.log'
    if not os.path.exists(log_path):
        continue
    
    with open(log_path, 'r', encoding='utf-8', errors='replace') as lf:
        log_lines = lf.readlines()
    
    # Check for KEYS NG where cursor lands on unexpected line  
    for i, line in enumerate(log_lines):
        line = line.rstrip()
        km = re.match(r"\[KEYS\]\s*'(\d+)G(.*)'", line)
        if not km:
            continue
        target = int(km.group(1))
        
        # Find next cursor line
        for j in range(i+1, min(i+15, len(log_lines))):
            cm = re.search(r'cursor \((\d+),(\d+)\)', log_lines[j])
            if cm:
                lm = re.search(r'\|\s*(\d+)\s+', log_lines[j])
                if lm:
                    actual = int(lm.group(1))
                    if actual != target:
                        issues.append(f'{base}: [LOG] KEYS "{target}G" but cursor landed on line {actual}')
                break

# Deduplicate
seen = set()
unique = []
for iss in issues:
    if iss not in seen:
        seen.add(iss)
        unique.append(iss)

print(f'Deep audit of 246+ scripts')
print(f'Found {len(unique)} issues:')
print()
for iss in unique:
    print(f'  {iss}')
    print()
