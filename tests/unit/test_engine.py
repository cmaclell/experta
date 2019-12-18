"""
Engine tests
"""

import pytest

from hypothesis import given
from hypothesis import strategies as st


def test_KnowledgeEngine_has__facts():
    from experta.engine import KnowledgeEngine
    ke = KnowledgeEngine()
    assert hasattr(ke, 'facts')


def test_KnowledgeEngine__facts_is_FactList():
    from experta.engine import KnowledgeEngine
    from experta.factlist import FactList

    ke = KnowledgeEngine()
    assert isinstance(ke.facts, FactList)


def test_KnowledgeEngine_has_declare():
    from experta.engine import KnowledgeEngine
    ke = KnowledgeEngine()
    assert hasattr(ke, 'declare')


def test_KnowledgeEngine_declare_define_fact():
    from experta.engine import KnowledgeEngine
    from experta import Fact
    from unittest.mock import patch

    ke = KnowledgeEngine()
    with patch('experta.factlist.FactList') as mock:
        ke.facts = mock
        ke.declare(Fact())
        assert mock.declare.called


def test_KnowledgeEngine_has_retract():
    from experta.engine import KnowledgeEngine

    assert hasattr(KnowledgeEngine, 'retract')


def test_KnowledgeEngine_retract_retracts_fact():
    from experta.engine import KnowledgeEngine
    from unittest.mock import patch

    ke = KnowledgeEngine()
    with patch('experta.factlist.FactList') as mock:
        ke.facts = mock
        ke.retract({'__factid__': (0, )})
        assert mock.retract.called


def test_KnowledgeEngine_has_agenda():
    from experta.engine import KnowledgeEngine
    ke = KnowledgeEngine()
    assert hasattr(ke, 'agenda')


def test_KnowledgeEngine_agenda_is_Agenda():
    from experta.engine import KnowledgeEngine
    from experta.agenda import Agenda

    ke = KnowledgeEngine()

    assert isinstance(ke.agenda, Agenda)


def test_KnowledgeEngine_default_strategy_is_Depth():
    from experta.engine import KnowledgeEngine
    from experta.strategies import DepthStrategy

    assert KnowledgeEngine.__strategy__ is DepthStrategy


def test_KnowledgeEngine_default_strategy_is_Depth_instance():
    from experta.engine import KnowledgeEngine
    from experta.strategies import DepthStrategy

    assert isinstance(KnowledgeEngine().strategy, DepthStrategy)


def test_KnowledgeEngine_has_get_rules_property():
    from experta.engine import KnowledgeEngine

    assert hasattr(KnowledgeEngine, 'get_rules')


def test_KnowledgeEngine_get_rules_return_empty_list():
    from experta.engine import KnowledgeEngine

    ke = KnowledgeEngine()

    assert ke.get_rules() == []


def test_KnowledgeEngine_get_rules_returns_the_list_of_rules():
    from experta.engine import KnowledgeEngine
    from experta import Rule
    from experta import InitialFact

    class Test(KnowledgeEngine):
        @Rule(InitialFact())
        def rule1(self):
            pass

        @Rule(InitialFact())
        def rule2(self):
            pass

    ke = Test()

    rules = ke.get_rules()

    assert len(rules) == 2
    assert all(isinstance(x, Rule) for x in rules)


def test_KnowledgeEngine_get_activations_exists():
    from experta.engine import KnowledgeEngine

    assert hasattr(KnowledgeEngine, 'get_activations')


def test_KnowledgeEngine_get_activations_returns_a_list():
    from experta.engine import KnowledgeEngine
    ke = KnowledgeEngine()

    res = ke.get_activations()

    assert isinstance(res, tuple)
    assert isinstance(res[0], list)
    assert isinstance(res[1], list)


def test_KnowledgeEngine_get_activations_returns_activations_added():
    from experta.engine import KnowledgeEngine
    from experta import Rule
    from experta import Fact

    class Test(KnowledgeEngine):
        @Rule(Fact(a=1),
              Fact(b=1),
              Fact(c=1))
        def test(self):
            pass

    ke = Test()

    ke.reset()

    ke.declare(Fact(a=1))
    ke.declare(Fact(b=1))
    ke.declare(Fact(c=1))

    assert len(ke.agenda.activations) == 1


def test_KnowledgeEngine_has_run():
    from experta.engine import KnowledgeEngine
    assert hasattr(KnowledgeEngine, 'run')


def test_KnowledgeEngine_has_reset():
    from experta.engine import KnowledgeEngine
    assert hasattr(KnowledgeEngine, 'reset')


def test_KnowledgeEngine_reset_resets_agenda():
    from experta.engine import KnowledgeEngine
    ke = KnowledgeEngine()
    ke.agenda = None

    ke.reset()
    assert ke.agenda is not None


def test_KnowledgeEngine_reset_resets_facts():
    from experta.engine import KnowledgeEngine
    ke = KnowledgeEngine()
    ke.facts = None

    ke.reset()
    assert ke.facts is not None


def test_KnowledgeEngine_reset_declare_initialfact():
    from experta.engine import KnowledgeEngine

    ke = KnowledgeEngine()
    ke.reset()

    assert len(ke.facts) == 1


def test_KnowledgeEngine_run_1_fires_activation():
    from experta.engine import KnowledgeEngine
    from experta import Rule

    executed = False

    class Test(KnowledgeEngine):
        # pylint: disable=too-few-public-methods
        @Rule()
        def rule1(self):
            # pylint: disable=no-self-use
            nonlocal executed
            executed = True

    ke = Test()

    ke.reset()
    assert not executed

    ke.run(1)
    assert executed


def test_KnowledgeEngine_run_fires_all_activation():
    from experta.engine import KnowledgeEngine
    from experta import Rule

    executed = 0

    class Test(KnowledgeEngine):
        @Rule()
        def rule1(self):
            nonlocal executed
            executed += 1

        @Rule()
        def rule2(self):
            nonlocal executed
            executed += 1

        @Rule()
        def rule3(self):
            nonlocal executed
            executed += 1

    ke = Test()

    ke.reset()
    assert executed == 0

    ke.run()
    assert executed == 3


def test_KnowledgeEngine_has_initialfacts():
    from experta.engine import KnowledgeEngine
    from experta import InitialFact

    assert list(KnowledgeEngine()._declare_initial_fact()) == [InitialFact()]


def test_KnowledgeEngine_reset():
    """
    Given a set of fixed facts, they're still there
    after a reset.
    Also, we have in account that InitialFact() is always there.
    And that if we add a normal fact after that, it's not persistent
    """

    from experta.engine import KnowledgeEngine
    from experta.deffacts import DefFacts
    from experta import Fact

    class KE1(KnowledgeEngine):
        @DefFacts()
        def some_facts(self):
            yield Fact(foo=1)

    ke = KE1()
    ke.declare(Fact(bar=9))
    ke.declare(Fact(bar=7))
    ke.declare(Fact(bar=8))
    ke.reset()

    assert len(ke.facts) == 2  # Initialfact + Fact(foo=1)

    ke = KE1()
    ke.reset()
    ke.declare(Fact(foo=2))
    ke.declare(Fact(foo=3, bar=4))

    assert len(ke.facts) == 4


@pytest.mark.slow
@given(to_declare_random=st.lists(st.integers()))
def test_rules_are_executed_once(to_declare_random):
    from random import shuffle
    from experta.engine import KnowledgeEngine
    from experta import Rule, DefFacts
    from experta import Fact, L

    executions = []
    to_declare = list(set(to_declare_random + [1, 2, 3]))
    shuffle(to_declare)

    class Test(KnowledgeEngine):
        @DefFacts()
        def tested_deffacts(self):
            for i in to_declare:
                yield Fact(something=i)

        @Rule(Fact(something=L(1)),
              Fact(something=L(2)))
        def rule1(self):
            nonlocal executions
            executions.append('rule1')

        @Rule(Fact(something=L(3)))
        def rule2(self):
            nonlocal executions
            executions.append('rule2')

    ke = Test()
    ke.reset()
    ke.run()

    assert executions.count('rule1') == 1
    assert executions.count('rule2') == 1


def test_default_is_and():
    """
    Test that AND is the default behavior
    """
    from collections import defaultdict
    from experta.engine import KnowledgeEngine
    from experta import Rule, DefFacts
    from experta import Fact, L

    executions = []

    class Test(KnowledgeEngine):
        """ Test KE """
        @DefFacts()
        def test_facts(self):
            for n in (1, 2, 3):
                yield Fact(something=n)

        @Rule(Fact(something=1),
              Fact(something=2))
        def rule1(self):
            """ First rule, something=1 and something=2"""
            nonlocal executions
            executions.append('rule1')

        @Rule(Fact(something=3))
        def rule2(self):
            """ Second rule, only something=3 """
            nonlocal executions
            executions.append('rule2')

    ke = Test()
    ke.reset()
    ke.run()

    assert executions.count('rule1') == 1
    assert executions.count('rule2') == 1


def test_or_notmatching_operator():
    """
    Test OR operator
    """
    from experta.engine import KnowledgeEngine
    from experta import Rule, OR, DefFacts
    from experta import Fact, L

    class Test(KnowledgeEngine):
        """ Test KE """
        @DefFacts()
        def some_facts(self):
            yield Fact(other=1)
            yield Fact(other=2)

        @Rule(OR(Fact(something=1),
                 Fact(something=2)))
        def rule1(self):
            """ First rule, something=1 and something=2"""
            pass

    ke_ = Test()
    ke_.reset()
    assert len(ke_.agenda.activations) == 0


def test_or_operator():
    """
    Test OR operator
    """
    from experta.engine import KnowledgeEngine
    from experta import Rule, OR
    from experta import Fact, L

    class Test(KnowledgeEngine):
        """ Test KE """
        @Rule(OR(Fact(something=L(1)),
                 Fact(something=L(2))))
        def rule1(self):
            """ First rule, something=1 and something=2"""
            pass

    ke_ = Test()
    ke_.reset()
    ke_.declare(Fact(something=1))
    assert len(ke_.agenda.activations) == 1

    ke_ = Test()
    ke_.reset()
    ke_.declare(Fact(something=2))
    assert len(ke_.agenda.activations) == 1

    ke_ = Test()
    ke_.reset()
    ke_.declare(Fact(something=3))
    assert len(ke_.agenda.activations) == 0


def test_ke_inheritance():
    from experta import Rule
    from experta import Fact, L
    from experta.engine import KnowledgeEngine

    executed = False

    class Person(Fact):
        pass

    class Base(KnowledgeEngine):
        @Rule(Person(name=L('pepe')))
        def is_pepe(self):
            self.declare(Person(drinks="coffee"))

    class Test(Base):
        @Rule(Person(drinks=L("coffee")))
        def drinks_coffee(self):
            nonlocal executed
            executed = True

    ke_ = Test()
    ke_.reset()
    ke_.declare(Person(name='pepe'))
    ke_.run()

    assert executed


def test_nested_declarations():
    from experta import Rule
    from experta import Fact, L
    from experta.engine import KnowledgeEngine

    class Person(Fact):
        pass

    executed = False

    class Person_KE(KnowledgeEngine):
        @Rule(Person(name=L("David")))
        def david(self):
            self.declare(Person(name="Pepe"))

        @Rule(Person(name=L("Pepe")))
        def pepe(self):
            nonlocal executed
            executed = True

    ke_ = Person_KE()
    ke_.reset()
    ke_.declare(Person(name="David"))
    ke_.run()
    assert executed


def test_matching_different_number_of_arguments():
    from experta import Rule
    from experta import Fact, L
    from experta.engine import KnowledgeEngine

    class Person(Fact):
        pass

    executed = False

    class Person_KE(KnowledgeEngine):
        @Rule(Person(name=L("David")))
        def david(self):
            self.declare(Person(name="Pepe", apellido="stuff"))

        @Rule(Person(name=L("Pepe")))
        def pepe(self):
            nonlocal executed
            executed = True

    ke_ = Person_KE()
    ke_.reset()
    ke_.declare(Person(name="David"))
    ke_.run()
    assert executed


def test_matching_captured_different_facts_AND():
    from experta import Rule
    from experta import Fact, W, L
    from experta.engine import KnowledgeEngine

    class Person(Fact):
        pass

    executions = []

    class Person_KE(KnowledgeEngine):
        @Rule(Person(name=W("name")), Person(surname=W("name")))
        def same_name(self, name="lala"):
            nonlocal executions
            executions.append(name)

    ke_ = Person_KE()
    ke_.reset()
    ke_.declare(Person(name="NotAName", surname='surname'))
    ke_.declare(Person(name='name', surname="NotAName"))
    ke_.run()
    assert executions == ["NotAName"]


def test_matching_captured_same_facts_AND():
    """
    CLIPs behaves like this::

        (watch all)

        (deftemplate person
           (slot name)
           (slot surname)
        )

        (defrule test_clips
         (foo (name ?thename))
         (foo (surname ?thename))
        => (printout t "found " ?valor_1 crlf ))

        (deffacts thenames
            (person (name NotAName) (surname NotAName))
            (person (name name) (surname NotAName))
        )

        (reset)
        (run)

    Result:

        FIRE    1 test_clips: f-1,f-2

    """
    from experta import Rule
    from experta import Fact, L, W
    from experta.engine import KnowledgeEngine

    class Person(Fact):
        pass

    executions = []

    class Person_KE(KnowledgeEngine):
        @Rule(Person(name=W("name"), surname=W('name')))
        def same_name(self, name):
            nonlocal executions
            executions.append(name)

    ke_ = Person_KE()
    ke_.reset()
    ke_.declare(Person(name='NotAName', surname="NotAName"))
    ke_.declare(Person(name='name', surname="NotAName"))
    ke_.run()
    assert executions == ["NotAName"]


def test_matching_captured_different_facts_NOT_positive():
    """
    Declaring a NOT() using C/V should be a factlist-wide
    comparision.

    Positive test (returning activation because there were
    NO matches (the NOT is therefore executed).
    """
    from experta import Rule, NOT
    from experta import Fact, L, W
    from experta.engine import KnowledgeEngine

    class Person(Fact):
        pass

    executions = []

    class Person_KE(KnowledgeEngine):
        @Rule(Person(name=W("name")),
              NOT(Person(surname=W('name'))))
        def same_name(self, name):
            nonlocal executions
            executions.append(name)

    ke_ = Person_KE()
    ke_.reset()
    ke_.declare(Person(name='name', surname="NotAName"))
    ke_.run()
    assert executions == ["name"]


def test_matching_captured_different_facts_NOT_negative():
    """
    Declaring a NOT() using C/V should be a factlist-wide
    comparision.

    Negative test (returning no activation because there were
    matches (the NOT is therefore not executed).
    """
    from experta import Rule, NOT
    from experta import Fact, W, L
    from experta.engine import KnowledgeEngine

    class Person(Fact):
        pass

    executions = []

    class Person_KE(KnowledgeEngine):
        @Rule(Person(name=W("name")),
              NOT(Person(surname=W('name'))))
        def same_name(self, name):
            nonlocal executions
            executions.append(name)

    ke_ = Person_KE()
    ke_.reset()
    ke_.declare(Person(name='name', surname="NotAName"))
    ke_.declare(Person(name='name', surname="name"))
    ke_.run()
    assert executions == []


def test_and_negated_variable__bad_definition():
    from experta import Rule, NOT
    from experta import Fact, W
    from experta.engine import KnowledgeEngine

    class Person(Fact):
        pass

    executions = []

    class Person_KE(KnowledgeEngine):
        @Rule(Person(age=~W('age')),
              Person(age=W('age')))
        def same_name(self, age):
            nonlocal executions
            executions.append(age)

    ke_ = Person_KE()
    ke_.reset()

    with pytest.raises(RuntimeError):
        ke_.declare(Person(age=15))


def test_and_negated_variable__positive_match():
    from experta import Rule, NOT
    from experta import Fact, W
    from experta.engine import KnowledgeEngine

    class Person(Fact):
        pass

    executions = []

    class Person_KE(KnowledgeEngine):
        @Rule(Person(age=W('age')),
              Person(age=~W('age')))
        def same_name(self, age):
            nonlocal executions
            executions.append(age)

    ke_ = Person_KE()
    ke_.reset()
    ke_.declare(Person(name="name1", age=18))
    ke_.declare(Person(name="name2", age=19))
    ke_.run()
    assert set(executions) == {18, 19}


def test_and_negated_variable__negative_match():
    from experta import Rule, NOT
    from experta import Fact, W
    from experta.engine import KnowledgeEngine

    class Person(Fact):
        pass

    executions = []

    class Person_KE(KnowledgeEngine):
        @Rule(Person(age=W('age')),
              Person(age=~W("age")))
        def same_name(self, age):
            nonlocal executions
            executions.append(age)

    ke_ = Person_KE()
    ke_.reset()
    ke_.declare(Person(name="name1", age=18))
    ke_.declare(Person(name="name2", age=18))
    ke_.run()
    assert executions == []


def test_not_aggregation():
    from experta import Rule, NOT, AND
    from experta import Fact, W
    from experta.engine import KnowledgeEngine

    class Person(Fact):
        pass

    class ConflictResolver(Fact):
        pass

    executions = []

    class Person_KE(KnowledgeEngine):
        @Rule(NOT(ConflictResolver(resolved=True)),
              AND(Person(age=W('age')),
                  Person(age=~W("age"))))
        def same_name(self, age):
            nonlocal executions
            executions.append(age)

    ke_ = Person_KE()
    ke_.reset()
    ke_.declare(Person(name="name1", age=18))
    ke_.declare(Person(name='name2', age=19))
    ke_.declare(ConflictResolver(resolved=True))
    ke_.run()
    assert executions == []

    executions = []
    ke_ = Person_KE()
    ke_.reset()
    ke_.declare(Person(name="name1", age=18))
    ke_.declare(Person(name='name2', age=19))
    ke_.run()
    assert set(executions) == {18, 19}

    executions = []
    ke_ = Person_KE()
    ke_.reset()
    ke_.declare(Person(name="name1", age=18))
    ke_.declare(Person(name="name2", age=18))
    ke_.run()
    assert executions == []

    ke_ = Person_KE()
    ke_.reset()
    ke_.declare(Person(name="name1", age=18))
    ke_.declare(Person(name="name2", age=18))
    ke_.declare(ConflictResolver(resolved=True))
    ke_.run()
    assert executions == []


def test_declare_raises_typeerror_if_conditionalelement_found():
    from experta import KnowledgeEngine, L, W, P, Fact

    ke = KnowledgeEngine()

    with pytest.raises(TypeError):
        ke.declare(Fact(L(1)))

    with pytest.raises(TypeError):
        ke.declare(Fact(W()))

    with pytest.raises(TypeError):
        ke.declare(Fact(P(lambda _: True)))

    with pytest.raises(TypeError):
        ke.declare(Fact(~L(1)))

    with pytest.raises(TypeError):
        ke.declare(Fact(L(1) | L(2)))

    with pytest.raises(TypeError):
        ke.declare(Fact(L(1) & L(2)))


def test_retract_while_not_running_remove_activations():
    from experta import KnowledgeEngine, Rule

    class KE(KnowledgeEngine):
        @Rule()
        def r1(self):
            pass

    ke = KE()
    ke.reset()
    assert len(ke.agenda.activations) == 1
    ke.retract(0)
    assert len(ke.agenda.activations) == 0


def test_halt_stops_execution():
    from experta import KnowledgeEngine, Rule

    class KE(KnowledgeEngine):
        @Rule(salience=1)
        def runfirst(self):
            self.halt()

        @Rule()
        def runsecond(self):
            assert False

    ke = KE()
    ke.reset()
    ke.run()


def test_matcher_must_be_Matcher():
    from experta import KnowledgeEngine

    class KE(KnowledgeEngine):
        __matcher__ = None

    with pytest.raises(TypeError):
        KE()


def test_strategy_must_be_Strategy():
    from experta import KnowledgeEngine

    class KE(KnowledgeEngine):
        __strategy__ = False

    with pytest.raises(TypeError):
        KE()


def test_modify_retracts_and_declare():
    from experta import KnowledgeEngine, Fact

    ke = KnowledgeEngine()

    f1 = ke.declare(Fact())
    assert len(ke.facts) == 1

    f2 = ke.modify(f1, _0='test_pos', key='test_key')
    assert f1 != f2
    assert len(ke.facts) == 1
    assert f2.__factid__ in ke.facts
    assert f2[0] == 'test_pos'
    assert f2['key'] == 'test_key'


def test_duplicate_declare():
    from experta import KnowledgeEngine, Fact

    ke = KnowledgeEngine()

    f1 = ke.declare(Fact(color='red'))
    assert len(ke.facts) == 1

    f2 = ke.duplicate(f1, color='yellow', blink=True)
    assert len(ke.facts) == 2
    assert f2 is not f1
    assert f2['color'] == 'yellow'
    assert f2['blink']


def test_reset_kwargs_are_passed_to_deffacts_named():
    from experta import KnowledgeEngine, DefFacts, Fact

    passed = False

    class KE(KnowledgeEngine):
        @DefFacts()
        def init(self, arg):
            nonlocal passed
            passed = arg
            yield Fact()

    ke = KE()
    ke.reset(arg=True)
    assert passed is True


def test_reset_kwargs_are_passed_to_deffacts_kwargs():
    from experta import KnowledgeEngine, DefFacts, Fact

    passed = False

    class KE(KnowledgeEngine):
        @DefFacts()
        def init(self, **kwargs):
            nonlocal passed
            passed = kwargs
            yield Fact()

    ke = KE()
    ke.reset(arg=True)
    assert passed == {"arg": True}


def test_reset_kwargs_are_passed_to_deffacts_mixed():
    from experta import KnowledgeEngine, DefFacts, Fact

    passed = False

    class KE(KnowledgeEngine):
        @DefFacts()
        def init(self, arg0, **kwargs):
            nonlocal passed
            passed = (arg0, kwargs)
            yield Fact()

    ke = KE()
    ke.reset(arg0=0, arg1=1)
    assert passed == (0, {"arg1": True})


def test_reset_kwargs_are_passed_to_multiple_deffacts():
    from experta import KnowledgeEngine, DefFacts, Fact

    passed = set()

    class KE(KnowledgeEngine):
        @DefFacts()
        def init0(self, arg0):
            nonlocal passed
            passed.add(arg0)
            yield Fact()

        @DefFacts()
        def init1(self, arg1):
            nonlocal passed
            passed.add(arg1)
            yield Fact()

    ke = KE()
    ke.reset(arg0=0, arg1=1)
    assert passed == {0, 1}


def test_last_activation_is_executed():
    from experta import KnowledgeEngine, Rule, Fact, AS

    executed = list()
    first, second = object(), object()

    class KE(KnowledgeEngine):
        @Rule(
            Fact(s=True),
            Fact('A')
        )
        def second(self):
            executed.append(second)

        @Rule(
            AS.f << Fact(s=False),
            Fact('A')
        )
        def first(self, f):
            executed.append(first)
            self.modify(f, s=True)

    ke = KE()
    ke.reset()
    ke.declare(Fact('A'))
    ke.declare(Fact(s=False))
    ke.run()
    assert executed == [first, second]

def test_last_activation_is_executed_2():
    from experta import KnowledgeEngine, Rule, Fact, AS, DefFacts
    from experta import NOT, W, MATCH

    executed = None

    class KE(KnowledgeEngine):
        @DefFacts()
        def _initial_action(self):
            yield Fact(action="greet")

        @Rule(Fact(action='greet'),
              NOT(Fact(name=W())))
        def ask_name(self):
            self.declare(Fact(name="foo"))

        @Rule(Fact(action='greet'),
              NOT(Fact(location=W())))
        def ask_location(self):
            self.declare(Fact(location="bar"))

        @Rule(Fact(action='greet'),
              Fact(name=MATCH.name),
              Fact(location=MATCH.location))
        def greet(self, name, location):
            nonlocal executed
            executed = (name, location)

    ke = KE()
    ke.reset()
    ke.run()
    assert executed == ("foo", "bar")
