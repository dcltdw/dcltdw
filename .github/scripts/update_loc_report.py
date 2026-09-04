#!/usr/bin/env python3
"""Replace the loc-report marker block in README.md.

Reads a Markdown table on stdin; reorders its rows to match the order the
repos are linked in the README's prose, then rewrites the text between the
loc-report markers with that table plus an "Updated YYYY-MM-DD" line.
Pure stdlib. Exits nonzero if the markers are missing or duplicated, or if
the prose and the counted repos have drifted apart, so a mangled README
fails the CI job instead of being clobbered.
"""
import datetime
import pathlib
import re
import sys

BEGIN = "<!-- loc-report:begin -->"
END = "<!-- loc-report:end -->"
REPO_LINK = re.compile(r"github\.com/dcltdw/([A-Za-z0-9._-]+)")


def readme_order(readme_text):
    """Return repo names as linked in the prose, in the order they appear.

    Only the text above the begin marker counts, so neither the generated
    table nor the Links section can influence the ordering. A repo linked
    more than once keeps its first position rather than raising: mentioning
    a project twice in prose is ordinary writing, not drift.
    """
    if BEGIN not in readme_text:
        raise ValueError("README must contain the loc-report begin marker")
    order = []
    for name in REPO_LINK.findall(readme_text.split(BEGIN)[0]):
        if name not in order:
            order.append(name)
    return order


def reorder(table_md, order):
    """Return table_md with its data rows sorted to match order.

    The header, its separator and a trailing TOTAL row keep their places.

    Raises if the counted repos and order disagree in either direction. A
    repo counted but never mentioned in the prose — or mentioned but not
    counted — means the workflow's repo list and the README have drifted,
    and the table cannot be ordered against a list it does not match. That
    is worth a red job rather than a quietly half-sorted table.
    """
    lines = [line for line in table_md.strip().splitlines() if line.strip()]
    if len(lines) < 2:
        raise ValueError("table needs at least a header and a separator row")
    header, separator = lines[0], lines[1]
    body = lines[2:]

    total = []
    if body and body[-1].lstrip("| ").startswith("**TOTAL**"):
        total = [body.pop()]

    rows = {}
    for line in body:
        name = line.split("|")[1].strip()
        if name in rows:
            raise ValueError(f"duplicate row in the LOC table: {name}")
        rows[name] = line

    counted, listed = set(rows), set(order)
    if counted != listed:
        raise ValueError(
            "the README prose and the counted repos have drifted apart; "
            f"counted but not linked in the prose: {sorted(counted - listed)}; "
            f"linked in the prose but not counted: {sorted(listed - counted)}"
        )

    return "\n".join([header, separator] + [rows[name] for name in order] + total)


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
    readme_text = readme.read_text(encoding="utf-8")
    today = datetime.datetime.now(datetime.timezone.utc).date()
    table_md = reorder(sys.stdin.read(), readme_order(readme_text))
    readme.write_text(splice(readme_text, table_md, today), encoding="utf-8")


if __name__ == "__main__":
    main()
