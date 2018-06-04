import pytest


def test_matcher_exists():
    try:
        from experta.abstract import Matcher
    except ImportError as exc:
        assert False, exc


def test_matcher_interface():
    from experta.abstract import Matcher

    assert Matcher.__abstractmethods__ == {'changes', 'reset'}
