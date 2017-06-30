from card import Card
from player import Player
import random


class Game:
    def __init__(self):
        self.deck = None
        self.players = []
        self.extra_cards = []
        self.reset()

    def reset(self):
        self.deck = [c for c in Card.cards if c not in ['*', '$']] * 4
        self.deck = self.deck + ['*', '$']
        self.players = []
        self.extra_cards = []
        random.shuffle(self.deck)

    def prepare(self, lord_idx):
        for i in xrange(3):
            self.players.append(Player(str(i)))

        # three cards for the lord
        for i in xrange(3):
            self.extra_cards.append(self.deck[i])
        del self.deck[:3]

        # draw cards in turn
        for i in xrange(len(self.deck)):
            self.players[i % 3].draw(self.deck[i])
        self.deck = []

        # suppose the third player is the lord
        self.players[lord_idx].draw(self.extra_cards)
        self.players[lord_idx].is_lord = True

        for p in self.players:
            p.cards = sorted(p.cards, key=lambda k: Card.cards_to_value[k])

    def run(self):
        last = None

        cards = []
        over = False
        winner = None
        while not over:
            # raw_input("Press Enter to continue...")
            over = False
            for i in xrange(3):
                last, cards = self.players[i].respond(last, cards,
                                                      self.players[(i - 1) % 3],
                                                      self.players[(i + 1) % 3])
                if not self.players[i].cards:
                    # winner = self.players[i].name
                    winner = i
                    over = True
                    break
        print "winner is player %s" % winner
        return winner

if __name__ == '__main__':
    game = Game()
    cnt = 0
    total = 100
    for i in xrange(total):
        game.reset()
        game.prepare(0)
        winner = game.run()
        if winner == 0:
            cnt += 1

    print "Lord winning rate: %f" % (cnt / float(total))
