import random
import itertools
from copy import copy

from pkg_resources import resource_listdir


CARDS = ['A', 'K', 'Q', 'J', '10', '9', '8', '7', '6', '5', '4', '3', '2']
COLORS = ['C', 'D', 'H', 'S']

DECK = [tup[0] + tup[1] for tup in itertools.product(CARDS, COLORS)]


class Player:

    def __init__(self, name, deck):
        self.name = name
        self.deck = deck
        self.down_deck = []
        self.card = None
        self.aces = self.get_number_of_aces()

    @property
    def is_empty(self):
        if self.deck:
            return False
        return True

    @property
    def lost(self):
        if len(self.deck + self.down_deck) == 0:
            return True
        return False


    def get_number_of_aces(self):
        return len([x for x in self.deck if x.startswith('A')])


    def get_card(self):
        if not self.is_empty:
            self.card = self.deck.pop(0)
        else:
            self.card = None

    def add_to_down_deck(self, cards):
        random.shuffle(cards)
        self.down_deck = cards + self.down_deck

    def replace_deck(self):
        self.deck = copy(self.down_deck)
        self.clear_down_deck()

    def clear_down_deck(self):
        self.down_deck = []


def get_decks():
    deck = copy(DECK)
    random.shuffle(deck)
    return deck[:26], deck[26:]


def compare_cards(card1, card2):
    card1_index = CARDS.index(card1[:-1])
    card2_index = CARDS.index(card2[:-1])

    # 0 equal
    # 1 player1 wins
    # 2 player2 wins

    if card1_index < card2_index:
        return 1
    if card1_index > card2_index:
        return 2
    return 0


def play_war(player1, player2):
    # Save down cards
    all_cards = [player1.card, player2.card]

    # If player does not have enough cards
    if len(player1.deck + player1.down_deck) < 2:
        all_cards += player1.deck + player1.down_deck
        return player2, all_cards
    if len(player2.deck + player2.down_deck) < 2:
        all_cards += player2.deck + player2.down_deck
        return player1, all_cards

    # If deck needs to be replaced
    if len(player1.deck) < 2:
        player1.deck += player1.down_deck
        player1.clear_down_deck()
    if len(player2.deck) < 2:
        player2.deck += player2.down_deck
        player2.clear_down_deck()

    # Get middle cards
    player1.get_card()
    player2.get_card()
    all_cards += [player1.card, player2.card]

    # Get top cards
    player1.get_card()
    player2.get_card()
    result = compare_cards(player1.card, player2.card)


    if result == 0:
        player, return_cards = play_war(player1, player2)
        all_cards += return_cards
        return player, all_cards
    
    if result == 1:
        all_cards += [player1.card, player2.card]
        return player1, all_cards
    if result == 2:
        all_cards += [player1.card, player2.card]
        return player2, all_cards


def play(player1, player2):

    winner = None
    loser = None
    counter = 1

    while True:

        if player1.lost:
            winner = player2
            loser = player1
            break
        if player2.lost:
            winner = player1
            loser = player2
            break

        if player1.is_empty:
            player1.replace_deck()
        if player2.is_empty:
            player2.replace_deck()

        player1.get_card()
        player2.get_card()

        result = compare_cards(player1.card, player2.card)
        # if player1.aces == 0:
        #     print(player1.card, player2.card, result)
        #     print(player1.deck, player1.down_deck)

        if result == 0:
            player, cards = play_war(player1, player2)
            player.add_to_down_deck(cards)

        elif result == 1:
            player1.add_to_down_deck([player1.card, player2.card])
        else:
            player2.add_to_down_deck([player1.card, player2.card])

        counter += 1

    return winner, loser, counter


def play_game():
    deck_player1, deck_player2 = get_decks()

    player1 = Player("Alice", deck_player1)
    player2 = Player("Bob", deck_player2)


    winner, loser, counter = play(player1, player2)

    result = {
        "rounds": counter,
        "winner": winner.name,
        "winner_ace": winner.aces,
        "loser": loser.name,
        "loser_ace": loser.aces,
    }

    return result


def get_average_rounds(results):
    sum = 0
    for result in results:
        sum += result["rounds"]
    return sum / len(results)

def ace_corelation(results):

    base = {
        "total_count": 0,
        "results": 0,
        "win": 0,
        "lose": 0 
    }

    aces = {}
    aces[0] = copy(base)
    aces[1] = copy(base)
    aces[2] = copy(base)
    aces[3] = copy(base)
    aces[4] = copy(base)

    for result in results:
        winner_aces = result["winner_ace"]
        loser_aces = result["loser_ace"]

        aces[winner_aces]["total_count"] += result["rounds"]
        aces[winner_aces]["results"] += 1
        aces[winner_aces]["win"] += 1

        aces[loser_aces]["total_count"] += result["rounds"]
        aces[loser_aces]["results"] += 1
        aces[loser_aces]["lose"] += 1

    for i in range(5):
        aces[i]["average_rounds"] = round(aces[i]["total_count"]/aces[i]["results"])
        aces[i]["win_prob"] = round(100*aces[i]["win"]/(aces[i]["win"]+aces[i]["lose"]),2)

    return aces


def main():
    results = []
    number_of_games = 100000

    for i in range(number_of_games):
        results.append(play_game())

    average = get_average_rounds(results)
    aces = ace_corelation(results)

    print(f"Povprečno število iger: {average}")
    print()
    for i in range(5):
        print(f"==== Igralec ima {i} asov ====")
        print(f"Povprečno število iger: {aces[i]['average_rounds']}")
        print(f"Verjetnost zmage: {aces[i]['win_prob']}")
        print()



if __name__ == "__main__":
    main()