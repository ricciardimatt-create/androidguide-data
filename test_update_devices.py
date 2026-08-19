import io
import unittest
from contextlib import redirect_stdout

from update_devices import normalize


class NormalizeSecurityEolTests(unittest.TestCase):
    def test_support_date_is_not_substituted_for_missing_security_eol(self):
        raw = [{
            "cycle": "galaxy-a23-5g",
            "releaseLabel": "Galaxy A23 5G",
            "releaseDate": "2022-09-02",
            "eol": False,
            "support": "2025-09-02",
        }]

        output = io.StringIO()
        with redirect_stdout(output):
            devices = normalize("Samsung", raw)

        self.assertEqual([], devices)
        self.assertIn("support date not substituted", output.getvalue())

    def test_explicit_security_eol_is_retained(self):
        raw = [{
            "cycle": "galaxy-s24",
            "releaseLabel": "Galaxy S24",
            "releaseDate": "2024-01-24",
            "eol": "2031-01-24",
            "support": "2031-01-24",
        }]

        self.assertEqual(
            [{
                "id": "samsung-galaxy-s24",
                "brand": "Samsung",
                "model": "Galaxy S24",
                "released": "2024-01-24",
                "eol": "2031-01-24",
                "source": "endoflife.date",
            }],
            normalize("Samsung", raw),
        )


if __name__ == "__main__":
    unittest.main()
