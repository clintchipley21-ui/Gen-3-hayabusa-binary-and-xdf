#!/usr/bin/env python3
"""Replace decompiled function handles (FUN_<addr>) in XDF descriptions with readable names.

Called at the end of make_stock_xdfs.py and make_race_xdf.py (after the patch injector), it rewrites each
"FUN_<addr>" token in the shipped XDF item descriptions to the name in docs/function-names.csv, for the
functions we have identified. Unlisted functions keep their FUN_<addr> handle. The full FUN_/address stays
in docs/xdf-notes.csv for cross-reference. "FUN_ram_<addr>" (full code-snippet form) is left untouched.
"""
import collections
import csv
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV = os.path.join(ROOT, 'docs', 'function-names.csv')
TOKEN = re.compile(r'(?<![A-Za-z0-9_])FUN_([0-9A-Fa-f]+)(?![0-9A-Fa-f])')


def load():
    names = {}
    with open(CSV, encoding='utf-8') as f:
        for row in csv.reader(f):
            if not row or row[0].startswith('#') or row[0] == 'address':
                continue
            names[int(row[0], 16)] = row[1]
    return names


def _norm(s):
    return re.sub(r'[-_]', ' ', s).lower()


def _clean(body):
    """Tidy artifacts left when a handle is dropped or replaced."""
    body = re.sub(r'(\b(?:from|by|in|via|and)\s+)-\s*', r'\1', body)   # "from -FUN" / "by -"
    body = re.sub(r'\s+-\s*(?=FUN_)', ' ', body)                        # "module -FUN_x" range leftover
    body = re.sub(r'\(\s*[,;]?\s*\)', '', body)                         # "()" / "( )"
    body = re.sub(r'\(\s+', '(', body)
    body = re.sub(r'\s+::\s*', ' :: ', body)                            # tidy "X ::  y"
    body = re.sub(r'[ \t]{2,}', ' ', body)                             # double spaces
    body = re.sub(r'\s+([.;,)])', r'\1', body)                          # space before punctuation
    return body.strip()


def rename(text, names=None):
    """Replace a known FUN_<addr> with its name in item <title> and <description> - but if the name's lead
    word is already next to the handle (the text or the category prefix already says what it is, e.g.
    'Per-gear RPM limiter FUN_2C068' or 'Launch Control :: FUN_289C4 ...'), drop the handle instead of
    duplicating. Unknown handles are left as-is. Hyphens/underscores are ignored when checking for a duplicate."""
    names = load() if names is None else names

    def process(body):
        def sub(t):
            name = names.get(int(t.group(1), 16))
            if not name:
                return t.group(0)
            win = _norm(body[max(0, t.start() - 45):t.start()] + body[t.end():t.end() + 45])
            head = _norm(name.split()[0].strip('(/'))
            return '' if head and head in win else name
        return _clean(TOKEN.sub(sub, body))

    for tag in ('description', 'title'):
        text = re.sub(r'<%s>(.*?)</%s>' % (tag, tag),
                      lambda m: '<%s>%s</%s>' % (tag, process(m.group(1)), tag), text, flags=re.S)
    return text


def count_known(text, names=None):
    names = load() if names is None else names
    return sum(1 for m in TOKEN.finditer(text) if int(m.group(1), 16) in names)


RAM_TOKEN = re.compile(r'(?<![A-Za-z0-9_])FUN_ram_0*([0-9A-Fa-f]+)\b')


def main():
    """Write docs/function-registry.csv: every function referenced in docs/xdf-notes.csv (the full notes),
    with its readable name (or 'unidentified') and how often it is referenced. names come from
    function-names.csv; run tools/xdf_userfriendly.py first so the notes are current."""
    names = load()
    notes = open(os.path.join(ROOT, 'docs', 'xdf-notes.csv'), encoding='utf-8').read()
    cnt = collections.Counter()
    for m in TOKEN.finditer(notes):
        cnt[int(m.group(1), 16)] += 1
    for m in RAM_TOKEN.finditer(notes):          # the FUN_ram_<addr> form used inside code snippets
        cnt[int(m.group(1), 16)] += 1
    rows = sorted(set(cnt) | set(names))
    out = os.path.join(ROOT, 'docs', 'function-registry.csv')
    with open(out, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(('address', 'name', 'references_in_notes'))
        for a in rows:
            w.writerow(('0x%X' % a, names.get(a, 'unidentified'), cnt.get(a, 0)))
    print('%s: %d functions referenced, %d named' % (os.path.relpath(out, ROOT), len(rows), len(names)))


if __name__ == '__main__':
    main()
