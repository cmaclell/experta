from experta import *
import inspect

class Maximum(KnowledgeEngine):
    @Rule(NOT(Fact(max=W())))
    def init(self):
        self.declare(Fact(max=0))

    @Rule(Fact(val=MATCH.val),
          AS.m << Fact(max=MATCH.max),
          TEST(True))
    def compute_max(self, m, val):
        self.modify(m, max=val)

    @Rule(AS.v << Fact(val=MATCH.val),
          Fact(max=MATCH.max),
          TEST(lambda max, val: val <= max))
    def remove_val(self, v):
        self.retract(v)

    @Rule(AS.v << Fact(max=W()),
          NOT(Fact(val=W())))
    def print_max(self, v):
        print("Max:", v['max'])



import random
import inspect

if __name__ == "__main__":
    ke = Maximum()
    a = ke.remove_val._wrapped
    b = ke.print_max._wrapped
    ass = inspect.getsource(a)
    bs = inspect.getsource(b)
    print(ass)
    print("___")
    print(bs)
    # x = get_rule_binding(ke.kill_rule)

