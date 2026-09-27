"""Fills a translation with the Japanese text of your own template, to translate.

    python3 tools/add_source.py zoids-saga.pot po/es.po > es-work.po

Every message of the template (exported from your own ROM with the launcher)
comes out in the template's order, its `msgid` the Japanese text and its
`msgstr` the translation's, empty where there is none yet. Messages of the
translation the template lacks follow at the end. Edit `es-work.po` with any PO
editor, then run `strip_source.py` before committing.
"""

import sys

import po


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    template, translation = po.read(sys.argv[1]), po.read(sys.argv[2])
    header = [e for e in translation if e.msgctxt is None and e.msgid == ""]
    ours = {e.msgctxt: e for e in translation if e.msgctxt is not None}
    out = list(header)
    for source in template:
        if source.msgctxt is None:
            continue
        mine = ours.pop(source.msgctxt, None)
        comments = [c for c in source.comments if c.startswith("#.")]
        if mine is not None:
            comments += [c for c in mine.comments if not c.startswith("#.")]
        out.append(po.Entry(comments, source.msgctxt, source.msgid, mine.msgstr if mine else ""))
    out.extend(ours.values())
    po.write(out)


if __name__ == "__main__":
    main()
