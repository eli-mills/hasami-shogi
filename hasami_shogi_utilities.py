from HasamiShogiGame import HasamiShogiGame

# LABELS (USED BY VISUAL CONSTANTS)
row_labels = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']
col_labels = ['1', '2', '3', '4', '5', '6', '7', '8', '9']

# USED BY AI
corner_capturing_pieces = {
    'a2': 'b1',
    'b1': 'a2',
    'a8': 'b9',
    'b9': 'a8',
    'h1': 'i2',
    'i2': 'h1',
    'h9': 'i8',
    'i8': 'h9'
}

def run_moves(game, move_list):
    """Takes game object and list of 4-string moves."""
    return [game.make_move(move[:2], move[2:]) for move in move_list]


def index_to_string(row, column):
    """Converts row/column index (indexed at 0) to square string. Assumes valid input."""
    return row_labels[row] + col_labels[column]


def string_to_index(square_string):
    """Returns the indices of the given square string as a tuple."""
    return row_labels.index(square_string[0]), col_labels.index(square_string[1])


def get_game_pieces(game):
    """Given a game, returns a color: [square_string_list] dictionary."""
    output = {"RED": set(), "BLACK": set()}
    for row in row_labels:
        for col in col_labels:
            square_occupant = game.get_square_occupant(row+col)
            if square_occupant in output:
                output[square_occupant].add(row+col)
    return output


def get_adjacent_squares(square_string):
    """Returns all directly adjacent pieces of the given square string."""
    output = set()
    row, col = string_to_index(square_string)
    poss_rows = row+1, row-1
    poss_cols = col+1, col-1
    for poss_row in poss_rows:
        if 0 <= poss_row < 9:
            output.add(index_to_string(poss_row, col))
    for poss_col in poss_cols:
        if 0 <= poss_col < 9:
            output.add(index_to_string(row, poss_col))
    return output


def get_next_square_in_line(square_string1, square_string2):
    """Given two adjacent square strings, gives the next square in a line. Returns None if out of range. Assumes valid input."""
    (row1, col1), (row2, col2) = string_to_index(square_string1), string_to_index(square_string2)
    row_dir, col_dir = row2 - row1, col2 - col1
    next_row, next_col = row2 + row_dir, col2 + col_dir
    if 0 <= next_row < 9 and 0 <= next_col < 9:
        return index_to_string(next_row, next_col)
    return None


def build_square_string_range(square_string_from, square_string_to):
    """Returns list of square strings from first square to second. Range cannot be diagonal. Assumes valid input."""
    if not square_string_from or not square_string_to:
        return None

    if square_string_from[0] != square_string_to[0] and square_string_from[1] != square_string_to[1]:
        return None

    # 1. Convert square strings to indices.
    row_from, col_from = row_labels.index(square_string_from[0]), int(square_string_from[1]) - 1
    row_to, col_to = row_labels.index(square_string_to[0]), int(square_string_to[1]) - 1

    # 2. Generate ranges. There should be exactly one range of length 0.
    row_min, row_max = min(row_to, row_from), max(row_to, row_from)
    col_min, col_max = min(col_to, col_from), max(col_to, col_from)
    row_range, col_range = range(row_min, row_max + 1), range(col_min, col_max + 1)

    # 3. Generate list of square strings from ranges. Reverse output if necessary.
    output_range = []
    for row_index in row_range:
        for col_index in col_range:
            output_range.append(row_labels[row_index] + col_labels[col_index])
    return output_range if row_from <= row_to and col_from <= col_to else output_range[::-1]


def return_valid_moves(game, square_string):
    """Returns all valid moves for the given square."""
    if game.get_square_occupant(square_string) == game.get_active_player():
        valid_moves = []
        north = build_square_string_range(square_string, 'a' + square_string[1])
        east = build_square_string_range(square_string, square_string[0] + '9')
        south = build_square_string_range(square_string, 'i' + square_string[1])
        west = build_square_string_range(square_string, square_string[0] + '1')
        for direction in [north, east, south, west]:
            for square in direction[1:]:
                if game.get_square_occupant(square) == "NONE":
                    valid_moves.append(square_string + square)
                else:
                    break
        return valid_moves


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
        self._move_log = []
        self._is_active = False
        self.update_active()
        self.call_count = 0

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

    def set_opposing_player(self, player):
        """Stores the given opposing player accordingly."""
        if player.get_color() == self._opposing_color:
            self._opposing_player = player
            player._opposing_player = self

    def get_pieces(self):
        """Returns all the current player's pieces as a set."""
        return self._pieces

    def move_piece(self, start, end):
        """Removes start square from piece list and adds end square."""
        # print(self._color, self._pieces)
        # print("Moving", start, "to", end)
        self._pieces.remove(start)
        self._pieces.add(end)

    def remove_pieces(self, piece_list):
        """Removes the pieces at the squares in the given list."""
        for square in piece_list:
            self._pieces.remove(square)

    def get_move_log(self):
        """Returns the current move log."""
        return self._move_log

    def add_to_move_log(self, move):
        """Adds a 4-char move to the move log."""
        self._move_log.append(move)

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
            self.add_to_move_log(start+destination)
            self.update_active()
            if self._opposing_player:
                self._opposing_player.add_to_move_log(start+destination)
                self._opposing_player.update_active()
            if prev_captures != self._game.get_num_captured_pieces(self._opposing_color):   # Pieces were captured
                self.remove_captured_pieces()


def main():
    new_game = HasamiShogiGame()
    player_red = Player(new_game, "RED", )
    player_black = Player(new_game, "BLACK")
    player_red.set_opposing_player(player_black)
    player_black.make_move("i5", "e5")
    player_red.make_move("a4", "e4")
    player_black.make_move("i3", "e3")
    new_game.get_game_board().print_board()
    print(get_adjacent_squares("a2"))



if __name__ == "__main__":
    main()

