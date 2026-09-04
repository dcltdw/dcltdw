import datetime
import os
import re
import pathlib
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import update_loc_report

TODAY = datetime.date(2026, 8, 19)
README = """# Hi

<!-- loc-report:begin -->
old content
<!-- loc-report:end -->

## Links
"""


class SpliceTest(unittest.TestCase):
    def test_replaces_block_and_stamps_date(self):
        result = update_loc_report.splice(README, "| a |\n| 1 |\n", TODAY)
        self.assertEqual(
            result,
            """# Hi

<!-- loc-report:begin -->
| a |
| 1 |

*Updated 2026-08-19*
<!-- loc-report:end -->

## Links
""",
        )

    def test_idempotent(self):
        once = update_loc_report.splice(README, "| a |\n", TODAY)
        twice = update_loc_report.splice(once, "| a |\n", TODAY)
        self.assertEqual(once, twice)

    def test_missing_markers_raise(self):
        with self.assertRaises(ValueError):
            update_loc_report.splice("# Hi\n", "| a |", TODAY)

    def test_duplicate_markers_raise(self):
        with self.assertRaises(ValueError):
            update_loc_report.splice(README + README, "| a |", TODAY)

    def test_reversed_markers_raise(self):
        reversed_readme = README.replace(
            "<!-- loc-report:begin -->", "<!-- TMP -->"
        ).replace(
            "<!-- loc-report:end -->", "<!-- loc-report:begin -->"
        ).replace("<!-- TMP -->", "<!-- loc-report:end -->")
        with self.assertRaises(ValueError):
            update_loc_report.splice(reversed_readme, "| a |", TODAY)

    def test_empty_table_raises(self):
        with self.assertRaises(ValueError):
            update_loc_report.splice(README, "   \n  \n", TODAY)


class RealReadmeTest(unittest.TestCase):
    def test_real_readme_has_one_well_formed_marker_pair(self):
        readme_path = pathlib.Path(__file__).resolve().parents[2] / "README.md"
        readme_text = readme_path.read_text(encoding="utf-8")
        result = update_loc_report.splice(readme_text, "| a |\n| 1 |\n", TODAY)
        self.assertEqual(result.count(update_loc_report.BEGIN), 1)
        self.assertEqual(result.count(update_loc_report.END), 1)

ORDER_README = """# Hi

## What I'm working on

- **[alpha](https://github.com/dcltdw/alpha)** — first.
- **[beta](https://github.com/dcltdw/beta)** — second, see the
  [live demo](https://beta.example.com/) and [PyPI](https://pypi.org/project/beta/).
- **[gamma](https://github.com/dcltdw/gamma)** — third.

<!-- loc-report:begin -->
| Repo |
| zeta |
<!-- loc-report:end -->

## Links

- [omega](https://github.com/dcltdw/omega)
"""

TABLE = """| Repo | Code | Docs | Total |
|:---|---:|---:|---:|
| gamma | 3 | 30 | 33 |
| alpha | 1 | 10 | 11 |
| beta | 2 | 20 | 22 |
| **TOTAL** | **6** | **60** | **66** |
"""


class ReadmeOrderTest(unittest.TestCase):
    def test_returns_repos_in_prose_link_order(self):
        self.assertEqual(
            update_loc_report.readme_order(ORDER_README), ["alpha", "beta", "gamma"]
        )

    def test_ignores_links_at_or_below_the_begin_marker(self):
        # "zeta" sits inside the block and "omega" below it; neither is prose.
        order = update_loc_report.readme_order(ORDER_README)
        self.assertNotIn("omega", order)
        self.assertNotIn("zeta", order)

    def test_ignores_non_dcltdw_and_non_github_links(self):
        readme = ORDER_README.replace(
            "- **[gamma](https://github.com/dcltdw/gamma)** — third.",
            "- [other](https://github.com/someoneelse/gamma) and "
            "[site](https://gamma.example.com/)",
        )
        self.assertEqual(update_loc_report.readme_order(readme), ["alpha", "beta"])

    def test_dedupes_repeated_links_keeping_first_occurrence(self):
        readme = ORDER_README.replace(
            "- **[gamma](https://github.com/dcltdw/gamma)** — third.",
            "- **[gamma](https://github.com/dcltdw/gamma)** — third.\n"
            "- again: [alpha](https://github.com/dcltdw/alpha)",
        )
        self.assertEqual(
            update_loc_report.readme_order(readme), ["alpha", "beta", "gamma"]
        )

    def test_missing_begin_marker_raises(self):
        with self.assertRaises(ValueError):
            update_loc_report.readme_order("# Hi\n")


class ReorderTest(unittest.TestCase):
    def test_sorts_data_rows_into_the_given_order(self):
        result = update_loc_report.reorder(TABLE, ["alpha", "beta", "gamma"])
        self.assertEqual(
            result,
            """| Repo | Code | Docs | Total |
|:---|---:|---:|---:|
| alpha | 1 | 10 | 11 |
| beta | 2 | 20 | 22 |
| gamma | 3 | 30 | 33 |
| **TOTAL** | **6** | **60** | **66** |""",
        )

    def test_keeps_total_row_last(self):
        result = update_loc_report.reorder(TABLE, ["gamma", "beta", "alpha"])
        self.assertTrue(result.splitlines()[-1].startswith("| **TOTAL**"))

    def test_already_ordered_table_is_unchanged(self):
        once = update_loc_report.reorder(TABLE, ["alpha", "beta", "gamma"])
        twice = update_loc_report.reorder(once, ["alpha", "beta", "gamma"])
        self.assertEqual(once, twice)

    def test_counted_repo_missing_from_readme_raises(self):
        with self.assertRaises(ValueError) as ctx:
            update_loc_report.reorder(TABLE, ["alpha", "beta"])
        self.assertIn("gamma", str(ctx.exception))

    def test_readme_repo_missing_from_table_raises(self):
        with self.assertRaises(ValueError) as ctx:
            update_loc_report.reorder(TABLE, ["alpha", "beta", "gamma", "delta"])
        self.assertIn("delta", str(ctx.exception))

    def test_duplicate_data_rows_raise(self):
        dupe = TABLE.replace(
            "| beta | 2 | 20 | 22 |", "| beta | 2 | 20 | 22 |\n| beta | 9 | 90 | 99 |"
        )
        with self.assertRaises(ValueError) as ctx:
            update_loc_report.reorder(dupe, ["alpha", "beta", "gamma"])
        self.assertIn("beta", str(ctx.exception))


class RealReadmeOrderTest(unittest.TestCase):
    """The README prose and the workflow's REPOS list must not drift apart."""

    def _root(self):
        return pathlib.Path(__file__).resolve().parents[2]

    def test_prose_links_match_the_workflows_repos_list(self):
        readme = (self._root() / "README.md").read_text(encoding="utf-8")
        workflow = (self._root() / ".github/workflows/loc-report.yml").read_text(
            encoding="utf-8"
        )
        match = re.search(r'REPOS:\s*"([^"]*)"', workflow)
        self.assertIsNotNone(match, "loc-report.yml no longer declares REPOS")
        self.assertEqual(
            sorted(update_loc_report.readme_order(readme)),
            sorted(match.group(1).split()),
        )

if __name__ == "__main__":
    unittest.main()
