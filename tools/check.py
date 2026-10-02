"""Checks the translations before they are merged.

    python3 tools/check.py po/*.po

Errors (the check fails):
- po/languages.json, the list the game's launcher downloads from, that
  cannot be read, lists a language twice, names one with a code other than
  letters, digits, `-` and `_` or a file other than po/<code>.po, or leaves
  out a PO file of po/;
- a file that cannot be read, or has no header;
- a message without a key, a key in an unknown form, or a key twice;
- a `msgid` that is not the message's key (the ROM's text must not be published),
  with the translation's leading and trailing new lines;
- Japanese text in a `msgid` or a comment;
- an empty translation.

Warnings (printed, the check passes):
- a `{...}` that is not one of the markers the game knows, which prints as written;
- Japanese kana or kanji left in a translation.
"""

import json
import re
import sys
from pathlib import Path

import po

KEY = re.compile(
    r"^[a-z-]+/\d+/0x[0-9a-f]+$"
    r"|^name-entry/(help|alphabet/\d+)$"
    r"|^port/[a-z0-9-]+(/[a-z0-9-]+)*$"
)
MARKER = re.compile(r"\{(name|var\d+:\d+|window:\d+|level|area|money|slot|button|count|total|page|pages|hours|minutes)\}")
BRACES = re.compile(r"\{[^{}]*\}")
JAPANESE = re.compile("[\u3040-\u30ff\u3400-\u9fff\uff01-\uff5e\uff61-\uff9f]")
CODE = re.compile(r"^[A-Za-z0-9_-]+$")
ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "po" / "languages.json"


def check_index():
    """The errors of po/languages.json against the PO files of po/."""
    try:
        languages = json.loads(INDEX.read_text(encoding="utf-8"))["languages"]
    except (OSError, ValueError, KeyError, TypeError) as error:
        return [f"{INDEX.name}: cannot be read ({error})"]
    errors, codes = [], set()
    for number, language in enumerate(languages):
        where = f"{INDEX.name}: language {number}"
        if not isinstance(language, dict):
            errors.append(f"{where} is not an object")
            continue
        code, name, file = (language.get(field) for field in ("code", "name", "file"))
        if not isinstance(code, str) or not CODE.match(code):
            errors.append(f"{where}: code {code!r} is not letters, digits, - and _")
            continue
        if code in codes:
            errors.append(f"{where}: {code} listed twice")
        codes.add(code)
        if not isinstance(name, str) or not name.strip():
            errors.append(f"{where}: {code} has no name")
        if file != f"po/{code}.po" or not (ROOT / file).is_file():
            errors.append(f"{where}: {code} names {file!r}, not the existing po/{code}.po")
    for path in sorted((ROOT / "po").glob("*.po")):
        if path.stem not in codes:
            errors.append(f"{INDEX.name}: po/{path.name} is not listed")
    return errors


def check(path):
    errors, warnings = [], []
    try:
        entries = po.read(path)
    except (OSError, ValueError) as error:
        return [str(error)], []
    if not any(e.msgctxt is None and e.msgid == "" for e in entries):
        errors.append(f"{path}: no header")
    seen = set()
    for e in entries:
        if e.msgctxt is None:
            if e.msgid != "":
                errors.append(f"{path}: a message without a key ({e.msgid[:30]!r})")
            continue
        key = e.msgctxt
        where = f"{path}: {key}"
        if not KEY.match(key):
            errors.append(f"{where}: unknown key form")
        if key in seen:
            errors.append(f"{where}: key given twice")
        seen.add(key)
        if e.msgid != po.key_id(key, e.msgstr):
            errors.append(f"{where}: msgid must be the key (run tools/strip_source.py)")
        if JAPANESE.search(e.msgid) or any(JAPANESE.search(c) for c in e.comments):
            errors.append(f"{where}: Japanese text in msgid or comments")
        if not e.msgstr:
            errors.append(f"{where}: empty translation")
        for braces in BRACES.findall(e.msgstr):
            if not MARKER.fullmatch(braces):
                warnings.append(f"{where}: {braces} is not a marker and prints as written")
        if JAPANESE.search(e.msgstr) and not key.startswith("name-entry/"):
            warnings.append(f"{where}: Japanese left in the translation")
    return errors, warnings


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    index_errors = check_index()
    for line in index_errors:
        print("error:", line)
    failed = bool(index_errors)
    for path in sys.argv[1:]:
        errors, warnings = check(path)
        for line in warnings:
            print("warning:", line)
        for line in errors:
            print("error:", line)
        failed |= bool(errors)
        print(f"{path}: {len(errors)} errors, {len(warnings)} warnings")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
