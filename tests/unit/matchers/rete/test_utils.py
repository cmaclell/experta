import pytest
from experta.matchers.rete import utils


def test_prepare_rule_is_dnf():
    from experta import Rule, NOT, AND, OR, Fact
    from experta.matchers.rete.dnf import dnf

    rule = Rule(AND(Fact(0), NOT(OR(Fact(1), Fact(2)))))(lambda:None)

    assert list(utils.prepare_rule(rule)) == [Fact(0),
                                              NOT(Fact(1)),
                                              NOT(Fact(2))]


def test_prepare_rule_empty():
    from experta import Rule, InitialFact

    rule = Rule()(lambda:None)

    assert list(utils.prepare_rule(rule)) == [InitialFact()]


def test_prepare_rule__rule_starting_with_not():
    from experta import Rule, InitialFact, NOT, Fact

    rule = Rule(NOT(Fact(1)))(lambda:None)

    assert list(utils.prepare_rule(rule)) == [InitialFact(), NOT(Fact(1))]


def test_prepare_rule__and_starting_with_not():
    from experta import Rule, InitialFact, NOT, Fact, OR, AND

    rule = Rule(OR(Fact(1), AND(NOT(Fact(2)), Fact(3))))(lambda:None)

    assert list(utils.prepare_rule(rule)) == [OR(Fact(1),
                                                 AND(InitialFact(),
                                                     NOT(Fact(2)),
                                                     Fact(3)))]

def test_prepare_rule__and_inside_rule():
    from experta import Rule, AND, Fact

    rule = Rule(AND(Fact(1), Fact(2)))(lambda:None)

    assert list(utils.prepare_rule(rule)) == [Fact(1), Fact(2)]


def test_prepare_rule__or_starting_with_not():
    from experta import Rule, InitialFact, NOT, Fact, OR, AND

    rule = Rule(OR(NOT(Fact(1)), NOT(Fact(2))))(lambda:None)

    assert list(utils.prepare_rule(rule)) == [OR(AND(InitialFact(),
                                                     NOT(Fact(1))),
                                                 AND(InitialFact(),
                                                     NOT(Fact(2))))]

def test_extract_facts():
    from experta import Rule, NOT, AND, OR, Fact

    rule = Rule(OR(AND(Fact(1), NOT(Fact(2))), Fact(3)))

    assert utils.extract_facts(rule) == {Fact(1), Fact(2), Fact(3)}


def test_illegal_CE():
    from experta import Rule, KnowledgeEngine
    from experta.conditionalelement import ConditionalElement

    class KE(KnowledgeEngine):
        @Rule(ConditionalElement())
        def r1():
            pass

    with pytest.raises(TypeError):
        KE()
