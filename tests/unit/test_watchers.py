"""
Test watchers module
"""


# def test_watchers_has_all_watchers():
#     """ Test that watchers module contains all watchers """
#     # pylint: disable=unused-variable
#     from experta.watchers import RULES # NOQA
#     from experta.watchers import AGENDA # NOQA
#     from experta.watchers import FACTS # NOQA
#     from experta.watchers import ACTIVATIONS # NOQA
# 
# 
# def test_watchers_watch():
#     """ Test that watch() method calls setlevel """
#     from experta.watchers import watch
#     from experta.watchers import RULES, FACTS, AGENDA, ACTIVATIONS
#     from unittest.mock import MagicMock
#     import logging
#     RULES.setLevel = MagicMock()
#     FACTS.setLevel = MagicMock()
#     AGENDA.setLevel = MagicMock()
#     ACTIVATIONS.setLevel = MagicMock()
#     watch()
#     RULES.setLevel.assert_called_with(logging.DEBUG)
#     AGENDA.setLevel.assert_called_with(logging.DEBUG)
#     FACTS.setLevel.assert_called_with(logging.DEBUG)
#     ACTIVATIONS.setLevel.assert_called_with(logging.DEBUG)
# 
# 
# def test_watchers_watch_once():
#     """ Test that watch() method calls setlevel """
#     from experta.watchers import watch
#     from experta.watchers import RULES, FACTS, AGENDA, ACTIVATIONS
#     from unittest.mock import MagicMock
#     import logging
#     for watcher in [RULES, FACTS, AGENDA, ACTIVATIONS]:
#         watcher.setLevel = MagicMock()
#         watch(watcher)
#         watcher.setLevel.assert_called_with(logging.DEBUG)
