"""Compile the project's UTF-8 PO files to GNU MO files using Python alone."""
import ast
import re
import struct
import sys
from pathlib import Path


def parse_po(path):
    messages = {}
    entry = {}
    active = None

    def finish_entry():
        nonlocal entry
        if "msgid" not in entry:
            return
        msgid = entry["msgid"]
        if "msgid_plural" in entry:
            key = msgid + "\0" + entry["msgid_plural"]
            value = entry.get("msgstr[0]", "") + "\0" + entry.get("msgstr[1]", "")
        else:
            key = msgid
            value = entry.get("msgstr", "")
        if key in messages:
            raise ValueError(f"Duplicate translation entry: {key!r} in {path}")
        messages[key] = value
        entry = {}

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            finish_entry()
            active = None
            continue
        if line.startswith("#"):
            continue
        if line.startswith("msgid_plural "):
            active = "msgid_plural"
            entry[active] = ast.literal_eval(line[len(active) + 1 :])
        elif line.startswith("msgid "):
            active = "msgid"
            entry[active] = ast.literal_eval(line[len(active) + 1 :])
        elif line.startswith("msgstr["):
            match = re.match(r"msgstr\[(\d+)\]\s+(.*)", line)
            active = f"msgstr[{match.group(1)}]"
            entry[active] = ast.literal_eval(match.group(2))
        elif line.startswith("msgstr "):
            active = "msgstr"
            entry[active] = ast.literal_eval(line[len("msgstr ") :])
        elif line.startswith('"') and active:
            entry[active] += ast.literal_eval(line)
    finish_entry()
    return messages


def compile_mo(messages, output_path):
    entries = sorted(
        ((key.encode("utf-8"), value.encode("utf-8")) for key, value in messages.items()),
        key=lambda pair: pair[0],
    )
    count = len(entries)
    original_table_offset = 7 * 4
    translated_table_offset = original_table_offset + count * 8
    strings_offset = translated_table_offset + count * 8
    originals = b""
    translations = b""
    original_table = []
    translated_table = []

    for original, _ in entries:
        original_table.append((len(original), strings_offset + len(originals)))
        originals += original + b"\0"
    for _, translated in entries:
        translated_table.append((len(translated), strings_offset + len(originals) + len(translations)))
        translations += translated + b"\0"

    header = struct.pack(
        "<7I",
        0x950412DE,
        0,
        count,
        original_table_offset,
        translated_table_offset,
        0,
        0,
    )
    tables = b"".join(struct.pack("<2I", *item) for item in original_table)
    tables += b"".join(struct.pack("<2I", *item) for item in translated_table)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(header + tables + originals + translations)


def main():
    base = Path(__file__).resolve().parents[1]
    po_files = list((base / "locale").rglob("*.po"))
    for po_file in po_files:
        mo_file = po_file.with_suffix(".mo")
        compile_mo(parse_po(po_file), mo_file)
        print(f"Compiled {po_file.relative_to(base)} -> {mo_file.relative_to(base)}")


if __name__ == "__main__":
    main()
