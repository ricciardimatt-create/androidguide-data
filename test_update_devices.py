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
        semantic_failures = []
        with redirect_stdout(output):
            devices = normalize("Samsung", raw, semantic_failures)

        self.assertEqual([], devices)
        self.assertIn("support date cannot substitute", output.getvalue())
        self.assertEqual(1, len(semantic_failures))
        self.assertIn("Galaxy A23 5G", semantic_failures[0])

    def test_out_of_scope_support_only_record_does_not_trip_guard(self):
        raw = [{
            "cycle": "galaxy-m99",
            "releaseLabel": "Galaxy M99",
            "releaseDate": "2026-01-01",
            "eol": False,
            "support": "2030-01-01",
        }]
        semantic_failures = []

        devices = normalize("Samsung", raw, semantic_failures)

        self.assertEqual([], devices)
        self.assertEqual([], semantic_failures)

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
