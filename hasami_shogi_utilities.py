from HasamiShogiGame import HasamiShogiGame

class Player():
    """Defines the methods for a player of Hasami Shogi."""
    def __init__(self, game, color, starting_pieces=None, starting_moves=None):
        """Initializes a player for Hasami Shogi."""
        self._game = game
        self._color = color
        if starting_pieces:
            self._pieces = starting_pieces
        else:
            self._pieces = {
                "RED": {'a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8', 'a9'},
                "BLACK": {'i1', 'i2', 'i3', 'i4', 'i5', 'i6', 'i7', 'i8', 'i9'}
            }[color]
        if starting_moves:
            self._move_log = starting_moves
            self.simulate_game(starting_moves)
        else:
            self._move_log = []

    def simulate_game(self, starting_moves):
        """Simulates a game given a list of moves (4-character string, rcrc)."""
        if starting_moves:
            for move in starting_moves:
                self._game.make_move(move[:2], move[2:])

    def get_pieces(self):
        """Returns all the current player's pieces as a set."""
        return self._pieces

    def move_piece(self, start, end):
        """Removes start square from piece list and adds end square."""
        self._pieces.remove(start)
        self._pieces.add(end)

    def remove_pieces(self, piece_list):
        """Removes the pieces at the squares in the given list."""
        for square in piece_list:
            self._pieces.remove(square)

    def check_right_color(self, square):
        """Returns true if square is in player's list."""
        return square in self.get_pieces()

    def make_move(self, start, destination):
        """Makes the given move in the game and updates piece locations."""
        pass




