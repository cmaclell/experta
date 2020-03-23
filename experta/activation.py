"""
Activations represent rules that matches against a specific factlist.

"""
from functools import total_ordering
import inspect

@total_ordering
class Activation:
    """
    Activation object
    """

    def __init__(self, rule, facts, context=None):
        self.rule = rule
        #self.ordered_facts = facts
        self.facts = set(facts)
        self.key = None
        if context is None:
            self.context = dict()
        else:
            self.context = context

    def fire(self, ke):
        #print(len(self.context))
        return self.rule(
            ke,
            **{k: v
               for k, v in self.context.items()
               if not k.startswith('__')})

    def __repr__(self):  # pragma: no cover
        return "Activation(rule={}, facts={}, context={})".format(
            self.rule, self.facts, self.context)

    def __eq__(self, other):
        try:
            return (self.context == other.context
                    and self.facts == other.facts
                    and self.rule == other.rule
                    and self.key == other.key)
        except AttributeError:
            return False

    def __lt__(self, other):
        return self.key < other.key

    def __hash__(self):
        return hash((self.rule,
                     frozenset(self.facts),
                     frozenset(self.context.items())))
