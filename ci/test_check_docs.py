#!/usr/bin/env python3
"""Tests for ci/check_docs.py (stdlib unittest; run: python3 -m unittest discover -s ci)."""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_docs  # noqa: E402


class FencedCodeTest(unittest.TestCase):
    def check(self, text):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "page.md")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(text)
            return check_docs.check_h1(path, "page.md") + check_docs.check_links(path, "page.md")

    def test_comment_in_shell_block_is_not_an_h1(self):
        doc = "# Page\n\n```bash\n# clone the repo\ngit clone x\n```\n"
        self.assertEqual(self.check(doc), [])

    def test_tilde_fence_and_longer_backtick_fence(self):
        doc = "# Page\n\n~~~sh\n# one\n~~~\n\n````md\n```\n# two\n```\n````\n"
        self.assertEqual(self.check(doc), [])

    def test_link_syntax_inside_code_block_is_not_checked(self):
        doc = "# Page\n\n```markdown\nSee [the guide](docs/your-page.md).\n```\n"
        self.assertEqual(self.check(doc), [])

    def test_prose_is_still_checked(self):
        doc = "# Page\n\n```\ncode\n```\n\n# Second\n\n[x](missing.md)\n"
        errors = self.check(doc)
        self.assertEqual(len(errors), 2, errors)
        self.assertIn("expected exactly one H1, found 2 (line 1, line 7)", errors[0])
        self.assertIn("page.md:9: dangling relative link 'missing.md'", errors[1])

    def test_unclosed_fence_hides_the_rest(self):
        doc = "# Page\n\n```\n# not a heading\n"
        self.assertEqual(self.check(doc), [])


if __name__ == "__main__":
    unittest.main()
