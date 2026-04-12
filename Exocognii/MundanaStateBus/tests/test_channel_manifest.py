# tests/test_channel_manifest.py
# Mundana State Bus v1.0
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from mundana_channels import CHANNELS, BusChannelError, validate_channel


def test_all_known_channels_validate():
    for ch in CHANNELS:
        assert validate_channel(ch) == ch


def test_unknown_channel_raises():
    with pytest.raises(BusChannelError):
        validate_channel("mundana.bogus")


def test_empty_string_raises():
    with pytest.raises(BusChannelError):
        validate_channel("")


def test_partial_name_raises():
    with pytest.raises(BusChannelError):
        validate_channel("mundana")


def test_case_sensitive():
    with pytest.raises(BusChannelError):
        validate_channel("Mundana.Caelestis")


def test_error_message_contains_channel_name():
    try:
        validate_channel("mundana.ghost")
    except BusChannelError as e:
        assert "mundana.ghost" in str(e)
