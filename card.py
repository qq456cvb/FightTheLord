from collections import Counter
import itertools

class Card:
    cards = ['3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A', '2', '*', '$']
    cards_to_value = dict(zip(cards, range(len(cards))))
    value_to_cards = {(v, c) for (c, v) in cards_to_value.iteritems()}

    def __init__(self):
        pass

    @staticmethod
    def to_value(card):
        if type(card) is list:
            val = 0
            for c in card:
                val += Card.cards_to_value[c]
            return val
        else:
            return Card.cards_to_value[card]


class CardGroup:
    def __init__(self, cards, t, val):
        self.type = t
        self.cards = cards
        self.value = val

    def __len__(self):
        return len(self.cards)

    @staticmethod
    def isvalid(cards):
        return CardGroup.folks(cards) == 1

    @staticmethod
    def folks(cards):
        cand = CardGroup.analyze(cards)
        cnt = 10000
        spec = False
        for c in cand:
            if c.type == 'triple_seq' or c.type == 'triple+single' or \
                    c.type == 'triple+double' or c.type == 'quadric+singles' or \
                    c.type == 'quadric+doubles' or c.type == 'triple_seq+singles' or \
                    c.type == 'triple_seq+singles':
                spec = True
                remain = list(cards)
                for card in c.cards:
                    remain.remove(card)
                if CardGroup.folks(remain) + 1 < cnt:
                    cnt = CardGroup.folks(remain) + 1
        if not spec:
            cnt = len(cand)
        return cnt

    @staticmethod
    def analyze(cards):
        cards = list(cards)
        candidates = []

        counts = Counter(cards)
        if '*' in cards and '$' in cards:
            candidates.append((CardGroup(['*', '$'], 'bigbang', 10000)))
            cards.remove('*')
            cards.remove('$')

        quadrics = []
        # quadric
        for c in counts:
            if counts[c] == 4:
                quadrics.append(c)
                candidates.append(CardGroup([c] * 4, 'bomb', Card.to_value(c)))
                cards.remove(c)

        counts = Counter(cards)
        singles = [c for c in counts if counts[c] == 1]
        doubles = [c for c in counts if counts[c] == 2]
        triples = [c for c in counts if counts[c] == 3]

        singles.sort(key=lambda k: Card.cards_to_value[k])
        doubles.sort(key=lambda k: Card.cards_to_value[k])
        triples.sort(key=lambda k: Card.cards_to_value[k])

        # continuous sequence
        if len(singles) > 0:
            cnt = 1
            cand = [singles[0]]
            for i in range(1, len(singles)):
                if Card.to_value(singles[i]) >= Card.to_value('2'):
                    break
                if Card.to_value(singles[i]) == Card.to_value(cand[-1]) + 1:
                    cand.append(singles[i])
                    cnt += 1
                else:
                    if cnt >= 5:
                        candidates.append(CardGroup(cand, 'single_seq', Card.to_value(cand[-1])))
                        for c in cand:
                            cards.remove(c)
                    cand = [singles[i]]
                    cnt = 1
            if cnt >= 5:
                candidates.append(CardGroup(cand, 'single_seq', Card.to_value(cand[-1])))
                for c in cand:
                    cards.remove(c)

        if len(doubles) > 0:
            cnt = 1
            cand = [doubles[0]] * 2
            for i in range(1, len(doubles)):
                if Card.to_value(doubles[i]) >= Card.to_value('2'):
                    break
                if Card.to_value(doubles[i]) == Card.to_value(cand[-1]) + 1:
                    cand += [doubles[i]] * 2
                    cnt += 1
                else:
                    if cnt >= 3:
                        candidates.append(CardGroup(cand, 'double_seq', Card.to_value(cand[-1])))
                        for c in cand:
                            if c in cards:
                                cards.remove(c)
                    cand = [doubles[i]] * 2
                    cnt = 1
            if cnt >= 3:
                candidates.append(CardGroup(cand, 'double_seq', Card.to_value(cand[-1])))
                for c in cand:
                    if c in cards:
                        cards.remove(c)

        if len(triples) > 0:
            cnt = 1
            cand = [triples[0]] * 3
            for i in range(1, len(triples)):
                if Card.to_value(triples[i]) >= Card.to_value('2'):
                    break
                if Card.to_value(triples[i]) == Card.to_value(cand[-1]) + 1:
                    cand += [triples[i]] * 3
                    cnt += 1
                else:
                    if cnt >= 2:
                        candidates.append(CardGroup(cand, 'triple_seq', Card.to_value(cand[-1])))
                        for c in cand:
                            if c in cards:
                                cards.remove(c)
                    cand = [triples[i]] * 3
                    cnt = 1
            if cnt >= 2:
                candidates.append(CardGroup(cand, 'triple_seq', Card.to_value(cand[-1])))
                for c in cand:
                    if c in cards:
                        cards.remove(c)

        for t in triples:
            candidates.append(CardGroup([t] * 3, 'triple', Card.to_value(t)))

        counts = Counter(cards)
        singles = [c for c in counts if counts[c] == 1]
        doubles = [c for c in counts if counts[c] == 2]

        # single
        for s in singles:
            candidates.append(CardGroup([s], 'single', Card.to_value(s)))

        # double
        for d in doubles:
            candidates.append(CardGroup([d] * 2, 'double', Card.to_value(d)))

        # 3 + 1, 3 + 2
        for c in triples:
            triple = [c] * 3
            for s in singles:
                if s not in triple:
                    candidates.append(CardGroup(triple + [s], 'triple+single',
                                                Card.to_value(c) * 1000 + Card.to_value(s)))
            for d in doubles:
                if d not in triple:
                    candidates.append(CardGroup(triple + [d] * 2, 'triple+double',
                                                Card.to_value(c) * 1000 + Card.to_value(d)))

        # 4 + 2
        for c in quadrics:
            for extra in list(itertools.combinations(singles, 2)):
                candidates.append(CardGroup([c] * 4 + list(extra), 'quadric+singles',
                                            Card.to_value(c) * 1000 + Card.to_value(list(extra))))
            for extra in list(itertools.combinations(doubles, 2)):
                candidates.append(CardGroup([c] * 4 + list(extra), 'quadric+doubles',
                                            Card.to_value(c) * 1000 + Card.to_value(list(extra))))
        # 3 * n + n, 3 * n + 2 * n
        triple_seq = [c.cards for c in candidates if c.type == 'triple_seq']
        for cand in triple_seq:
            cnt = len(cand) / 3
            for extra in list(itertools.combinations(singles, cnt)):
                candidates.append(
                    CardGroup(cand + list(extra), 'triple_seq+singles',
                              Card.to_value(cand[-1]) * 1000 + Card.to_value(list(extra))))
            for extra in list(itertools.combinations(doubles, cnt)):
                candidates.append(
                    CardGroup(cand + list(extra), 'triple_seq+doubles',
                              Card.to_value(cand[-1]) * 1000 + Card.to_value(list(extra))))

        importance = ['single', 'double', 'double_seq', 'single_seq', 'triple+single',
                      'triple+double', 'triple_seq+singles', 'triple_seq+doubles',
                      'triple_seq', 'triple', 'quadric+singles', 'quadric+doubles',
                      'bomb', 'bigbang']
        candidates.sort(cmp=lambda x, y: importance.index(x.type) - importance.index(y.type)
                        if importance.index(x.type) != importance.index(y.type) else x.value - y.value)
        # for c in candidates:
        #     print c.cards
        return candidates

if __name__ == '__main__':
    CardGroup.analyze(['3', '3', '3', '4', '4', '4', '10', 'J', 'Q', 'A', 'A', '2', '2', '*', '$'])
