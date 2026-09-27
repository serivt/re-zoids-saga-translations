"""Removes the Japanese text from a translation before it is committed.

    python3 tools/strip_source.py es-work.po > po/es.po

Every translated message keeps its key, its translation, its notes (`#.`) and
translator comments (`# `) and flags (`#,`); its `msgid` becomes the key again
(with the translation's leading and trailing new lines, as gettext tools want).
Untranslated messages, source references (`#:`) and previous texts (`#|`) are
dropped, so nothing from the ROM is left.
"""

import sys

import po

KEPT = ("#.", "# ", "#,")


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    out = []
    for e in po.read(sys.argv[1]):
        if e.msgctxt is None:
            if e.msgid == "":
                out.append(e)
            continue
        if not e.msgstr:
            continue
        comments = [c for c in e.comments if c.startswith(KEPT) or c == "#"]
        out.append(po.Entry(comments, e.msgctxt, po.key_id(e.msgctxt, e.msgstr), e.msgstr))
    po.write(out)


if __name__ == "__main__":
    main()
