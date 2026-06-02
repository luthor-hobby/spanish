#!/usr/bin/env python3
"""
Build script for the spanish git repo.

Copies HTML files from Spanish Study into structured subdirectories
and generates index.html files at every level.

Run from anywhere:
    python3 build.py
"""

import os
import shutil
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
SRC = SCRIPT_DIR.parent  # Spanish Study/
DEST = SCRIPT_DIR         # spanish/

# Source subdirs to copy wholesale (preserving their own subdirectory structure)
DIR_MAPPINGS = [
    "entrevista",
    "flashandfire",
    "placeres_prohibidos",
    "collins_grammar_html",
]

# Individual files: (src relative to SRC, dest relative to DEST)
FILE_MAPPINGS = [
    ("lingo_reader.html", "dialogues/lingo_reader.html"),
]

PRETTY_NAMES = {
    "entrevista":          "Entrevista con el Vampiro",
    "flashandfire":        "Flash and Fire",
    "placeres_prohibidos": "Placeres Prohibidos",
    "collins_grammar_html":"Collins Spanish Grammar",
    "dialogues":           "Dialogues",
    "audiobook":           "Audiobook",
    "html":                "HTML Reader",
}

INDEX_CSS = """
  body { font-family: Georgia, serif; max-width: 700px; margin: 40px auto;
         padding: 0 20px; background: #fafaf8; color: #222; }
  h1   { border-bottom: 2px solid #c8a96e; padding-bottom: 8px; color: #5a3e1b; }
  ul   { list-style: none; padding: 0; }
  li   { padding: 6px 0; border-bottom: 1px solid #e8e0d0; }
  li.dir a { font-weight: bold; }
  a    { color: #5a3e1b; text-decoration: none; }
  a:hover { text-decoration: underline; }
  .back { margin-bottom: 20px; font-size: 0.9em; }
"""


def pretty(name):
    return PRETTY_NAMES.get(name, name.replace("_", " ").replace("-", " ").title())


def copy_html_tree(src_dir, dest_dir):
    src_dir, dest_dir = Path(src_dir), Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    for item in sorted(src_dir.iterdir()):
        if item.name == "index.html":
            continue
        if item.is_file() and item.suffix.lower() == ".html":
            shutil.copy2(item, dest_dir / item.name)
        elif item.is_dir():
            copy_html_tree(item, dest_dir / item.name)


def write_index(directory, title, is_root=False):
    directory = Path(directory)
    subdirs = sorted(d for d in directory.iterdir() if d.is_dir() and not d.name.startswith("."))
    files   = sorted(
        f for f in directory.iterdir()
        if f.is_file() and f.suffix.lower() == ".html" and f.name != "index.html"
    )

    items = []
    for d in subdirs:
        items.append(f'<li class="dir"><a href="{d.name}/index.html">{pretty(d.name)}/</a></li>')
    for f in files:
        label = f.stem.replace("_", " ").replace("-", " ")
        items.append(f'<li class="file"><a href="{f.name}">{label}</a></li>')

    back = "" if is_root else '<p class="back"><a href="../index.html">&larr; Back</a></p>'

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>{INDEX_CSS}</style>
</head>
<body>
{back}
<h1>{title}</h1>
<ul>
  {"".join(items)}
</ul>
</body>
</html>"""

    (directory / "index.html").write_text(html, encoding="utf-8")
    print(f"  wrote index → {directory.relative_to(DEST)}")


def gen_indexes(directory, title=None, is_root=False):
    directory = Path(directory)
    write_index(directory, title or pretty(directory.name), is_root=is_root)
    for sub in sorted(directory.iterdir()):
        if sub.is_dir() and not sub.name.startswith("."):
            gen_indexes(sub)


def build():
    print("=== Copying HTML files ===")
    for name in DIR_MAPPINGS:
        src = SRC / name
        dest = DEST / name
        if src.exists():
            print(f"  {name}/")
            copy_html_tree(src, dest)
        else:
            print(f"  WARNING: {src} not found, skipping")

    for src_rel, dest_rel in FILE_MAPPINGS:
        src  = SRC / src_rel
        dest = DEST / dest_rel
        if src.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            print(f"  {src_rel} → {dest_rel}")
        else:
            print(f"  WARNING: {src} not found, skipping")

    print("\n=== Generating index files ===")
    gen_indexes(DEST, title="Spanish Study", is_root=True)

    print("\nDone.")


if __name__ == "__main__":
    build()
