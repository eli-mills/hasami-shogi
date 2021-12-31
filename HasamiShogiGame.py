import cProfile
import copy


class HasamiShogiUtilities:
    """Contains useful constants and methods for the Hasami Shogi Game and related classes."""
    def __init__(self):
        """Initializes useful constants."""
        self.row_num = self.bi_dict({'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7, 'i': 8})
        self.col_num = self.bi_dict({'1': 0, '2': 1, '3': 2, '4': 3, '5': 4, '6': 5, '7': 6, '8': 7, '9': 8})
        self.row_labels = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']
        self.col_labels = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
        self.all_squares_in_order = [row + col for row in self.row_labels for col in self.col_labels]
        self.all_squares = set(self.all_squares_in_order)

    def bi_dict(self, dictionary):
        """Given a dictionary, adds all values as keys and their keys as values. Does not work if values are mutable."""
        output = {}
        for key, value in dictionary.items():
            output[key] = value
            output[value] = key
        return output

    def index_to_square(self, row, column):
        """Converts row/column index (indexed at 0) to square string. Assumes valid input."""
        return self.row_num[row] + self.col_num[column]

    def square_to_index(self, square_string):
        """Returns the indices of the given square string as a tuple."""
        return self.row_num[square_string[0]], self.col_num[square_string[1]]

    def opposite_color(color):
        """Returns RED if BLACK, and vice versa."""
        return {"RED": "BLACK", "BLACK": "RED"}[color]

    def get_adjacent_squares(self, square_string):
        """Returns all directly adjacent pieces of the given square string."""
        row, col = self.square_to_index(square_string)
        poss_rows = row + 1, row - 1
        poss_cols = col + 1, col - 1
        return {self.index_to_square(x, col) for x in poss_rows if 0 <= x < 9} | \
               {self.index_to_square(row, y) for y in poss_cols if 0 <= y < 9}

    def get_next_square(self, square_string1, square_string2):
        """Given two adjacent square strings, gives the next square in a line. Returns None if off board. Assumes valid input."""
        if not square_string1 or not square_string2:
            return None
        (row1, col1), (row2, col2) = self.square_to_index(square_string1), self.square_to_index(square_string2)
        row_dir, col_dir = row2 - row1, col2 - col1
        next_row, next_col = row2 + row_dir, col2 + col_dir
        if 0 <= next_row < 9 and 0 <= next_col < 9:
            return self.index_to_square(next_row, next_col)
        return None

    def build_square_string_range(self, square_string_from, square_string_to):
        """Returns list of square strings from first square to second. Range cannot be diagonal. Assumes valid input."""
        if not square_string_from or not square_string_to:
            return None

        if square_string_from[0] != square_string_to[0] and square_string_from[1] != square_string_to[1]:
            return None

        # 1. Convert square strings to indices.
        row_from, col_from = self.square_to_index(square_string_from)
        row_to, col_to = self.square_to_index(square_string_to)

        # 2. Generate ranges. There should be exactly one range of length 0.
        row_min, row_max = min(row_to, row_from), max(row_to, row_from)
        col_min, col_max = min(col_to, col_from), max(col_to, col_from)
        row_range, col_range = range(row_min, row_max + 1), range(col_min, col_max + 1)

        # 3. Generate list of square strings from ranges. Reverse output if necessary.
        output_range = [self.index_to_square(row, col) for row in row_range for col in col_range]
        return output_range if row_from <= row_to and col_from <= col_to else output_range[::-1]


class CaptureChain:
    """Defines the methods and properties of a network of Hasami Shogi pieces where a capture is possible."""
    def __init__(self, pieces, orientation):
        """Creates a capture network with the given list of Piece objects."""



class Piece(HasamiShogiUtilities):
    """Defines the methods and properties of pieces in a Hasami Shogi game."""
    def __init__(self, color, square, board):
        """Initializes a piece object with a color at a particular square."""
        super().__init__()
        self._directions = {'left', 'right', 'up', 'down'}
        self.color = color
        self.position = square
        self.board = board
        self.visible_pieces = {'left': None, 'right': None, 'up': None, 'down': None}
        self.reachable_squares = {'left': set(), 'right': set(), 'up': set(), 'down': set()}
        if self.board.get_square_piece_dict():
            self.initialize_piece_to_board()
        self.capture_networks = {"capturing": set(), "captured": set()}

    def short_setup(self):
        """Used by Board to point Piece to partners once all have been initialized."""
        row = self.position[0]
        col = self.position[1]
        right_neighbor = str(int(col)+1)
        left_neighbor = str(int(col)-1)
        if col < '9':
            self.visible_pieces['right'] = self.board.get_square_piece_dict()[row + right_neighbor]
        if col > '1':
            self.visible_pieces['left'] = self.board.get_square_piece_dict()[row + left_neighbor]
        if row == 'a':
            self.visible_pieces['down'] = self.board.get_square_piece_dict()['i' + col]
            self.reachable_squares['down'] = set(self.build_square_string_range(f'b{col}', f'h{col}'))
        elif row == 'i':
            self.visible_pieces['up'] = self.board.get_square_piece_dict()['a' + col]
            self.reachable_squares['up'] = set(self.build_square_string_range(f'b{col}', f'h{col}'))

    def initialize_piece_to_board(self):
        """Used to setup Piece object on existing board (for testing only)."""
        self.set_visible_piece('left', self.find_piece_in_direction('left'))
        self.set_visible_piece('right', self.find_piece_in_direction('right'))
        self.set_visible_piece('up', self.find_piece_in_direction('up'))
        self.set_visible_piece('down', self.find_piece_in_direction('down'))

        self.set_reachable_squares('left', self.find_squares_in_direction('left'))
        self.set_reachable_squares('right', self.find_squares_in_direction('right'))
        self.set_reachable_squares('up', self.find_squares_in_direction('up'))
        self.set_reachable_squares('down', self.find_squares_in_direction('down'))

    def find_piece_in_direction(self, direction):
        """Given a direction, finds the first piece in that direction on the game board."""
        if direction == 'left' or direction == 'right':
            possible_squares = {square for square in self.board.get_square_piece_dict() if square[0] == self.position[0]}
        if direction == 'up' or direction == 'down':
            possible_squares = {square for square in self.board.get_square_piece_dict() if square[1] == self.position[1]}

        if direction == 'right' or direction == 'down':             # Increasing direction
            possible_squares = {square for square in possible_squares if square > self.position}
            return self.board.get_square_piece_dict()[min(possible_squares)] if possible_squares else None
        if direction == 'left' or direction == 'up':                # Decreasing direction
            possible_squares = {square for square in possible_squares if square < self.position}
            return self.board.get_square_piece_dict()[max(possible_squares)] if possible_squares else None

    def find_squares_in_direction(self, direction):
        """Given a direction, returns set of all reachable squares in that direction."""
        if self.visible_pieces[direction]:
            vis_piece = self.visible_pieces[direction]
            return set(self.build_square_string_range(self.position, vis_piece.position)[1:-1])
        edge = self.get_board_edge(self.position, direction)
        return set(self.build_square_string_range(self.position, edge)[1:])

    def get_visible_pieces(self):
        """Returns the Piece's set of visible Pieces."""
        return {self.visible_pieces[dir] for dir in {'left', 'right', 'up', 'down'} if self.visible_pieces[dir]}

    def get_visible_piece_in_dir(self, direction):
        return self.visible_pieces[direction]

    def set_visible_piece(self, direction, piece):
        """Sets the given Piece as visible in the given direction. Sets self as visible to Piece in opposite direction."""
        opp_direction = self.find_opp_move(direction)
        self.visible_pieces[direction] = piece
        if piece:                                           # Check if piece given None value.
            piece.visible_pieces[opp_direction] = self

    def get_reachable_squares(self):
        """Returns the set of squares the Piece object can reach."""
        reachable = self.reachable_squares
        return reachable['up'] | reachable['down'] | reachable['left'] | reachable['right']

    def get_reach_squares_in_dir(self, direction):
        """Takes a direction and returns the set of reachable squares in that direction."""
        return set(self.reachable_squares[direction])

    def set_reachable_squares(self, direction, square_set):
        """Sets the Piece's reachable squares in a given direction to the given set.
        Updates visible Piece if available."""
        self.reachable_squares[direction] = square_set
        if self.visible_pieces[direction]:
            opp_dir = self.find_opp_move(direction)
            self.visible_pieces[direction].reachable_squares[opp_dir] = square_set

    def can_reach(self, square):
        """Returns True if the given square is in the Piece's reachable squares, else False."""
        return square in self.reachable_squares

    def can_see(self, piece):
        """Returns True if the given Piece is in the Piece's visible pieces, else False."""
        return piece in self.visible_pieces

    def find_move_dir(self, old_square, new_square):
        """Returns 'left', 'right', 'up', or 'down' based on move direction. Returns None otherwise."""
        if old_square[0] == new_square[0]:                                  # Horizontal
            if old_square[1] < new_square[1]:
                return 'right'
            if old_square[1] > new_square[1]:
                return 'left'
        elif old_square[1] == new_square[1]:                                # Vertical
            if old_square[0] < new_square[0]:
                return 'down'
            if old_square[0] > new_square[0]:
                return 'up'
        return None

    def find_cross_move(self, move_dir):
        """Given a move direction, returns the 'cross directions' tuple. Increasing square value direction first."""
        if move_dir == 'up' or move_dir == 'down':
            return 'right', 'left'
        elif move_dir == 'right' or move_dir == 'left':
            return 'down', 'up'

    def find_opp_move(self, move_dir):
        return self.bi_dict({'up': 'down', 'left': 'right'})[move_dir]

    def get_board_edge(self, square, direction):
        """Given a square and a direction, returns the square at the board's edge in that direction."""
        class BoardEdgeError(Exception):
            pass
        if direction == 'up':
            return 'a' + square[1]
        if direction == 'down':
            return 'i' + square[1]
        if direction == 'right':
            return square[0] + '9'
        if direction == 'left':
            return square[0] + '1'
        raise BoardEdgeError

    def update_cross_dir(self, old_pos, increase_dir, decrease_dir):
        """Updates the visible pieces and reachable squares in the given directions."""

        old_increasing = self.visible_pieces[increase_dir]
        old_decreasing = self.visible_pieces[decrease_dir]
        if old_increasing: old_increasing.set_visible_piece(decrease_dir, old_decreasing)
        if old_decreasing: old_decreasing.set_visible_piece(increase_dir, old_increasing)

        reachable_squares = self.reachable_squares[decrease_dir] | self.reachable_squares[increase_dir] | {old_pos}
        if old_increasing: old_increasing.set_reachable_squares(decrease_dir, reachable_squares)
        if old_decreasing: old_decreasing.set_reachable_squares(increase_dir, reachable_squares)

        new_incr_piece = self.find_piece_in_direction(increase_dir)
        new_decr_piece = self.find_piece_in_direction(decrease_dir)
        self.set_visible_piece(increase_dir, new_incr_piece)        # Also sets other piece if not None.
        self.set_visible_piece(decrease_dir, new_decr_piece)

        incr_reachable = self.find_squares_in_direction(increase_dir)
        decr_reachable = self.find_squares_in_direction(decrease_dir)
        self.set_reachable_squares(increase_dir, incr_reachable)
        self.set_reachable_squares(decrease_dir, decr_reachable)

    def find_adj_piece(self):
        """Searches all four directions. Returns set of (direction, Piece) tuples or empty set if none found."""
        return {(dir, self.visible_pieces[dir]) for dir in self._directions if self.visible_pieces[dir] and not self.reachable_squares[dir]}

    def remove_piece(self):
        """Updates visible pieces for Piece removal."""
        vertical_reachable = self.reachable_squares['up'] | self.reachable_squares['down'] | {self.position}
        horizontal_reachable = self.reachable_squares['left'] | self.reachable_squares['right'] | {self.position}
        if self.visible_pieces['up']:
            self.visible_pieces['up'].set_reachable_squares('down', vertical_reachable)
            self.visible_pieces['up'].set_visible_piece('down', self.visible_pieces['down'])
        if self.visible_pieces['down']:
            self.visible_pieces['down'].set_reachable_squares('up', vertical_reachable)
            self.visible_pieces['down'].set_visible_piece('up', self.visible_pieces['up'])
        if self.visible_pieces['left']:
            self.visible_pieces['left'].set_reachable_squares('right', horizontal_reachable)
            self.visible_pieces['left'].set_visible_piece('right', self.visible_pieces['right'])
        if self.visible_pieces['right']:
            self.visible_pieces['right'].set_reachable_squares('left', horizontal_reachable)
            self.visible_pieces['right'].set_visible_piece('left', self.visible_pieces['left'])

    def move_piece(self, new_pos):
        """Sets the new position and updates all necessary pieces."""
        old_pos = self.position
        self.position = new_pos
        move_dir = self.find_move_dir(old_pos, new_pos)
        opp_dir = self.find_opp_move(move_dir)
        self.board.set_piece_at_square(new_pos, self)
        self.board.del_piece_at_square(old_pos)

        path = self.build_square_string_range(old_pos, new_pos)

        self.reachable_squares[opp_dir] |= set(path[:-1])
        self.reachable_squares[move_dir] -= set(path)
        move_dir_reachable = self.reachable_squares[move_dir]
        opp_dir_reachable = self.reachable_squares[opp_dir]
        if self.visible_pieces[move_dir]:
            self.visible_pieces[move_dir].set_reachable_squares(opp_dir, move_dir_reachable)
        if self.visible_pieces[opp_dir]:
            self.visible_pieces[opp_dir].set_reachable_squares(move_dir, opp_dir_reachable)

        incr_cross, decr_cross = self.find_cross_move(move_dir)
        self.update_cross_dir(old_pos, incr_cross, decr_cross)


class GameBoard(HasamiShogiUtilities):
    """Defines the methods for a Hasami Shogi game board. Used by HasamiShogiGame."""
    def __init__(self):
        """Initializes a 9x9 Hasami Shogi game board as a list of lists. Sets player positions."""
        super().__init__()
        black_starting_squares = {'i1', 'i2', 'i3', 'i4', 'i5', 'i6', 'i7', 'i8', 'i9'}
        red_starting_squares = {'a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8', 'a9'}
        self._square_piece_dict = {}
        self.capture_chains = {}    # (square, color): {capture chains}
        all_pieces = {Piece("RED", square, self) for square in red_starting_squares} | {Piece("BLACK", square, self) for square in black_starting_squares}
        self._square_piece_dict = {square: piece for square in self.all_squares for piece in all_pieces if piece.position == square}
        for piece in all_pieces: piece.short_setup()

    def get_board_list(self):
        """Returns the board as a list of lists."""
        return [[color for color in [self.get_square(ss) for ss in self.all_squares_in_order]][(9 * x):(9 * (x + 1))] for x in range(0, 9)]

    def print_board(self):
        """Prints the current board with row/column labels. Abbreviates RED and BLACK and replaces NONE with '.'. """
        print("  " + " ".join(self.col_labels))
        for row in range(9):
            output_string = self.row_labels[row] + " "
            for square in self.get_board_list()[row]:
                if square == "NONE":
                    output_string += '. '
                else:
                    output_string += square[0] + " "
            print(output_string[:-1])

    def get_square(self, square_string):
        """Given a square string, returns the value at that square."""
        piece = self.get_piece_at_square(square_string)
        return piece.color if piece else "NONE"

    def set_square(self, square_string, square_value):
        """Sets the value of the given square to the given value."""
        if square_string not in self.all_squares or square_value not in {"RED", "BLACK", "NONE"}:
            return None
        if square_value == "NONE":
            self.remove_piece(square_string)
        else:
            self.set_piece_at_square(square_string, Piece(square_value, square_string, self))

    def get_square_piece_dict(self):
        """Returns the dictionary of all occupied squares and their Piece objects."""
        return dict(self._square_piece_dict)

    def get_piece_at_square(self, square):
        """Returns the Piece object at the given square. Returns NONE if no piece at square."""
        return self._square_piece_dict.get(square)

    def set_piece_at_square(self, square, piece):
        """Sets the given square to the given piece."""
        self._square_piece_dict[square] = piece

    def del_piece_at_square(self, square):
        """Deletes the entry for the given square in the occupant dictionary."""
        del self._square_piece_dict[square]

    def move_piece(self, piece_loc, destination):
        """Moves the piece at the given location to the destination."""
        piece = self._square_piece_dict[piece_loc]
        piece.move_piece(destination)

    def remove_piece(self, piece_loc):
        """Removes the piece at the given location from the dictionary and calls Piece method to update visibles."""
        piece_to_remove = self._square_piece_dict[piece_loc]
        piece_to_remove.remove_piece()
        del self._square_piece_dict[piece_loc]


class HasamiShogiGame(HasamiShogiUtilities):
    """Defines the methods for a game of Hasami Shogi."""
    def __init__(self):
        """Creates a new board, sets game state to UNFINISHED, active player to BLACK, captured pieces to 0."""
        super().__init__()
        self._game_board = GameBoard()
        self._game_state = "UNFINISHED"     # UNFINISHED, RED_WON, BLACK_WON
        self._active_player = "BLACK"       # BLACK, RED
        self._inactive_player = "RED"       # BLACK, RED
        self._captured_pieces = {"RED": 0, "BLACK": 0}

    def get_game_board(self):
        """Returns the game board object."""
        return self._game_board

    def get_game_state(self):
        """Returns the current game state."""
        return self._game_state

    def set_game_state(self, game_state):
        """Sets the game state to the given value."""
        self._game_state = game_state

    def get_active_player(self):
        """Returns the current player."""
        return self._active_player

    def toggle_active_player(self):
        """Switches the active player to the other color."""
        self._active_player, self._inactive_player = self._inactive_player, self._active_player

    def get_num_captured_pieces(self, player_color):
        """Returns the number of captured pieces of the given color."""
        return self._captured_pieces[player_color]

    def add_num_captured_pieces(self, player_color, num_captured):
        """Adds the given number to the captured pieces of the given color."""
        self._captured_pieces[player_color] += num_captured

    def get_square_occupant(self, square_string):
        """Returns the value at the given square on the board: RED, BLACK, or NONE."""
        return self.get_game_board().get_square(square_string)

    def set_square_occupant(self, square_string, value):
        """Sets the occupant at the given square to the given value."""
        self.get_game_board().set_square(square_string, value)

    def execute_move(self, moving_from, moving_to):
        """(Blindly) moves the piece at the first position to the second position."""
        self._game_board.move_piece(moving_from, moving_to)

    def is_move_legal(self, moving_from, moving_to):
        """Checks if move from first square to second is legal. Returns True if so, False if not."""
        if self.get_game_state() != "UNFINISHED":                                               # Game is finished
            return False

        if moving_from not in self.all_squares or moving_to not in self.all_squares:              # Out of range
            return False

        piece = self.get_game_board().get_piece_at_square(moving_from)

        if not piece:                                                                           # Moving on empty square
            return False

        if piece.color != self.get_active_player():                                             # Wrong color
            return False

        if moving_to not in piece.get_reachable_squares():                                      # Square not in reach
            return False
        return True

    def find_captured_squares(self, from_square, to_square):
        """Finds capture pattern in given square string range. Returns captured squares if found, else False."""
        capturing_color = self.get_square_occupant(from_square)
        captured_color = {"RED": "BLACK", "BLACK": "RED"}[capturing_color]              # Picks opposite color.
        square_string_list = self.get_game_board().build_square_string_range(from_square, to_square)  # Square strings
        square_value_list = [self.get_square_occupant(x) for x in square_string_list]                 # Values on board
        for index, square_value in enumerate(square_value_list[1:]):
            if square_value == capturing_color:
                if index == 0:                                          # Two of capturing color in a row, no capture.
                    return False
                end_cap = square_string_list[1:][index]                 # Store the other "bread" of the "sandwich".
                return self.get_game_board().build_square_string_range(from_square, end_cap)[1:-1]  # Captured only.
            if square_value != captured_color:                          # Breaks on NONE.
                return False

    def check_linear_captures(self, moved_to):
        """Searches four directions around latest move, captures pieces, and updates capture counts.
        Returns False if no capture."""

        # 1. Determine 4 limits to the edges of the board.
        left_limit = moved_to[0] + '1'
        right_limit = moved_to[0] + '9'
        top_limit = 'a' + moved_to[1]
        bottom_limit = 'i' + moved_to[1]
        search_directions = [left_limit, right_limit, top_limit, bottom_limit]

        # 2. Check each direction for captures up to the edges of the board.
        captured_lists = [self.find_captured_squares(moved_to, limit) for limit in search_directions]
        captured_squares = [square for sublist in captured_lists if sublist for square in sublist]

        # 3. Add captured pieces to the score.
        self.add_num_captured_pieces(self._inactive_player, len(captured_squares))

        # 4. Change all captured squares to "NONE".
        for captured in captured_squares:
            self._game_board.remove_piece(captured)

    def find_closest_corner(self, moved_to):
        """Finds the closest corner to the new square to check for corner capture."""
        closest_corner = ""
        square_row, square_column = self.get_game_board().square_to_index(moved_to)
        if square_row <= 1:
            closest_corner += "a"
        if square_row >= 7:
            closest_corner += "i"
        if square_column <= 1:
            closest_corner += "1"
        if square_column >= 7:
            closest_corner += "9"
        return closest_corner

    def check_corner_capture(self, moved_to):
        """Checks for a capture in the corner. Removes enemy piece in corner. Returns True if successful, else False."""
        capture_scenarios = {                           # Key is the captured piece, lists are capturing positions.
            "a1": ["a2", "b1"],
            "a9": ["a8", "b9"],
            "i1": ["h1", "i2"],
            "i9": ["h9", "i8"]
        }

        closest_corner = self.find_closest_corner(moved_to)

        if closest_corner in capture_scenarios:
            if moved_to in capture_scenarios[closest_corner]:

                # Determine what colors are at the three corner positions:
                moved_to_index = capture_scenarios[closest_corner].index(moved_to)
                capturing_end = capture_scenarios[closest_corner][moved_to_index - 1]
                moved_to_color = self.get_square_occupant(moved_to)
                captured_color = self.get_square_occupant(closest_corner)
                capturing_end_color = self.get_square_occupant(capturing_end)

                # Check for correct pattern:
                if moved_to_color == capturing_end_color and captured_color == self._inactive_player:
                    self._game_board.remove_piece(closest_corner)
                    self.add_num_captured_pieces(self._inactive_player, 1)

    def check_win(self):
        """Checks if the number of captured pieces of either color is 8 or 9."""
        if self.get_num_captured_pieces("RED") > 7:
            self.set_game_state("BLACK_WON")
        elif self.get_num_captured_pieces("BLACK") > 7:
            self.set_game_state("RED_WON")

    def make_move(self, moving_from, moving_to):
        """Moves from first square to second and returns True if legal, then updates game variables accordingly."""
        if not self.is_move_legal(moving_from, moving_to):
            return False
        self.execute_move(moving_from, moving_to)
        self.check_linear_captures(moving_to)
        self.check_corner_capture(moving_to)
        self.check_win()
        self.toggle_active_player()
        return True


def main():
    new_game = HasamiShogiGame()
    new_game.make_move('i5', 'e5')
    new_game.make_move('a4', 'e4')
    adj = new_game.get_game_board().get_piece_at_square('e4').find_adj_piece()
    pass

if __name__ == '__main__':
    # cProfile.run('main()', sort='cumtime')
    main()
