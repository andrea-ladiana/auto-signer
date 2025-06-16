import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from pdf_signer import _parse_pages_basic


def test_first_page():
    assert _parse_pages_basic('first', 5) == [0]


def test_last_page():
    assert _parse_pages_basic('last', 5) == [4]


def test_single_page():
    assert _parse_pages_basic('3', 5) == [2]


def test_comma_separated_list():
    assert _parse_pages_basic('1,3,5', 5) == [0, 2, 4]


def test_range():
    assert _parse_pages_basic('2-4', 5) == [1, 2, 3]


def test_mixed_spec():
    assert _parse_pages_basic('1,3-5', 5) == [0, 2, 3, 4]


def test_range_exceeds_total_pages():
    assert _parse_pages_basic('2-10', 5) == [1, 2, 3, 4]


def test_invalid_spec_returns_empty():
    assert _parse_pages_basic('invalid', 5) == []
