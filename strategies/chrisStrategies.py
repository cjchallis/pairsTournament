from __future__ import division
from copy import copy
from math import log

class FoldLowWithHigh:
    def __init__(self, fold, hand):
        ''' Strategy that folds when 'fold' is available if 'hand' or higher is in hand'''
        self.fold = fold
        self.hand = hand

    def play(self, info):
        # get best fold as tuple (playerIndex, card)
        best = info.bestFold(self.player)
        # get current hand
        stack = self.player.stack
        if best[1] <= self.fold and max(stack) >= self.hand:
            return best
        return "Hit"

class Expectation3:
    '''
    Determines optimal play by computing the expected points per turn
    until next points are earned.
    '''
    def __init__(self, tm = 5, high = 10, burn = 5):
        self.TURN_MAX = tm
        self.cards = tuple(range(1, high + 1))
        self.burn = burn

    def play(self, info):
        self.discards = info.discards
        deck = info.deck
        hand = tuple(self.player.stack)
        fold = info.bestFold(self.player)
        if(fold[1] <= 2):
            return fold
        play_to = max(11, 60 / info.noPlayers + 1)
        high_card = max(hand) if hand else 0
        scores = []
        for i in range(info.noPlayers):
            scores.append(info.players[i].getScore())
        if play_to - max(scores) < 6 and high_card + self.player.getScore() >= play_to:
            return fold
        ev_hit = self._turn(hand, deck, 1)

        if fold[1] / 2 < ev_hit:
             return fold
        return ev_hit

    def _p_deal(self, c, deck):
        return deck.count(c) / len(deck)

    def _p_fold(self, c, deck):
        return self._p_deal(c, deck)

    def _hit(self, hand, deck, trn):
        return sum([self._p_deal(c, deck) * c for c in hand]) / (trn+1)

    def _fold(self, ev_hit, deck, trn):
        prob = sum([self._p_fold(c, deck) for c in self.cards if c < ev_hit])
        ev = 0
        if prob > 0:
            ev = sum([self._p_fold(c, deck) * c for c in self.cards if c < ev_hit]) / prob / (trn+1)
        return (prob, ev)

    def _reshuffle(self, deck):
        return self.discards + deck

    def _turn(self, hand, deck, trn):
        ev_hit = self._hit(hand, deck, trn)
        if trn < self.TURN_MAX:
            for c in self.cards:
                if c not in hand and c in deck:
                    d = copy(deck)
                    d.remove(c)
                    if len(d) == self.burn:
                        d = self._reshuffle(d)
                    ev_hit += self._turn(hand + tuple([c]), d, trn+1) * self._p_deal(c, deck)

        if trn == 1:
            return ev_hit
        f = self._fold(ev_hit, deck, trn)
        p_fold = f[0]
        ev_fold = f[1]
        return p_fold * ev_fold + (1-p_fold) * ev_hit

class Heuristic:
    '''
    Determines optimal play according to 4 simple parameters.
    '''
    def __init__(self, ratio = 2.5, near_death = 3, always = 2, diff = 3):
        self.ratio = ratio
        self.nd = near_death
        self.always = always
        self.diff = diff

    def play(self, info):
        hand = self.player.stack
        fold = info.bestFold(self.player)
        if(fold[1] <= self.always):
            return fold
        if(sum(hand) / fold[1] > self.ratio and max(hand) - fold[1] >= self.diff):
            return fold
        play_to = max(11, 60 / info.noPlayers + 1)
        scores = []
        for i in range(info.noPlayers):
            scores.append(info.players[i].getScore())
        if play_to - max(scores) <= self.nd and max(hand) + self.player.getScore() >= play_to:
            return fold
        return "hit"

class SmartRatio:
    '''
    Determines optimal play with simple ratio intended to approximate
    Expectation with a full deck.
    '''
    def __init__(self, start = 1, inc = 1, near_death = 6, always = 2):
        self.start = start
        self.inc = inc
        self.nd = near_death
        self.always = always

    def play(self, info):
        hand = self.player.stack
        fold = info.bestFold(self.player)
        # cards always fold for
        if(fold[1] <= self.always):
            return fold
        play_to = max(11, 60 / info.noPlayers + 1)
        # when to start 'end-game' folding
        scores = []
        for i in range(info.noPlayers):
            scores.append(info.players[i].getScore())
        if play_to - max(scores) <= self.nd and max(hand) + self.player.getScore() >= play_to:
            return fold
        # general fold rule
        if sum(hand) / fold[1] >= (self.start + self.inc*len(hand)):
            return fold
        return "hit"

class Interactive:
    '''Allows interactive play with bots.'''

    def play(self, info):
        self._print_state(info)
        choice = eval(str(input('Your play?')))
        return choice

    def _print_state(self, info):
        for p in info.players:
            print('Player %d:\tstack: %s' % (p._index, str(p.stack)))
            print('\t\tpoints: %d' % (p.getScore()))
        print('You:\tstack:%s' % (str(self.player.stack)))
        print('\tpoints: %d' % (self.player.getScore()))


class PureExp:
    '''
    Initial standard bot. Decides only based on expected points now 
    from hit vs available fold.
    '''
    def __init__(self, mult, nd):
        self.mult = mult
        self.nd = nd

    def play(self, info):
        hand = self.player.stack
        fold = info.bestFold(self.player)
        play_to = max(60 / len(info.players) + 1, 11)
        scores = [p.getScore() for p in info.players]
        if (play_to - max(scores) <= self.nd and max(hand) + 
            self.player.getScore() >= play_to):
            return fold
        if fold[1] < self.mult * self._ev_hit(self.player.stack, info.deck):
            return fold
        return "hit"

    def _ev_hit(self, hand, deck):
        return sum([self._p_deal(c, deck) * c for c in hand])

    def _p_deal(self, c, deck):
        return deck.count(c) / len(deck)


class Weights:

    def __init__(self, mult):
        self.mult = mult
        self.pe = PureExp(0.9, 8)
        
    def _log_weight(self, k):
        return self.mult * log(max(12-k,1)) + 1

    def play(self, info):
        self.pe.player = self.player
        fold = info.bestFold(self.player)
        me = self.player._index
        p_lose_fold = self._p_lose_new(fold[1], info, me) 
        p_lose_hit = p_pair = 0
        for c in self.player.stack:
            p_pair += self._p_deal(c, info.deck)
            p_lose_hit += (self._p_deal(c, info.deck) * 
                           self._p_lose_new(c, info, me))
        p_nxt = 1 - p_pair
        n = len(info.players)
        for i in range(n):
            j = (me + i + 1) % n
            # for now assume other players always hit
            p_pair = 0
            for c in info.players[j].stack:
                p_pair += self._p_deal(c, info.deck)
                p_lose_hit += (p_nxt * self._p_deal(c, info.deck) *
                               self._p_lose_new(c, info, j))
            p_nxt *= 1 - p_pair
        # assumption for probability of losing if reach next turn
        nxt_fold = min(fold[1], self._exp_fold(info.deck, n-1))
        p_lose_hit += p_nxt * self._p_lose_new(nxt_fold, info, me)
        #print("Lose from hit: " + str(p_lose_hit))
        #print("Lose from fold: " + str(p_lose_fold))
        if abs(p_lose_fold - p_lose_hit) < 0.05:
            return self.pe.play(info)
        if p_lose_fold < p_lose_hit:
            return fold
        return "hit"

    def _p_deal(self, c, deck):
        return deck.count(c) / len(deck)

    def _exp_fold(self, deck, trials):
        pmf = [self._p_deal(c, deck) for c in range(1, 11)]
        cdf = [sum(pmf[0:i]) for i in range(10)]
        min_cdf = [1 - (1-c) ** trials for c in cdf]
        min_pmf = [min_cdf[0]] + [min_cdf[i+1] - min_cdf[i] for i in range(9)]
        return sum(min_pmf[c-1] * c for c in range(1,11))

    def _p_lose_new(self, c, info, idx):
        max_sc = max(11, 60 / len(info.players) + 1)
        scores = [p.getScore() for p in info.players]
        scores[idx] += c
        weights = [self._log_weight(max_sc - s) for s in scores]
        return weights[self.player._index] / sum(weights)
       

class HitMe:

    def play(self, info):
        return "hit"
