# -*- coding: utf-8 -*-
"""
Created on Sat Jan 18 19:27:21 2020

@author: robert.sheline
"""

from experta import Fact, KnowledgeEngine, Rule, MATCH, TEST, DefFacts, AS


class Depressed(Fact):
    pass


class Hate(Fact):
    pass


class Buy(Fact):
    pass


class Possess(Fact):
    pass


class Gun(Fact):
    pass


class Weapon(Fact):
    pass


class Kill(Fact):
    pass


class KillEngine(KnowledgeEngine):
    fired = []

    @DefFacts()
    def first(self):
        yield Depressed("JOHN")
        yield Buy("JOHN", "OBJ1")
        yield Gun("OBJ1")

    @Rule(
        AS.fact1 << Hate(MATCH.a, MATCH.b),
        Possess(MATCH.a, MATCH.c),
        Weapon(MATCH.c),
        TEST(lambda a, b, c: True))
    def kill_rule(self, a, b, fact1):
        self.fired.append(('kill_rule', a, b))
        self.declare(Kill(a, b))

    @Rule(
        Depressed(MATCH.w),
        TEST(lambda w: w == "JOHN"))
    def hate_rule(self, w):
        self.fired.append(('hate_rule', w))
        self.declare(Hate(w, w))

    @Rule(
        Buy(MATCH.u, MATCH.v),
        TEST(lambda u: u == "JOHN"),
        TEST(lambda v: v == "OBJ1"))
    def possess_rule(self, u, v):
        self.fired.append(('possess_rule', u, v))
        self.declare(Possess(u, v))

    @Rule(
        Gun(MATCH.z),
        TEST(lambda z: True))
    def weapon_rule(self, z):
        self.fired.append(('weapon_rule', z))
        self.declare(Weapon(z))


class KillEngineEmpty(KnowledgeEngine):
    fired = []

    @DefFacts()
    def first(self):
        yield Depressed("JOHN")
        yield Buy("JOHN", "OBJ1")
        yield Gun("OBJ1")

class TestEngine(KnowledgeEngine):
    @Rule(
        AS.fact123 << Fact())

    def weapon_rule(self, fact123):
        print("test engine rule fire", fact123)

if __name__=="__main__":
    from apprentice.working_memory import ExpertaWorkingMemory
    from apprentice.working_memory.skills import fraction_skill_set

    from apprentice.agents.soartech_agent import SoarTechAgent
    import copy
    import dill as pickle

    # c = copy.deepcopy(fraction_skill_set['click_done'])
    prior_skills = [fraction_skill_set['click_done']]
    prior_skills = None
    # wm = ExpertaWorkingMemory(ke=KnowledgeEngine())
    # wm.add_skills(prior_skills)
    if prior_skills is None:
        prior_skills = {
            "click_done": True,
            "check": True,
            "equal": False,
            "update_answer": True,
            "update_convert": True,
            "add": True,
            "multiply": True,
        }

    wm = ExpertaWorkingMemory(ke=KnowledgeEngine())

    skill_map = fraction_skill_set
    prior_skills = [
        skill_map[s]
        for s, active in prior_skills.items()
        if active and s in skill_map
    ]
    wm.add_skills(prior_skills)

    c = copy.deepcopy(wm)


