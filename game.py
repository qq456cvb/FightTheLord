from __future__ import print_function
from card import Card, CardGroup
import card
from player import Player
import numpy as np
import random
from collections import Counter


def counter_subset(list1, list2):
    c1, c2 = Counter(list1), Counter(list2)

    for (k, n) in c1.items():
        if n > c2[k]:
            return False
    return True


class Game:
    def __init__(self):
        self.deck = None
        self.players = []
        self.last_player = None
        self.last_cards = None
        self.lord_idx = -1
        self.history = []
        self.extra_cards = []
        self.action_space = card.get_action_space()
        self.next_turn = 0
        self.reset()

    def reset(self):
        self.deck = [c for c in Card.cards if c not in ['*', '$']] * 4
        self.deck = self.deck + ['*', '$']
        self.players = []
        self.last_player = None
        self.last_cards = None
        self.lord_idx = -1
        self.history = []
        self.extra_cards = []
        random.shuffle(self.deck)
        for i in range(3):
            self.players.append(Player(str(i)))

    def get_mask(self, i):
        mask = np.zeros_like(self.action_space)
        for j in range(mask.size):
            if counter_subset(self.action_space[j], self.players[i].cards):
                mask[j] = 1
        mask = mask.astype(bool)
        if self.last_player is not None:
            if self.last_player is not self.players[i]:
                for j in range(1, mask.size):
                    if mask[j] == 1 and not CardGroup.to_cardgroup(self.action_space[j]).bigger_than(self.last_cards):
                        mask[j] = False
            elif self.last_player is self.players[i]:
                mask[0] = False
        else:
            mask[0] = False
        return mask

    def prepare(self, lord_idx):
        self.lord_idx = lord_idx
        # three cards for the lord
        for i in range(3):
            self.extra_cards.append(self.deck[i])
        del self.deck[:3]

        print("extra cards: ", end='')
        print(self.extra_cards)
        # draw cards in turn
        for i in range(len(self.deck)):
            self.players[i % 3].draw(self.deck[i])
        self.deck = []

        # suppose the third player is the lord
        self.players[lord_idx].draw(self.extra_cards)
        self.players[lord_idx].is_lord = True

        for p in self.players:
            p.cards = sorted(p.cards, key=lambda k: Card.cards_to_value[k])

        self.next_turn = (lord_idx + 3) % 3
        for i in range(lord_idx, lord_idx + 3):
            idx = i % 3
            if self.players[idx].trainable:
                self.next_turn = idx
                break
            else:
                self.last_player, self.last_cards, passed = self.players[idx].respond(self.last_player, self.last_cards,
                                                                                      self.players[(idx - 1) % 3],
                                                                                      self.players[(idx + 1) % 3])
                self.log(idx, self.last_cards.cards, passed)

    def run(self):
        over = False
        winner = None
        while not over:
            # raw_input("Press Enter to continue...")
            over = False
            for i in range(3):
                i = (self.next_turn + i) % 3
                self.last_player, self.last_cards, passed = self.players[i].respond(self.last_player, self.last_cards,
                                                                                    self.players[(i - 1) % 3],
                                                                                    self.players[(i + 1) % 3])
                self.log(i, self.last_cards.cards, passed)
                self.history += self.last_cards.cards
                if not self.players[i].cards:
                    # winner = self.players[i].name
                    winner = i
                    over = True
                    break
        print("winner is player %s" % winner)
        print('....................................')
        return winner

    def check_winner(self):
        for i in range(3):
            if not self.players[i].cards:
                return i
        return None

    def log(self, i, cards, passed):
        if passed:
            print("player %d passed" % i)
        else:
            print("player %d respond:" % i, end='')
            print(cards)

    def step(self, i, a, single_step=False):
        if a != 0:
            self.players[i].discard(self.action_space[a])
            self.last_player = self.players[i]
            assert self.players[i] is self.last_player
            self.last_cards = CardGroup.to_cardgroup(self.action_space[a])
            self.history += self.last_cards.cards
            self.log(i, self.last_cards.cards, False)
            if not self.players[i].cards:
                return 2 if self.players[i].is_lord else 1, True
        else:
            self.log(i, [], True)
        if not single_step:
            ai = 0
            for k in range(i + 1, i + 3):
                ai = k % 3
                if self.players[ai].trainable:
                    break
                if not self.players[ai].cards:
                    # TODO: add coordination rewards
                    return -1, True
                self.last_player, self.last_cards, passed = self.players[ai].respond(self.last_player, self.last_cards,
                                                                             self.players[(ai - 1) % 3],
                                                                             self.players[(ai + 1) % 3])
                self.log(ai, self.last_cards.cards, passed)
                if not passed:
                    self.history += self.last_cards.cards
            self.next_turn = ai % 3
        else:
            self.next_turn = (self.next_turn + 1) % 3
        return 0, False

    def get_state(self, i):
        return np.hstack((Card.to_onehot(self.history),
                          Card.to_onehot(self.extra_cards),
                          Card.to_onehot(self.players[i].cards)))

if __name__ == '__main__':
    game = Game()
    cnt = 0
    total = 100
    for i in range(total):
        game.reset()
        game.players[2].is_human = True
        game.prepare(2)
        winner = game.run()
        if winner == 0:
            cnt += 1

    print("Lord winning rate: %f" % (cnt / float(total)))
