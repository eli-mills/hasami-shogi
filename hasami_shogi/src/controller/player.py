class Player:
    """Defines the methods for a player of Hasami Shogi."""
    def __init__(self, game, color):
        """Initializes a player for Hasami Shogi."""
        self._game = game
        self._color = color
        self._opposing_color = {"RED": "BLACK", "BLACK": "RED"}[color]
        self._pieces = {
            "RED": {'a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8', 'a9'},
            "BLACK": {'i1', 'i2', 'i3', 'i4', 'i5', 'i6', 'i7', 'i8', 'i9'}
        }[color]
        self._opposing_player = None
        self._is_active = False
        self.update_active()

    def update_active(self):
        """Checks the game status and updates whether the Player is the active player."""
        self._is_active = (self._game.get_active_player() == self._color)

    def get_active(self):
        """Returns True if current player is active."""
        return self._is_active

    def get_game(self):
        """Returns the current game."""
        return self._game

    def get_color(self):
        """Returns the player's color."""
        return self._color

    def get_opposing_color(self):
        """Returns the opposing player's color."""
        return self._opposing_color

    def get_opposing_player(self):
        """Returns the opposing player object."""
        return self._opposing_player

    def set_opposing_player(self, player):
        """Sets the given player as opponent and sets self as given player's opponent. Must be opposite colors."""
        if player.get_color() == self._opposing_color:
            self._opposing_player = player
            player._opposing_player = self

    def get_pieces(self):
        """Returns all the current player's pieces as a set."""
        return self._pieces

    def move_piece(self, start, end):
        """Removes start square from piece list and adds end square."""
        self._pieces.remove(start)
        self._pieces.add(end)

    def remove_pieces(self, piece_list):
        """Removes squares in given list from the Player's piece set."""
        for square in piece_list:
            self._pieces.remove(square)

    def add_pieces(self, piece_list):
        """Adds squares in given list to the Player's piece set."""
        for square in piece_list:
            self._pieces.add(square)

    def check_right_color(self, square):
        """Returns true if square is in player's list."""
        return square in self.get_pieces()

    def remove_captured_pieces(self):
        """Finds and removes the captured squares from the opponent's list."""
        old_set = set(self._opposing_player.get_pieces())
        for piece in old_set:
            if self._game.get_square_occupant(piece) == "NONE":
                self._opposing_player.remove_pieces([piece])

    def make_move(self, start, destination):
        """Makes the given move in the game and updates piece locations in log and opponent's log."""
        prev_captures = self._game.get_num_captured_pieces(self._opposing_color)
        if self._game.make_move(start, destination):
            if self._is_active:
                self.move_piece(start, destination)
            self.update_active()
            if self._opposing_player:
                self._opposing_player.update_active()
            if prev_captures != self._game.get_num_captured_pieces(self._opposing_color):   # Pieces were captured
                self.remove_captured_pieces()
            return True
        return False

    def undo_move(self):
        """Calls undo_move on HasamiShogiGame and handles restoring correct pieces to both players."""
        results = self._game.undo_move()
        if results is None:
            return
        move, cap_pieces = results
        self.move_piece(move[2:], move[:2])
        if cap_pieces is not None:
            self._opposing_player.add_pieces(cap_pieces)
        self.update_active()
