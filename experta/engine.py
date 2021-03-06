"""
``experta engine`` represents ``CLIPS modules``

"""

import inspect
import logging
from itertools import chain

import experta
from experta import abstract
from experta import watchers
from experta.agenda import Agenda
from experta.deffacts import DefFacts
from experta.fact import Fact
from experta.fact import InitialFact
from experta.factlist import FactList
from experta.rule import Rule

logging.basicConfig()


class KnowledgeEngine:
    """
    This represents a clips' ``module``, which is an ``inference engine``
    holding a set of ``rules`` (as :obj:`experta.rule.Rule` objects),
    an ``agenda`` (as :obj:`experta.agenda.Agenda` object)
    and a ``fact-list`` (as :obj:`experta.factlist.FactList` objects)

    This could be considered, when inherited from, as the
    ``knowlege-base``.
    """
    from experta.matchers import ReteMatcher as __matcher__
    from experta.strategies import DepthStrategy as __strategy__

    def __init__(self):
        self.running = False
        self.facts = FactList()
        self.agenda = Agenda()

        self.init_matcher()

        if (isinstance(self.__strategy__, type)
                and issubclass(self.__strategy__, abstract.Strategy)):
            self.strategy = self.__strategy__()
        else:
            raise TypeError("__strategy__ must be a subclass of Strategy")

    def init_matcher(self):
        if (isinstance(self.__matcher__, type)
                and issubclass(self.__matcher__, abstract.Matcher)):
            self.matcher = self.__matcher__(self)
        else:
            raise TypeError("__matcher__ must be a subclass of Matcher")

    @staticmethod
    def _get_real_modifiers(**modifiers):
        for k, v in modifiers.items():
            if k.startswith('_') and k[1:].isnumeric():
                yield (int(k[1:]), v)
            else:
                yield (k, v)

    def modify(self, declared_fact, **modifiers):
        """

        Modifies a fact.

        Facts are immutable in Clips, thus, as documented in clips
        reference manual, this retracts a fact and then re-declares it

        `modifiers` must be a Mapping object containing keys and values
        to be changed.

        To allow modifying positional facts, the user can pass a string
        containing the symbol "_" followed by the numeric index
        (starting with 0). Ex::

            >>> ke.modify(my_fact, _0="hello", _1="world", other_key="!")

        """
        self.retract(declared_fact)

        newfact = declared_fact.copy()
        newfact.update(dict(self._get_real_modifiers(**modifiers)))

        return self.declare(newfact)

    def duplicate(self, template_fact, **modifiers):
        """Create a new fact from an existing one."""

        newfact = template_fact.copy()
        newfact.update(dict(self._get_real_modifiers(**modifiers)))

        return self.declare(newfact)

    @DefFacts(order=-1)
    def _declare_initial_fact(self):
        yield InitialFact()

    def _get_by_type(self, wanted_type):
        for _, obj in inspect.getmembers(self):
            if isinstance(obj, wanted_type):
                obj.ke = self
                yield obj

    def get_rules(self):
        """Return the existing rules."""
        return list(self._get_by_type(Rule))

    def get_deffacts(self):
        """Return the existing deffacts sorted by the internal order"""
        return sorted(self._get_by_type(DefFacts), key=lambda d: d.order)

    def get_activations(self):
        """
        Return activations
        """
        r = self.matcher.changes(*self.facts.changes)
        return r

    def retract(self, idx_or_declared_fact, cascade=True):
        """
        Retracts a specific fact, using its index

        .. note::
            This updates the agenda
        """
        # if type(idx_or_declared_fact) is dict:
        # idx_or_declared_fact = idx_or_declared_fact['__factid__']

        if type(idx_or_declared_fact) is int:
            idx_or_declared_fact = self.facts[idx_or_declared_fact]

        self.facts.retract(idx_or_declared_fact)

        if not self.running:
            added, removed = self.get_activations()
            self.strategy.update_agenda(self.agenda, added, removed)

        if cascade:
            for child in idx_or_declared_fact.__children__:
                try:
                    self.retract(child)
                except IndexError:  # child has already been deleted
                    pass

    def step(self):
        """
            added, removed = self.get_activations()

        perform one step of inference and return the next activation
        :return: activation
        """

        added, removed = self.get_activations()
        # if len(added) > 0:
        # print("added in step: ", added)
        self.strategy.update_agenda(self.agenda, added, removed)

        if watchers.worth('AGENDA', 'DEBUG'):  # pragma: no cover
            for idx, act in enumerate(self.agenda.activations):
                watchers.AGENDA.debug(
                    "%d: %r %r",
                    idx,
                    act.rule.__name__,
                    ", ".join(str(f) for f in act.facts))

    def run(self, steps=float('inf')):
        """
        Execute agenda activations
        """

        self.running = True
        activation = None
        execution = 0
        while steps > 0 and self.running:
            self.step()
            activation = self.agenda.get_next()

            if activation is None:
                break
            else:
                steps -= 1
                execution += 1

                watchers.RULES.info(
                    "FIRE %s %s: %s",
                    execution,
                    activation.rule.__name__,
                    ", ".join(str(f) for f in activation.facts))

                activation.fire(self)

        self.running = False

    def halt(self):
        self.running = False

    def reset(self, **kwargs):
        """
        Performs a reset as per CLIPS behaviour (resets the
        agenda and factlist and declares InitialFact())
        Any keyword argument passed to `reset` will be passed to @DefFacts
        which have those arguments on their signature.
        .. note:: If persistent facts have been added, they'll be
                  re-declared.
        """

        self.agenda = Agenda()
        self.facts = FactList()

        self.matcher.reset()

        deffacts = []
        for deffact in self.get_deffacts():

            signature = inspect.signature(deffact)
            if not any(p.kind == inspect.Parameter.VAR_KEYWORD
                       for p in signature.parameters.values()):
                # There is not **kwargs defined. Pass only the defined
                # names.
                args = set(signature.parameters.keys())
                deffacts.append(
                    deffact(**{k: v for k, v in kwargs.items()
                               if k in args}))
            else:
                deffacts.append(deffact(**kwargs))

        # Declare all facts yielded by deffacts

        self.__declare(*chain.from_iterable(deffacts), cond=True)

        self.running = False
        self.matcher._get_conflict_set_nodes.cache_clear()

    def __declare(self, *facts, cond=False):

        """
        Internal declaration method. Used for ``declare`` and ``deffacts``
        """
        if any(f.has_field_constraints() for f in facts):
            raise TypeError(
                "Declared facts cannot contain conditional elements")
        elif any(f.has_nested_accessor() for f in facts):
            raise KeyError(
                "Cannot declare facts containing double underscores as keys.")
        else:

            last_inserted = None

            for fact in facts:
                last_inserted = self.facts.declare(fact)

            if not self.running:
                added, removed = self.get_activations()

                self.strategy.update_agenda(self.agenda, added, removed)

            return last_inserted

    def declare(self, *facts):
        """
        Declare from inside a fact, equivalent to ``assert`` in clips.

        .. note::

            This updates the agenda.
        """
        # try:
        #     activation_frame = inspect.currentframe().f_back.f_back.f_back
        #     assert type(activation_frame.f_locals[
        #                     'self']) == experta.activation.Activation
        #     for fact in facts:
        #         fact.__source__ = activation_frame.f_locals['self']
        #         for f in fact.__source__.facts:
        #             if not isinstance(f, Fact):
        #                 continue
        #             f.__children__.append(fact)
        # except (AssertionError, AttributeError, KeyError):
        #     pass

        try:
            activation_frame = inspect.currentframe().f_back
            for i in range(7):
                if 'self' in activation_frame.f_locals:
                    if type(activation_frame.f_locals[
                                'self']) == experta.activation.Activation:
                        for fact in facts:
                            fact.__source__ = activation_frame.f_locals['self']
                            for f in fact.__source__.facts:
                                if not isinstance(f, Fact):
                                    continue
                                f.__children__.append(fact)
                        break
                activation_frame = activation_frame.f_back
        except (AssertionError, AttributeError, KeyError) as e:
            pass

        if not self.facts:
            pass  # watchers.ENGINE.warning("Declaring fact before reset()")

        return self.__declare(*facts)
