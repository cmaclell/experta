try:
    from experta import *
except ImportError:
    from pyknow import *

P = [[None, 2, None, 6, None, 8, None, None, None],
     [5, 8, None, None, None, 9, 7, None, None],
     [None, None, None, None, 4, None, None, None, None],
     [3, 7, None, None, None, None, 5, None, None],
     [6, None, None, None, None, None, None, None, 4],
     [None, None, 8, None, None, None, None, 1, 3],
     [None, None, None, None, 2, None, None, None, None],
     [None, None, 9, 8, None, None, None, 3, 6],
     [None, None, None, 3, None, 6, None, 9, None]]


class Possible(Fact):
    pass


class Solver(KnowledgeEngine):
    @DefFacts()
    def init_puzzle(self):
        for x, row in enumerate(P):
            for y, cell in enumerate(row):
                block = ((y // 3) * 3) + (x // 3)
                if cell is None:
                    yield Fact(value=None, y=y, x=x, block=block)
                    for i in range(1, 10):
                        yield Possible(value=i, y=y, x=x, block=block)
                else:
                    yield Fact(value=cell, y=y, x=x, block=block)


    @Rule(Fact(value=~L(None) & MATCH.v, y=MATCH.y),
          AS.p << Possible(value=MATCH.v, y=MATCH.y))
    def discarded_by_column(self, p):
        self.retract(p)

    @Rule(Fact(value=~L(None) & MATCH.v, x=MATCH.x),
          AS.p << Possible(value=MATCH.v, x=MATCH.x))
    def discarded_by_row(self, p):
        self.retract(p)

    @Rule(Fact(value=~L(None) & MATCH.v, block=MATCH.b),
          AS.p << Possible(value=MATCH.v, block=MATCH.b))
    def discarded_by_block(self, p):
        self.retract(p)

    @Rule(AS.cell << Fact(value=None, x=MATCH.x, y=MATCH.y, block=MATCH.b),
          Possible(value=MATCH.v, x=MATCH.x, y=MATCH.y, block=MATCH.b),
          NOT(Possible(value=~MATCH.v, x=MATCH.x, y=MATCH.y, block=MATCH.b)))
    def only_one_possible(self, cell, v):
        self.retract(cell)
        self.declare(Fact(value=v, x=cell['x'], y=cell['y'], block=cell['block']))

    @Rule(AS.cell << Fact(value=None, x=MATCH.x, y=MATCH.y, block=MATCH.b),
          Possible(value=MATCH.v, x=MATCH.x, y=MATCH.y, block=MATCH.b),
          NOT(Possible(value=MATCH.v, x=~MATCH.x, y=~MATCH.y, block=MATCH.b)))
    def unique_candidate_block(self, cell, v):
        self.retract(cell)
        self.declare(Fact(value=v, x=cell['x'], y=cell['y'], block=cell['block']))

    @Rule(AS.cell << Fact(value=None, x=MATCH.x, y=MATCH.y, block=MATCH.b),
          Possible(value=MATCH.v, x=MATCH.x, y=MATCH.y, block=MATCH.b),
          NOT(Possible(value=MATCH.v, x=~MATCH.x, y=MATCH.y, block=~MATCH.b)))
    def unique_candidate_col(self, cell, v):
        self.retract(cell)
        self.declare(Fact(value=v, x=cell['x'], y=cell['y'], block=cell['block']))

    @Rule(AS.cell << Fact(value=None, x=MATCH.x, y=MATCH.y, block=MATCH.b),
          Possible(value=MATCH.v, x=MATCH.x, y=MATCH.y, block=MATCH.b),
          NOT(Possible(value=MATCH.v, x=MATCH.x, y=~MATCH.y, block=~MATCH.b)))
    def unique_candidate_row(self, cell, v):
        self.retract(cell)
        self.declare(Fact(value=v, x=cell['x'], y=cell['y'], block=cell['block']))

    @Rule(Fact(value=~L(None) & MATCH.v, x=MATCH.x, y=MATCH.y, block=MATCH.b),
          AS.p << Possible(value=~MATCH.v, x=MATCH.x, y=MATCH.y, block=MATCH.b))
    def remove_other_candidates(self, p):
        self.retract(p)


watch('RULES', 'FACTS')
s = Solver()
s.reset()
s.run()
