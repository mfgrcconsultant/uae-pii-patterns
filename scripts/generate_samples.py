"""Generate synthetic test data with valid checksums. All values are FAKE.

Run from the repo root:  python scripts/generate_samples.py
"""
from __future__ import annotations

import csv
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
random.seed(971)


def luhn_check_digit(partial: str) -> str:
    total = 0
    for i, ch in enumerate(reversed(partial)):
        n = int(ch)
        if i % 2 == 0:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return str((10 - total % 10) % 10)


def fake_eid() -> str:
    partial = f"784{random.randint(1960, 2015)}{random.randint(0, 9_999_999):07d}"
    d = partial + luhn_check_digit(partial)
    return f"{d[:3]}-{d[3:7]}-{d[7:14]}-{d[14]}"


def fake_iban() -> str:
    bban = f"{random.randint(1, 999):03d}{random.randint(0, 10**16 - 1):016d}"
    check = 98 - int(bban + "101400") % 97
    s = f"AE{check:02d}{bban}"
    return " ".join(s[i:i + 4] for i in range(0, len(s), 4))


def corrupt(value: str) -> str:
    chars = list(value)
    idx = max(i for i, c in enumerate(chars) if c.isdigit())
    chars[idx] = str((int(chars[idx]) + 1) % 10)
    return "".join(chars)


def main() -> None:
    rows = []
    for _ in range(5):
        e = fake_eid()
        rows += [("uae_emirates_id", e, "true", f"Customer Emirates ID: {e}"),
                 ("uae_emirates_id", corrupt(e), "false", f"Emirates ID {corrupt(e)} (bad checksum)")]
        i = fake_iban()
        rows += [("uae_iban", i, "true", f"Beneficiary IBAN {i}"),
                 ("uae_iban", corrupt(i), "false", f"IBAN {corrupt(i)} (bad checksum)")]
    rows += [
        ("uae_mobile", "+971 50 123 4567", "true", "Mobile: +971 50 123 4567"),
        ("uae_mobile", "0551234567", "true", "WhatsApp 0551234567"),
        ("uae_landline", "+971 4 123 4567", "true", "Office tel +971 4 123 4567"),
        ("uae_trn", "100123456700003", "true", "TRN: 100123456700003"),
        ("uae_trn", "100123456700003", "false", "Reference 100123456700003 (no keyword)"),
        ("uae_passport", "A1234567", "true", "Passport No. A1234567"),
    ]
    path = ROOT / "samples/synthetic-data.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["entity", "value", "should_detect", "context"])
        w.writerows(rows)
    print(f"Wrote {len(rows)} synthetic rows to {path}")


if __name__ == "__main__":
    main()
