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


class KillEngine2(KnowledgeEngine):
    @DefFacts()
    def first(self):
        yield Depressed("JOHN")
        yield Gun("OBJ1")

    @Rule(
        Depressed(MATCH.w))
    def hate_rule(self, w):
        print("declaring hate")
        self.declare(Hate(w, w))


ke = KillEngine2()
ke.reset()
ke.run()
print(ke.facts)
ke.retract(ke.facts[1])
print("___")
ke.run()
print(ke.facts)

