import pytest
from safqa_scraper.utils import parse_budget


def test_european_format():
    assert parse_budget("1.500.000,00") == 1500000.00


def test_us_format():
    assert parse_budget("1,500,000.00") == 1500000.00


def test_plain_number():
    assert parse_budget("1500000") == 1500000.00


def test_with_mad_currency():
    assert parse_budget("1.500.000,00 MAD") == 1500000.00


def test_with_dh_currency():
    assert parse_budget("1.500.000,00 DH") == 1500000.00


def test_with_dhs_currency():
    assert parse_budget("1.500.000,00 Dhs") == 1500000.00


def test_whitespace_insensitive():
    assert parse_budget("  1.500.000,00  ") == 1500000.00


def test_unparseable_returns_none():
    assert parse_budget("N/A") is None


def test_empty_string_returns_none():
    assert parse_budget("") is None


def test_none_input_returns_none():
    assert parse_budget(None) is None


def test_zero():
    assert parse_budget("0") == 0.0


def test_no_decimal():
    assert parse_budget("750000") == 750000.00


def test_european_with_cents():
    assert parse_budget("750.000,50") == 750000.50


def test_us_with_cents():
    assert parse_budget("750,000.50") == 750000.50
