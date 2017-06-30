from card import CardGroup, Card


class Player:
    def __init__(self, name):
        self.cards = []
        self.candidates = []
        self.need_analyze = True
        self.name = name
        self.is_lord = False

    def draw(self, group):
        self.need_analyze = True
        if type(group) is list:
            self.cards += group
        else:
            self.cards.append(group)

    def discard(self, group):
        self.need_analyze = True
        if type(group) is list:
            for c in group:
                self.cards.remove(c)
        else:
            self.cards.remove(group)

    def respond(self, last_player, cards, before_player, next_player):
        if self.need_analyze:
            self.candidates = CardGroup.analyze(self.cards)

        self.need_analyze = False
        if last_player is None or self == last_player:
            if CardGroup.folks(self.cards) == 2:
                self.discard(self.candidates[-1].cards)
                return self, self.candidates[-1]
            elif not next_player.is_lord and len(next_player.cards) == 1:
                for group in self.candidates:
                    if group.type == 'single':
                        self.discard(group.cards)
                        return self, group
                self.discard(self.candidates[0].cards)
                return self, self.candidates[0]
            elif next_player.is_lord and len(next_player.cards) == 1:
                for group in self.candidates:
                    if group.type != 'single':
                        self.discard(group.cards)
                        return self, group
                self.discard(self.candidates[-1].cards)
                return self, self.candidates[-1]
            else:
                for group in self.candidates:
                    if group.type != 'single' or Card.to_value(group.cards[0]) < Card.to_value('A'):
                        self.discard(group.cards)
                        return self, group
                self.discard(self.candidates[0].cards)
                return self, self.candidates[0]
            # print "player %s cards:" % self.name
            # print self.cards
            # print "player %s respond:" % self.name
            # print self.candidates[0].cards
            # self.discard(self.candidates[0].cards)
            # return self.name, self.candidates[0]
        elif not last_player.is_lord:
            if CardGroup.folks(self.cards) <= 2:
                for c in self.candidates:
                    if (c.type == cards.type and c.value > cards.value) or c.type == 'bomb' or c.type == 'bigbang':
                        # print "player %s cards:" % self.name
                        # print self.cards
                        # print "player %s respond:" % self.name
                        # print c.cards
                        if c.type == 'bomb' and cards.type == 'bomb' and cards.value > c.value:
                            continue
                        self.discard(c.cards)
                        return self, c
                return last_player, cards
            elif before_player.is_lord and last_player != before_player.name:
                return last_player, cards
            else:
                for c in self.candidates:
                    if c.type == cards.type and c.value > cards.value \
                            and Card.to_value(c.cards[0]) < Card.to_value('A') \
                            and cards.type != 'bomb':
                        self.discard(c.cards)
                        return self, c
                return last_player, cards
        else:
            for c in self.candidates:
                if c.type == cards.type and c.value > cards.value:
                    self.discard(c.cards)
                    return self, c
            # use bomb
            for c in self.candidates:
                if c.type == 'bomb' or c.type == 'bigbang':
                    if c.type == 'bomb' and cards.type == 'bomb' and cards.value > c.value:
                        continue
                    self.discard(c.cards)
                    return self, c
            return last_player, cards
