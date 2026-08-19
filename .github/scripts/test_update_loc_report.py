import datetime
import os
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


if __name__ == "__main__":
    unittest.main()
