import os
import sys
import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from pdf_signer import _get_timestamp_position

@pytest.mark.parametrize("relative,expected", [
    ("below", "bottom-right"),
    ("above", "top-right"),
    ("left", "bottom-left"),
    ("right", "bottom-right"),
])
def test_center_position(relative, expected):
    assert _get_timestamp_position("center", relative) == expected

