import unicodedata
from collections import Counter
from pypdf import PdfReader

r = PdfReader(r'c:\source\vimfu\content\output\latex\book.pdf')

SUSPECT = set(range(0x200B, 0x2010)) | {
    0xFEFF, 0x00AD, 0x00A0,
    0x2028, 0x2029, 0x202A, 0x202B, 0x202C, 0x202D, 0x202E,
    0x2060, 0x2061, 0x2062, 0x2063, 0x2064,
}
hits = []
for pi, p in enumerate(r.pages):
    try:
        text = p.extract_text() or ''
    except Exception:
        continue
    for col, ch in enumerate(text):
        cp = ord(ch)
        flag = None
        if cp < 0x20 and ch not in '\t\n\r':
            flag = 'C0 control'
        elif cp in SUSPECT:
            flag = unicodedata.name(ch, '?')
        elif 0xE000 <= cp <= 0xF8FF:
            flag = 'PUA'
        elif cp == 0xFFFD:
            flag = 'REPLACEMENT CHARACTER'
        if flag:
            ctx = text[max(0, col-25):col+25]
            hits.append((pi+1, col, cp, flag, ctx))

print(f'Total suspect chars: {len(hits)}')
c = Counter(h[2] for h in hits)
for cp, n in c.most_common():
    name = unicodedata.name(chr(cp), '?')
    print(f'  U+{cp:04X}  count={n:5d}   {name}')

print()
print('=== NUL (U+0000) occurrences ===')
for pg, col, cp, flag, ctx in hits:
    if cp == 0:
        safe = ''.join(
            ch if ch.isprintable() and ord(ch) < 0x10000 and ord(ch) >= 0x20
            else f'<U+{ord(ch):04X}>'
            for ch in ctx
        )
        print(f'  p{pg}  col={col}  ...{safe}...')
