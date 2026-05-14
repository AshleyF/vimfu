"""One-shot rebuild of .bw.pdf siblings for every .bw.svg via svglib.

Used when the system Inkscape is broken (e.g. after a Windows update).
Each conversion runs in a subprocess with a short timeout so a single
bad SVG can't stall the whole batch.
"""
import sys
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, TimeoutError as FuturesTimeout

def convert_one(path_str):
    from svglib.svglib import svg2rlg
    from reportlab.graphics import renderPDF
    from pathlib import Path
    s = Path(path_str)
    d = svg2rlg(str(s))
    if d is None:
        return (path_str, False, 'drawing None')
    renderPDF.drawToFile(d, str(s.with_suffix('.pdf')))
    return (path_str, True, '')


def main():
    ROOT = Path(r'c:\source\vimfu\content\output\html\screenshots')
    svgs = sorted(ROOT.rglob('*.bw.svg'))
    todo = [s for s in svgs if not s.with_suffix('.pdf').exists()
            or s.stat().st_mtime > s.with_suffix('.pdf').stat().st_mtime]
    print(f'{len(todo)} of {len(svgs)} SVGs need conversion', flush=True)
    ok = 0
    failed = []
    with ProcessPoolExecutor(max_workers=4) as ex:
        futures = {ex.submit(convert_one, str(s)): s for s in todo}
        for i, f in enumerate(futures):
            s = futures[f]
            try:
                _, success, err = f.result(timeout=15)
                if success:
                    ok += 1
                else:
                    failed.append((s, err))
            except FuturesTimeout:
                failed.append((s, 'timeout'))
                f.cancel()
            except Exception as e:
                failed.append((s, str(e)))
            if (ok + len(failed)) % 25 == 0:
                print(f'  ... {ok + len(failed)}/{len(todo)}  ok={ok} fail={len(failed)}', flush=True)
    print(f'Done. ok={ok} failed={len(failed)}')
    for s, e in failed[:10]:
        print(f'  FAIL {s.name}: {e}')

if __name__ == '__main__':
    main()

