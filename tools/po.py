"""Reads and writes the PO files of Re:Zoids Saga.

Every message is keyed by its `msgctxt` (`table/index/offset`, e.g.
`dialogue/397/0x58`). The game reads only `msgctxt` and `msgstr`; in this
repository `msgid` holds the key again, so no text from the ROM is published.
"""

import sys
from dataclasses import dataclass, field

FIELDS = ("msgctxt", "msgid", "msgstr")


@dataclass
class Entry:
    """One PO entry: its comment lines and its three fields."""

    comments: list = field(default_factory=list)
    msgctxt: str = None
    msgid: str = ""
    msgstr: str = ""


def unquote(text, where):
    """The value of a quoted PO string, escapes resolved."""
    if len(text) < 2 or not text.startswith('"') or not text.endswith('"'):
        raise ValueError(f"{where}: expected a quoted string")
    out = []
    body = text[1:-1]
    i = 0
    while i < len(body):
        c = body[i]
        if c == "\\" and i + 1 < len(body):
            n = body[i + 1]
            out.append({"n": "\n", "t": "\t", '"': '"', "\\": "\\"}.get(n, "\\" + n))
            i += 2
            continue
        out.append(c)
        i += 1
    return "".join(out)


def quote(text):
    """A PO quoted string for `text`, on one line."""
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\t", "\\t") + '"'


def read(path):
    """The entries of a PO file, the header (empty `msgid`, no context) first."""
    entries = []
    entry = Entry()
    last = None
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    for number, raw in enumerate(lines, 1):
        line = raw.strip()
        where = f"{path}:{number}"
        if not line:
            if last or entry.comments:
                entries.append(entry)
            entry, last = Entry(), None
            continue
        if line.startswith("#"):
            if last:
                entries.append(entry)
                entry, last = Entry(), None
            entry.comments.append(line)
            continue
        name, _, rest = line.partition(" ")
        if name in FIELDS:
            if name == "msgctxt" and last:
                entries.append(entry)
                entry = Entry()
            setattr(entry, name, unquote(rest, where))
            last = name
        elif line.startswith('"') and last:
            setattr(entry, last, getattr(entry, last) + unquote(line, where))
        else:
            raise ValueError(f"{where}: cannot read {raw!r}")
    if last or entry.comments:
        entries.append(entry)
    return entries


def write(entries, out=sys.stdout):
    """Writes `entries` as a PO file."""
    blocks = []
    for e in entries:
        lines = list(e.comments)
        if e.msgctxt is not None:
            lines.append("msgctxt " + quote(e.msgctxt))
        if e.msgctxt is None and e.msgid == "":
            lines.append('msgid ""')
            lines.append('msgstr ""')
            lines.extend(quote(part + "\n") for part in e.msgstr.split("\n") if part)
        else:
            lines.append("msgid " + quote(e.msgid))
            lines.append("msgstr " + quote(e.msgstr))
        blocks.append("\n".join(lines))
    out.write("\n\n".join(blocks) + "\n")


def key_id(key, text):
    """The `msgid` a message keeps here: its key, with the translation's
    leading and trailing new lines, which gettext tools require to match."""
    lead = "\n" if text.startswith("\n") else ""
    trail = "\n" if text.endswith("\n") else ""
    return lead + key + trail
