from card import CardGroup


class Player:
    def __init__(self, name):
        self.cards = []
        self.candidates = []
        self.need_analyze = True
        self.name = name

    def draw(self, group):
        if type(group) is list:
            self.cards += group
        else:
            self.cards.append(group)

    def discard(self, group):
        if type(group) is list:
            for c in group:
                self.cards.remove(c)
        else:
            self.cards.remove(group)

    def respond(self, last, cards):
        if self.need_analyze:
            self.candidates = CardGroup.analyze(self.cards)
        if last is None or self.name == last:
            # print "player %s cards:" % self.name
            # print self.cards
            print "player %s respond:" % self.name
            print self.candidates[0].cards
            self.discard(self.candidates[0].cards)
            self.need_analyze = True
            return self.name, self.candidates[0]
        else:
            for c in self.candidates:
                if c.type == cards.type and c.value > cards.value:
                    # print "player %s cards:" % self.name
                    # print self.cards
                    print "player %s respond:" % self.name
                    print c.cards
                    self.discard(c.cards)
                    self.need_analyze = True
                    return self.name, c
            self.need_analyze = False
            print "player %s pass!" % self.name
            return last, cards
