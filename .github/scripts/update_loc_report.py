#!/usr/bin/env python3
"""Replace the loc-report marker block in README.md.

Reads a Markdown table on stdin; rewrites the text between the
loc-report markers with that table plus an "Updated YYYY-MM-DD" line.
Pure stdlib. Exits nonzero if the markers are missing or duplicated,
so a mangled README fails the CI job instead of being clobbered.
"""
import datetime
import pathlib
import sys

BEGIN = "<!-- loc-report:begin -->"
END = "<!-- loc-report:end -->"


def splice(readme_text, table_md, today):
    """Return readme_text with the marker block's contents replaced."""
    if not table_md.strip():
        raise ValueError("table_md is empty; refusing to blank the loc-report block")
    if readme_text.count(BEGIN) != 1 or readme_text.count(END) != 1:
        raise ValueError("README must contain exactly one begin and one end marker")
    if readme_text.index(BEGIN) > readme_text.index(END):
        raise ValueError("loc-report markers are in the wrong order")
    head, rest = readme_text.split(BEGIN)
    _, tail = rest.split(END)
    block = f"{BEGIN}\n{table_md.strip()}\n\n*Updated {today.isoformat()}*\n{END}"
    return head + block + tail


def main():
    readme = pathlib.Path("README.md")
    today = datetime.datetime.now(datetime.timezone.utc).date()
    readme.write_text(
        splice(readme.read_text(encoding="utf-8"), sys.stdin.read(), today),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
