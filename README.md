# Re:Zoids Saga translations

Translations for [Re:Zoids Saga](https://github.com/serivt/re-zoids-saga), the
open-source port of *Zoids Saga* (Game Boy Advance, Japan, Rev 1). The game, its engine
and its documentation live in that repository; this one only holds the translation
files, so anyone can read them and suggest corrections.

| Language | File | State |
|---|---|---|
| Spanish (Spain) | [`po/es.po`](po/es.po) | Chapters 1–6 of the story, menus, guides and battles |
| English (US) | [`po/en.po`](po/en.po) | Translated from the Spanish, same coverage; review welcome |

## No Japanese text here

The Japanese script belongs to the original game and is copyrighted, so nothing taken
from the ROM is published. Each file holds, for every message, its **key** and its
**translation** only:

```po
msgctxt "dialogue/397/0x58"
msgid "dialogue/397/0x58"
msgstr "Blood\n¡Sí, señor! Los datos\nreunidos ya deberían\nobrar en su poder."
```

The game reads `msgctxt` and `msgstr`; `msgid` repeats the key where a normal PO file
would carry the source text. To see the Japanese next to each line, generate it from
your own copy of the ROM (see [Translating with your ROM](#translating-with-your-rom)).

## How localization works

- **Keys.** Every message is found by its script table, string index and offset in the
  string: `dialogue/397/0x58` is the message at offset `0x58` of dialogue string 397.
  A string can hold several messages (one per text box). The tables are `title`,
  `name-entry`, `pause-menu`, `dialogue`, `battle`, `battle-text`, `battle-menu`,
  `battle-label`, `item`, `name`, `part`, `system`, `zoid-guide` and
  `character-guide`, plus `port/...` for the port's own messages (save slots, the end
  of the demo, the launcher's screens).
- **Partial files work.** Messages a file lacks stay in Japanese, so a translation can
  grow chapter by chapter.
- **Markers.** Keep them exactly as they are:

  | Marker | Meaning |
  |---|---|
  | `\n` | New line |
  | `{name}` | The player's name (up to 8 letters) |
  | `{varN:D}` | A number the script prints in D cells |
  | `{window:N}` | The text continues in window N |
  | `{level}`, `{area}`, `{money}`, `{slot}`, `{count}`, `{button}` | Values in the port's own messages |

  Any other `{...}` is printed as written.
- **Room.** Latin text uses the port's own proportional font. A story box line holds
  168 pixels beside a portrait (about 25–29 letters) or 224 without one; a box shows
  three lines and turns pages by itself, keeping the speaker's name. The speaker is
  the first line of the message. Menus and lists have their own widths; the launcher
  reports a translated message that cannot fit even a screen-wide window.

The full reference is the main repository's
[docs/translation.md](https://github.com/serivt/re-zoids-saga/blob/main/docs/translation.md).

## Playing with a translation

Download the game from the main repository's
[Releases](https://github.com/serivt/re-zoids-saga/releases) (or build it, see its
README), start it, choose your ROM and pick a `.po` file from this repository as the
translation. From the command line:

```bash
re-zoids-saga path/to/rom.gba --translation po/es.po
```

## Suggesting a correction

No tools needed:

- **Open an issue** with the *Translation correction* form: the current text, your
  wording and where it appears (a screenshot helps).
- **Or edit the file on GitHub:** open [`po/es.po`](po/es.po), press the pencil, find
  the line (search for its text), change only the `msgstr` and propose the change as a
  pull request.

Keep the markers and the `\n` line breaks, and keep lines short enough for their
window (see *Room* above). Every pull request is checked automatically.

## Translating with your ROM

To translate new messages you need the Japanese text, which you generate from your own
dump of the game (Zoids Saga, Japan, Rev 1).

1. **Export the template.** With the game's executable (`re-zoids-saga` from a release,
   `"Re Zoids Saga.app/Contents/MacOS/re-zoids-saga"` on macOS, or
   `cargo run -p launcher --release --` from the main repository):

   ```bash
   re-zoids-saga path/to/rom.gba --export-template zoids-saga.pot \
     title name-entry pause-menu dialogue battle battle-text battle-menu battle-label \
     item name part system zoid-guide character-guide port
   ```

   Tables can be narrowed to ranges, e.g. `dialogue:30-41`. Without tables the
   template covers the title, the name entry, dialogue 30–41 and the port's messages.
2. **Add the Japanese to the translation** (Python 3, no packages needed):

   ```bash
   python3 tools/add_source.py zoids-saga.pot po/es.po > es-work.po
   ```

   `es-work.po` has every message of the template, the Japanese as `msgid` and the
   translation so far as `msgstr`. Edit it with any PO editor, such as
   [Poedit](https://poedit.net/). A few existing translations start or end with a line
   break the Japanese lacks on purpose; Poedit may warn about them.
3. **Remove the Japanese again** and check the result:

   ```bash
   python3 tools/strip_source.py es-work.po > po/es.po
   python3 tools/check.py po/es.po
   ```

   `strip_source.py` keeps only the translated messages, with their keys, notes and
   translator comments. Commit `po/es.po` and open a pull request. `*.pot` and
   `*-work.po` files are ignored by git: never commit them.

### A new language

Start from an empty file with a header:

```po
msgid ""
msgstr ""
"Content-Type: text/plain; charset=UTF-8\n"
"Language: fr\n"
```

save it as `po/fr.po`, then follow the steps above with it.

## Checks

[`tools/check.py`](tools/check.py) runs on every push and pull request, together with
gettext's `msgfmt --check-format`. It fails on unreadable files, unknown or repeated
keys, a `msgid` other than the key, Japanese text in `msgid` or comments, and empty
translations; it warns about unknown markers and Japanese left in a translation.

## License

To be decided by the maintainer.
