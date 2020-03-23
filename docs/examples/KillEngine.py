from experta import *


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
    @DefFacts()
    def first(self):
        yield Depressed("JOHN")
        yield Buy("JOHN", "OBJ1")
        yield Gun("OBJ1")

    @Rule(
        AS.fact1 << Hate(MATCH.a, MATCH.b), Possess(MATCH.a, MATCH.c), Weapon(MATCH.c))
    def kill_rule(self, a, b, fact1):
        print("FACT 1: ", fact1)
        #print(a + ' kills ' + b)
        self.declare(Kill(a, b))

    @Rule(
        Depressed(MATCH.w))
    def hate_rule(self, w):
        #print(w + ' hates ' + w)
        self.declare(Hate(w, w))

    @Rule(
        Buy(MATCH.u, MATCH.v),
        TEST(lambda u: True))
    def possess_rule(self, u, v):
        #print(u + ' possesses ' + v)
        self.declare(Possess(u, v))

    @Rule(
        Gun(MATCH.z),
        TEST(lambda z: True))
    def weapon_rule(self, z):
        #print(z + " is a weapon")
        self.declare(Weapon(z))

class KillEngineEmpty(KnowledgeEngine):
    @DefFacts()
    def first(self):
        yield Depressed("JOHN")
        yield Buy("JOHN", "OBJ1")
        yield Gun("OBJ1")

from apprentice.explain.util import rename_rule_unique

if __name__=="__main__":
    from apprentice.explain.explanation import Explanation
    from apprentice.working_memory import ExpertaWorkingMemory

    #new_wm = ExpertaWorkingMemory(KillEngineEmpty())
    cf = KillEngine()
    cf.reset()
    cf.run(10)
    # facts = cf.facts
    # kill_fact = cf.facts[7]
    # x = Explanation(kill_fact)
    # print(x.general)
    # print(x.conditions)
    #
    # r = x.new_rule
    # new_wm.add_rule(r)
    # print(new_wm.ke.get_rules())
