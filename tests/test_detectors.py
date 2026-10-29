import csv
from pathlib import Path

import pytest

from uae_pii import detect, iban_valid, luhn_valid, mask

SAMPLES = Path(__file__).resolve().parents[1] / "samples" / "synthetic-data.csv"


def entities(text, **kw):
    return {m.entity for m in detect(text, **kw)}


@pytest.mark.parametrize("row", list(csv.DictReader(SAMPLES.open(encoding="utf-8"))))
def test_synthetic_samples(row):
    found = {m.entity: m.value for m in detect(row["context"])}
    if row["should_detect"] == "true":
        assert found.get(row["entity"]) == row["value"]
    else:
        assert row["entity"] not in found


def test_iban_mod97():
    assert iban_valid("AE07 0331 2345 6789 0123 456")
    assert not iban_valid("AE08 0331 2345 6789 0123 456")
    assert not iban_valid("GB82 WEST 1234 5698 7654 32")


def test_luhn():
    assert luhn_valid("79927398713")
    assert not luhn_valid("79927398710")


def test_emirates_id_formats():
    eid = next(r for r in csv.DictReader(SAMPLES.open(encoding="utf-8"))
               if r["entity"] == "uae_emirates_id" and r["should_detect"] == "true")["value"]
    assert "uae_emirates_id" in entities(eid)
    assert "uae_emirates_id" in entities(eid.replace("-", ""))
    assert "uae_emirates_id" in entities(eid.replace("-", " "))


def test_keyword_boosts_confidence():
    without = detect("call 0501234567 today")[0]
    with_kw = detect("mobile: 0501234567")[0]
    assert without.confidence == "medium"
    assert with_kw.confidence == "high"


def test_arabic_keyword():
    assert "uae_trn" in entities("الرقم الضريبي 100123456700003")


def test_keyword_required():
    assert "uae_passport" not in entities("ref A1234567")
    assert "uae_passport" in entities("جواز السفر A1234567")


def test_min_confidence_filter():
    assert entities("tel 04 123 4567", min_confidence="high") == set()


def test_no_mobile_inside_longer_number():
    assert "uae_mobile" not in entities("order 1234050123456789")


def test_mask():
    assert mask("784-1990-1234567-1") == "***-****-****567-1"
    assert mask("AE07 0331 2345 6789 0123 456").endswith("3 456")
    assert mask("A1234567") == "****4567"
