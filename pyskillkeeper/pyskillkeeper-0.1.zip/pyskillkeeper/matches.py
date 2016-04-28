from collections import namedtuple


class Tournament(object):

    def __init__(self, name):
        self.name = name
        self.matches = []


class Match(namedtuple('Match', ['id', 'time', 'order', 'tournament', 'player1', 'player2', 'winner'])):

    def __repr__(self):
        if not self.winning_player:
            return '<Match %s vs %s (TIE) at %s>' % (self.player1, self.player2, self.tournament)
        return '<Match %s (WIN) vs %s (LOSS) at %s>' % (self.winning_player, self.losing_player, self.tournament)

    @property
    def winning_player(self):
        if self.winner == 0:
            # Tie.
            return None

        if self.winner == 1:
            return self.player1
        return self.player2

    @property
    def losing_player(self):
        if self.winner == 0:
            # Tie.
            return None

        if self.winner == 1:
            return self.player2
        return self.player1
