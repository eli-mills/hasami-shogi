from HasamiShogiGame import HasamiShogiGame

# LABELS (USED BY VISUAL CONSTANTS)
row_labels = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']
col_labels = ['1', '2', '3', '4', '5', '6', '7', '8', '9']


def run_moves(game, move_list):
    """Takes game object and list of 4-string moves."""
    return [game.make_move(move[:2], move[2:]) for move in move_list]


def build_square_string_range(square_string_from, square_string_to):
    """Returns list of square strings from first square to second. Range cannot be diagonal. Assumes valid input."""
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
        self._pieces = {
            "RED": {'a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8', 'a9'},
            "BLACK": {'i1', 'i2', 'i3', 'i4', 'i5', 'i6', 'i7', 'i8', 'i9'}
        }[color]
        self._opposing_player = None
        self._move_log = []
        self._is_active = False
        self.update_active()

    def update_active(self):
        """Checks the game status and updates whether the Player is the active player."""
        self._is_active = (self._game.get_active_player() == self._color)

    def get_color(self):
        """Returns the player's color."""
        return self._color

    def set_opposing_player(self, player):
        """Stores the given opposing player accordingly."""
        self._opposing_player = player
        player._opposing_player = self

    def simulate_game(self, moves):
        """Simulates a game given a list of moves (4-character string, rcrc). Assumes all moves are valid."""
        if self._color == "BLACK":
            black_player = self
            red_player = self._opposing_player
        else:
            black_player = self._opposing_player
            red_player = self

        for move_num, move in enumerate(moves):
            if move_num%2 == 0:
                black_player.make_move(move[:2], move[2:])
            else:
                red_player.make_move(move[:2], move[2:])

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

    def get_move_log(self):
        """Returns the current move log."""
        return self._move_log

    def add_to_move_log(self, move):
        """Adds a 4-char move to the move log."""
        self._move_log.append(move)

    def check_right_color(self, square):
        """Returns true if square is in player's list."""
        return square in self.get_pieces()

    def make_move(self, start, destination):
        """Makes the given move in the game and updates piece locations in log and opponent's log."""
        if self._game.make_move(start, destination):
            if self._is_active:
                self.move_piece(start, destination)
            self.add_to_move_log(start+destination)
            self.update_active()
            if self._opposing_player:
                self._opposing_player.add_to_move_log(start+destination)
                self._opposing_player.update_active()


def main():
    new_game = HasamiShogiGame()
    player_red = Player(new_game, "RED", )
    player_black = Player(new_game, "BLACK")
    print(return_valid_moves(new_game, "i7"))
    player_black.make_move("i7", "f7", player_red)
    player_red.make_move("a2", "d2", player_black)
    new_game.get_game_board().print_board()
    print(return_valid_moves(new_game, "f7"))
    print(player_black.get_pieces())
    print(player_red.get_pieces())
    print(player_black.get_move_log())
    print(player_red.get_move_log())



if __name__ == "__main__":
    main()

