# UAE PII Patterns 🔍

**Detection patterns and validators for UAE personal data**: Emirates ID, UAE IBAN, phone numbers, TRN, and passport numbers. Ready for Python, Microsoft Presidio, Microsoft Purview, Forcepoint DLP, and any regex-capable tool.

أنماط الكشف عن البيانات الشخصية الإماراتية لأنظمة منع تسرب البيانات

![Tests](https://github.com/mfgrcconsultant/uae-pii-patterns/actions/workflows/tests.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![PDPL](https://img.shields.io/badge/Supports-UAE_PDPL-000000)

> ⚠️ **All sample data in this repo is synthetic.** Never commit real personal data. Formats are based on publicly documented structures. Test in your environment before using any pattern in blocking mode.

---

## Why this exists

Generic DLP and privacy tools detect US SSNs and EU IBANs out of the box but often miss UAE identifiers, or flag every 15-digit number as an Emirates ID. This repo provides:

- **Checksum validation** (Luhn for Emirates ID, mod-97 for IBAN) to cut false positives
- **English and Arabic keywords** for proximity matching
- **One source of truth** ([`uae_pii/patterns.yaml`](uae_pii/patterns.yaml)) that generates every export
- **Confidence levels** to support a monitor-first, then block, rollout

Useful for **UAE PDPL**, **DIFC DP Law**, **ADGM DPR**, **ADHICS**, and **UAE IA** data protection controls.

---

## Supported identifiers

| Identifier | Example (fake) | Validation | Base confidence | Keyword required |
|---|---|---|---|---|
| Emirates ID | `784-1990-1234567-X` | Luhn check digit | 🟢 High | No |
| UAE IBAN | `AE07 0331 2345 6789 0123 456` | ISO 13616 mod-97 | 🟢 High | No |
| UAE mobile | `+971 50 123 4567`, `0501234567` | Format | 🟡 Medium | No |
| UAE landline | `+971 4 123 4567` | Format + area code | 🔴 Low | No |
| TRN (VAT / Corporate Tax) | `100123456700003` | Format | 🟡 Medium | **Yes** |
| Passport number | `A1234567` | Format | 🔴 Low | **Yes** |

A nearby keyword (within 300 characters) raises confidence by one level. Identifiers marked **keyword required** are only reported when a keyword is present, because their formats overlap with ordinary numbers.

---

## Quick start

```bash
git clone https://github.com/mfgrcconsultant/uae-pii-patterns.git
cd uae-pii-patterns
pip install -e .
```

### Command line

```bash
# Scan a file (values masked by default)
uae-pii document.txt

# JSON output, high confidence only
uae-pii document.txt --json --min-confidence high

# Pipe text in
echo "Mobile: +971 50 123 4567" | uae-pii
```

Example output:

```
high    uae_emirates_id    ***-****-****366-4               @ 22-40
high    uae_mobile         +*** ** *** 4567                 @ 49-65
high    uae_iban           **** **** **** **** ***3 456     @ 72-100
medium  uae_trn            ***********0003                  @ 116-131
```

The exit code is `1` when PII is found, so you can use it in CI pipelines and pre-commit hooks.

### Python

```python
from uae_pii import detect, mask

for m in detect("Customer Emirates ID: 784-1976-3831366-4", min_confidence="medium"):
    print(m.entity, mask(m.value), m.confidence)
```

### Microsoft Presidio

```bash
pip install -e ".[presidio]"
```

```python
from presidio_analyzer import AnalyzerEngine
from uae_pii.presidio import get_recognizers

analyzer = AnalyzerEngine()
for recognizer in get_recognizers():
    analyzer.registry.add_recognizer(recognizer)

results = analyzer.analyze(text="IBAN AE07 0331 2345 6789 0123 456", language="en")
```

---

## DLP exports

| Tool | File | Notes |
|---|---|---|
| Microsoft Purview | [`exports/purview/uae-pii-rulepack.xml`](exports/purview/uae-pii-rulepack.xml) | Custom sensitive information type rule package. Upload with `New-DlpSensitiveInformationTypeRulePackage`. |
| Forcepoint DLP | [`exports/forcepoint/README.md`](exports/forcepoint/README.md) | Regex and key-phrase classifier settings with a rollout guide. |
| Any regex tool | [`exports/generic-regex.md`](exports/generic-regex.md) | Copy-paste patterns with keywords and examples. |

**Purview upload (Security & Compliance PowerShell):**

```powershell
Connect-IPPSSession
New-DlpSensitiveInformationTypeRulePackage -FileData ([System.IO.File]::ReadAllBytes("uae-pii-rulepack.xml"))
```

> Regex-only engines can't run checksum validation. Expect more false positives there than with the Python or Presidio versions, and rely on keywords and match-count thresholds.

---

## Recommended rollout

1. **Monitor:** deploy in audit or monitor mode for 2–4 weeks.
2. **Tune:** review incidents, then adjust keywords and thresholds.
3. **Notify:** enable user notifications or policy tips for medium-confidence matches.
4. **Block:** block high-confidence matches (validated Emirates ID and IBAN) on external channels.

---

## Project structure

```
uae-pii-patterns/
├── uae_pii/
│   ├── patterns.yaml        # Single source of truth
│   ├── detectors.py         # Regex + validators + keyword proximity
│   ├── presidio.py          # Presidio recognizers
│   └── __main__.py          # CLI
├── exports/                 # Generated: Purview, Forcepoint, generic regex
├── samples/
│   └── synthetic-data.csv   # Fake values with valid checksums
├── scripts/
│   ├── build_exports.py     # Regenerates exports/ from patterns.yaml
│   └── generate_samples.py  # Regenerates synthetic test data
└── tests/                   # pytest suite (runs in GitHub Actions)
```

---

## Contributing

To change or add a pattern:

1. Edit [`uae_pii/patterns.yaml`](uae_pii/patterns.yaml).
2. Add synthetic test cases in `scripts/generate_samples.py` or `tests/`.
3. Run:
   ```bash
   python scripts/generate_samples.py
   python scripts/build_exports.py
   pytest
   ```
4. Open a pull request. CI fails if the exports are out of date.

**Roadmap:** trade licence numbers (by emirate), UID numbers, labour card numbers, vehicle plates, and DIFC/ADGM company registration numbers.

**Never include real personal data** in issues, pull requests or tests.

---

## Related

- [Awesome UAE GRC](https://github.com/mfgrcconsultant/awesome-uae-grc) - Curated UAE GRC resources

## Disclaimer

Provided for educational and defensive purposes, as is, without warranty. Not legal advice. Identifier formats may change; verify against official sources. Not affiliated with any UAE government entity.

## License

[MIT](LICENSE) © 2026 Mohamed Faizal (MoFa)
