import inspect

from KillEngine import KillEngine, KillEngineEmpty
from experta import W, Rule
from experta.unification import unify
from mini_lambda import is_mini_lambda_expr


def get_source_str(f):
    if is_mini_lambda_expr(f):
        return f.to_string()
    else:
        return inspect.getsource(f)


def get_condition_binding(condition):
    return [x.__bind__ for x in condition.values()]


def ordered_bindings(b):
    return tuple([t[1] for t in sorted(b.items(), key=lambda x: str(x[0]))])


class Explanation:
    def __init__(self, fact):
        self.rules = []
        self.conditions = []
        self.general = self.explain_fact(fact)
        self.rules = self.rules[::-1]  # order rules logically
        self.conditions = [f.copy(sub=self.general) for f in self.conditions]
        self.new_rule = self.compose()

    def compose(self):
        def test_rule(*args, **kwargs):
            print("test rule called with args: ", args, " and kwargs: ",
                  kwargs)

        # inject this ###########!#!! into ExpertaWorkingMemory
        func = test_rule

        """ compose a function using the generated explanation and 
        unification """
        r = Rule(*self.conditions)
        r.__call__(func)
        return r

    def get_rule_binding(self, rule):
        """ given an experta rule, returns """
        s = get_source_str(rule._wrapped)

        for l in s.split('\n'):
            if 'self.declare' in l:
                fs = l[l.find('(') + 1:-1]
        binding = {}

        sig = fs[fs.find('(') + 1:-1]
        for i, arg in enumerate(sig.split(',')):
            binding[i] = W(arg.strip())
            # todo: kwargs
        binding['__class__'] = fs[:fs.find('(')]
        return binding  # tuple(binding.values())

    def get_condition_binding(self, condition):
        binding = dict(condition)
        binding['__class__'] = condition.__class__.__name__
        return binding  # [condition.__class__.__name__] + list(
        # binding.values())

    def explain_fact(self, fact, general={}, root=True):

        print("explain_fact:::", locals())
        # because we are only building general substitution, only consider
        # facts who came from an activation i.e. rule
        if fact.__source__ is not None:

            # keep track of rules that need to be fired for composition
            self.rules.append(fact.__source__.rule)
            e1s = []
            for antecedent_fact in fact.__source__.facts:

                # antecedent fact came from another rule, so the backchain
                # must continue
                if antecedent_fact.__source__ is not None:
                    e1s.append((antecedent_fact,
                                tuple(self.get_rule_binding(
                                    antecedent_fact.__source__.rule).values(

                                ))))
                # antecedent fact is a terminal, so the condition of this
                # fact is the boundary condition
                else:
                    self.conditions.extend(fact.__source__.rule._args)

            # LHS of current rule, i.e. RHS of explanation tuple
            for conj in fact.__source__.rule._args:
                e2 = tuple(self.get_condition_binding(conj).values())

                for e1 in e1s:
                    # precheck that fact type matches
                    if e1[1][-1] == e2[-1]:
                        # ensure they unify, i.e. they are corresponding
                        # facts and conditions

                        u = unify(e1[1], e2, general)
                        if u is not None:
                            new_g = self.explain_fact(fact=e1[0],
                                                      general=general.update(
                                                          u),
                                                      root=False)
                            if new_g is not None:
                                general.update(new_g)

                            e1s.remove(e1)
                            break

        return general


if __name__ == "__main__":
    from apprentice.working_memory import ExpertaWorkingMemory

    new_wm = ExpertaWorkingMemory(KillEngineEmpty())
    cf = KillEngine()
    cf.reset()
    cf.run(10)
    facts = cf.facts
    kill_fact = cf.facts[7]
    x = Explanation(kill_fact)
    print(x.general)
    print(x.conditions)
    r = x.new_rule

    new_wm.add_rule(r)

    # new_wm.ke.run(10)
    print(new_wm.ke.get_rules())
    # print(new_wm.ke.facts)

    # frames = [ for f in cf.facts]
    # frame = kill_fact.__source__
    # r = frame.f_locals['self'].rule
