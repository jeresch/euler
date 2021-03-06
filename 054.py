import functools


@functools.total_ordering
class Value:
    ordering = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
    faces = ['T', 'J', 'Q', 'K', 'A']

    def __init__(self, char):
        self.type = char

    def __eq__(self, other):
        return self.type == other.type

    def __lt__(self, other):
        return self.ordering.index(self.type) < self.ordering.index(other.type)

    def __str__(self):
        return self.type


@functools.total_ordering
class Card:
    suits = ['H', 'S', 'C', 'D']

    def __init__(self, the_string):
        self.suit = the_string[1]
        self.value = Value(the_string[0])

    def __eq__(self, other):
        return self.value == other.value

    def __lt__(self, other):
        return self.value < other.value

    def __str__(self):
        return str(self.value) + self.suit


class AmbiguousWinnerError(Exception):
    pass


class UnknownRankError(Exception):
    pass


@functools.total_ordering
class Hand:
    HIGH_CARD = 1
    ONE_PAIR = 2
    TWO_PAIRS = 3
    THREE_OF_KIND = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    FOUR_OF_KIND = 8
    STRAIGHT_FLUSH = 9
    ROYAL_FLUSH = 10

    def __init__(self, cards):
        self.cards: List[Card] = cards
        self.rank = self.calc_rank()

    def rank_name(self):
        if self.rank == self.HIGH_CARD:
            return "HIGH_CARD"
        elif self.rank == self.ONE_PAIR:
            return "ONE_PAIR"
        elif self.rank == self.TWO_PAIRS:
            return "TWO_PAIRS"
        elif self.rank == self.THREE_OF_KIND:
            return "THREE_OF_KIND"
        elif self.rank == self.STRAIGHT:
            return "STRAIGHT"
        elif self.rank == self.FLUSH:
            return "FLUSH"
        elif self.rank == self.FULL_HOUSE:
            return "FULL_HOUSE"
        elif self.rank == self.FOUR_OF_KIND:
            return "FOUR_OF_KIND"
        elif self.rank == self.STRAIGHT_FLUSH:
            return "STRAIGHT_FLUSH"
        elif self.rank == self.ROYAL_FLUSH:
            return "ROYAL_FLUSH"

        raise UnknownRankError("Shouldn't get here")

    def calc_rank(self):
        card_values = [card.value for card in self.cards]
        all_same_suit = self._all_same_suit()
        cards_consecutive = self._cards_consecutive()

        if all_same_suit and all(Value(face) in card_values for face in Value.faces):
            return self.ROYAL_FLUSH
        elif all_same_suit and cards_consecutive:
            return self.STRAIGHT_FLUSH
        elif self._have_n_of_same_type(4):
            return self.FOUR_OF_KIND
        elif self._have_n_of_same_type(3) and self._have_n_of_same_type(2):
            return self.FULL_HOUSE
        elif all_same_suit:
            return self.FLUSH
        elif cards_consecutive:
            return self.STRAIGHT
        elif self._have_n_of_same_type(3):
            return self.THREE_OF_KIND
        elif self._have_two_pairs():
            return self.TWO_PAIRS
        elif self._have_n_of_same_type(2):
            return self.ONE_PAIR
        else:
            return self.HIGH_CARD

    def group_by_type(self):
        res = {}
        for t in Value.ordering:
            res[t] = []
        for card in self.cards:
            t = card.value.type
            res[t].append(card)
        return res

    def __eq__(self, other):
        return False

    def __gt__(self, other):
        if self.rank > other.rank:
            return True
        elif self.rank < other.rank:
            return False

        my_grouped = self.group_by_type()
        other_grouped = other.group_by_type()

        if self.rank == self.ROYAL_FLUSH:
            raise AmbiguousWinnerError()
        elif self.rank == self.STRAIGHT_FLUSH:
            return max(self.cards) > max(other.cards)
        elif self.rank == self.FOUR_OF_KIND:
            my_four = [my_grouped[t] for t in Value.ordering if len(my_grouped[t]) == 4][0]
            their_four = [other_grouped[t] for t in Value.ordering if len(other_grouped[t]) == 4][0]
            return my_four[0] > their_four[0]
        elif self.rank == self.FULL_HOUSE:
            my_three = [my_grouped[t] for t in Value.ordering if len(my_grouped[t]) == 3][0]
            their_three = [other_grouped[t] for t in Value.ordering if len(other_grouped[t]) == 3][0]
            if my_three[0] > their_three[0]:
                return True
            elif my_three[0] < their_three[0]:
                return False

            my_two = [my_grouped[t] for t in Value.ordering if len(my_grouped[t]) == 2][0]
            their_two = [other_grouped[t] for t in Value.ordering if len(other_grouped[t]) == 2][0]
            return my_two[0] > their_two[0]
        elif self.rank == self.FLUSH:
            my_sorted = reversed(sorted(self.cards))
            their_sorted = reversed(sorted(self.cards))
            for mine, theirs in zip(my_sorted, their_sorted):
                if mine > theirs:
                    return True
                elif mine < theirs:
                    return False
            raise AmbiguousWinnerError()
        elif self.rank == self.STRAIGHT:
            my_sorted = reversed(sorted(self.cards))
            their_sorted = reversed(sorted(self.cards))
            return my_sorted[0] > their_sorted[0]
        elif self.rank == self.THREE_OF_KIND:
            my_three = [my_grouped[t] for t in Value.ordering if len(my_grouped[t]) == 3][0]
            their_three = [other_grouped[t] for t in Value.ordering if len(other_grouped[t]) == 3][0]
            if my_three[0] > their_three[0]:
                return True
            elif my_three[0] < their_three[0]:
                return False
            my_other_two = [my_grouped[t][0] for t in Value.ordering if len(my_grouped[t]) != 3]
            their_other_two = [other_grouped[t][0] for t in Value.ordering if len(other_grouped[t]) != 3]
            if max(my_other_two) > max(their_other_two):
                return True
            elif max(my_other_two) < max(their_other_two):
                return False
            if min(my_other_two) > min(their_other_two):
                return True
            elif min(my_other_two) < min(their_other_two):
                return False
            raise AmbiguousWinnerError()
        elif self.rank == self.TWO_PAIRS:
            my_pair_values = [my_grouped[t][0].value for t in Value.ordering if len(my_grouped[t]) == 2]
            their_pair_values = [other_grouped[t][0].value for t in Value.ordering if len(other_grouped[t]) == 2]
            if max(my_pair_values) > max(their_pair_values):
                return True
            elif max(my_pair_values) < max(their_pair_values):
                return False
            if min(my_pair_values) > min(their_pair_values):
                return True
            elif min(my_pair_values) < min(their_pair_values):
                return False

            my_fifth_value = [my_grouped[t][0].value for t in Value.ordering if len(my_grouped[t]) == 1][0]
            their_fifth_value = [other_grouped[t][0].value for t in Value.ordering if len(other_grouped[t]) == 1][0]
            if my_fifth_value > their_fifth_value:
                return True
            elif my_fifth_value < their_fifth_value:
                return False
            raise AmbiguousWinnerError()
        elif self.rank == self.ONE_PAIR:
            my_pair_value = [my_grouped[t][0].value for t in Value.ordering if len(my_grouped[t]) == 2][0]
            their_pair_value = [other_grouped[t][0].value for t in Value.ordering if len(other_grouped[t]) == 2][0]
            if my_pair_value > their_pair_value:
                return True
            elif my_pair_value < their_pair_value:
                return False
            my_other_values = reversed(sorted([my_grouped[t][0].value for t in Value.ordering if len(my_grouped[t]) == 1]))
            their_other_values = reversed(sorted([other_grouped[t][0].value for t in Value.ordering if len(other_grouped[t]) == 1]))
            for my_val, their_val in zip(my_other_values, their_other_values):
                if my_val > their_val:
                    return True
                elif my_val < their_val:
                    return False
            raise AmbiguousWinnerError()
        elif self.rank == self.HIGH_CARD:
            mine_sorted = sorted(self.cards, reverse=True)
            their_sorted = sorted(other.cards, reverse=True)
            for my_card, their_card in zip(mine_sorted, their_sorted):
                if my_card > their_card:
                    return True
                elif my_card < their_card:
                    return False
            raise AmbiguousWinnerError()

        raise UnknownRankError()

    def __str__(self):
        return " ".join(str(card) for card in self.cards)

    def _all_same_suit(self):
        return any(all(card.suit == suit for card in self.cards) for suit in Card.suits)

    def _cards_consecutive(self):
        card_types = [card.value.type for card in sorted(self.cards)]
        for i in range(1, len(self.cards)):
            if Value.ordering.index(card_types[i - 1]) + 1 != Value.ordering.index(card_types[i]):
                return False
        return True

    def _have_n_of_same_type(self, n):
        card_values = [card.value for card in self.cards]
        card_types = [val.type for val in card_values]
        return any(card_types.count(t) == n for t in Value.ordering)

    def _have_two_pairs(self):
        grouped = self.group_by_type()
        num_pairs = 0
        for t in grouped:
            if len(grouped[t]) == 2:
                num_pairs += 1
        return num_pairs == 2


player_1_wins = 0
with open('054_poker.txt', 'r') as f:
    for i, line in enumerate(f):
        cards = [Card(s) for s in line.split()]
        p1_hand = Hand(cards[:5])
        p2_hand = Hand(cards[5:])
        if p1_hand > p2_hand:
            player_1_wins += 1
        print("Line {}: P1[{}]({}) P2[{}]({}), Player 1 {}".format(
            i, p1_hand, p1_hand.rank_name(), p2_hand, p2_hand.rank_name(), "wins" if p1_hand > p2_hand else "loses"))

print(player_1_wins)
