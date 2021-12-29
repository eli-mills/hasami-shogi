# Author: Eli Mills
# Date: 11/25/2021
# Description: Portfolio Project - Hasami Shogi

import cProfile


class HasamiShogiUtilities:
    """Contains useful constants and methods for the Hasami Shogi Game and related classes."""
    def __init__(self):
        """Initializes useful constants."""
        self.row_num = self.bi_dict({'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7, 'i': 8})
        self.col_num = self.bi_dict({'1': 0, '2': 1, '3': 2, '4': 3, '5': 4, '6': 5, '7': 6, '8': 7, '9': 8})
        self._row_labels = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']
        self._col_labels = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
        self._all_squares_in_order = [row + col for row in self._row_labels for col in self._col_labels]
        self._all_squares = set(self._all_squares_in_order)

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


class CaptureNetwork:
    """Defines the methods and properties of a network of Hasami Shogi pieces where a capture is possible."""
    def __init__(self, piece_list):
        """Creates a capture network with the given list of Piece objects."""
        pass


class Piece(HasamiShogiUtilities):
    """Defines the methods and properties of pieces in a Hasami Shogi game."""
    def __init__(self, color, square, board):
        """Initializes a piece object with a color at a particular square."""
        super().__init__()
        self._color = color
        self._position = square
        self._board = board
        self._visible_pieces = {'left': None, 'right': None, 'up': None, 'down': None}
        self._reachable_squares = {'left': set(), 'right': set(), 'up': set(), 'down': set()}
        self._move_dir_partners = self.bi_dict({'left': 'right', 'up': 'down'})

        initial_reachable = {x + self._position[1] for x in self._row_labels[1:8]}
        if self._position[0] == 'a':
            self._reachable_squares['down'] = initial_reachable
        elif self._position[0] == 'i':
            self._reachable_squares['up'] = initial_reachable

    def initialize_visible_piece(self):
        """To be called by GameBoard after Pieces are initialized. Sets the initial visible piece across the board."""
        if self._position[0] == 'a':
            self._visible_pieces['down'] = self._board.get_square_piece_dict()['i'+self._position[1]]
        elif self._position[0] == 'i':
            self._visible_pieces['up'] = self._board.get_square_piece_dict()['a'+self._position[1]]

    def set_position(self, new_square):
        """Sets piece position to new square. Does not check if square is valid."""
        self._position = new_square

    def get_position(self):
        """Returns the Piece's position."""
        return self._position

    def get_color(self):
        """Returns the Piece's color."""
        return self._color

    def get_visible_pieces(self):
        """Returns the Piece's set of visible Pieces."""
        return {self._visible_pieces[dir] for dir in {'left', 'right', 'up', 'down'} if self._visible_pieces[dir]}

    def set_visible_piece(self, direction, piece):
        """Sets the Piece's visible pieces to the given piece in the given direction."""
        self._visible_pieces[direction] = piece

    def get_reachable_squares(self):
        """Returns the set of squares the Piece object can reach."""
        reachable = self._reachable_squares
        return reachable['up'] | reachable['down'] | reachable['left'] | reachable['right']

    def get_reach_squares_in_dir(self, direction):
        """Takes a direction and returns the set of reachable squares in that direction."""
        return set(self._reachable_squares[direction])

    def set_reachable_squares(self, direction, square_set):
        """Sets the Piece's reachable squares in a given direction to the given set."""
        self._reachable_squares[direction] = square_set

    def can_reach(self, square):
        """Returns True if the given square is in the Piece's reachable squares, else False."""
        return square in self._reachable_squares

    def can_see(self, piece):
        """Returns True if the given Piece is in the Piece's visible pieces, else False."""
        return piece in self._visible_pieces

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

    def move_piece(self, new_pos):
        """Sets the new position and updates all necessary pieces."""
        old_pos = self._position
        self.set_position(new_pos)
        move_dir = self.find_move_dir(old_pos, new_pos)
        opp_dir = self._move_dir_partners[move_dir]
        self._board.set_square_piece(new_pos, self)
        self._board.del_square_piece(old_pos)
        piece_dict = self._board.get_square_piece_dict()

        path = self.build_square_string_range(old_pos, new_pos)
        if self._reachable_squares[opp_dir]:
            self._reachable_squares[opp_dir] |= set(path[:-1])
        if self._reachable_squares[move_dir]:
            self._reachable_squares[move_dir] -= set(path)
        move_dir_reachable = self._reachable_squares[move_dir]
        opp_dir_reachable = self._reachable_squares[opp_dir]
        if self._visible_pieces[move_dir]:
            self._visible_pieces[move_dir].set_reachable_squares(opp_dir, move_dir_reachable)
        if self._visible_pieces[opp_dir]:
            self._visible_pieces[opp_dir].set_reachable_squares(move_dir, opp_dir_reachable)

        if move_dir == "up" or move_dir == "down":                      # Update visible pieces in old and new row
            old_right = self._visible_pieces['right']
            old_left = self._visible_pieces['left']
            if old_right: old_right.set_visible_piece('left', old_left)
            if old_left: old_left.set_visible_piece('right', old_right)

            reachable_squares = self._reachable_squares['left'] | self._reachable_squares['right'] | {old_pos}
            if old_right: old_right.set_reachable_squares('left', reachable_squares)
            if old_left: old_left.set_reachable_squares('right', reachable_squares)

            right_piece_squares = {square for square in piece_dict if square[0] == new_pos[0] and square[1] > new_pos[1]}
            left_piece_squares = {square for square in piece_dict if square[0] == new_pos[0] and square[1] < new_pos[1]}
            if right_piece_squares:
                new_right = piece_dict.get(min(right_piece_squares))
            else:
                new_right = None
            if left_piece_squares:
                new_left = piece_dict.get(max(left_piece_squares))
            else:
                new_left = None
            self.set_visible_piece("right", new_right)
            self.set_visible_piece("left", new_left)
            if new_right: new_right.set_visible_piece("left", self)
            if new_left: new_left.set_visible_piece("right", self)

            right_reachable = self.build_square_string_range(new_pos, new_right)
            left_reachable = self.build_square_string_range(new_pos, new_left)
            if right_reachable: right_reachable = set(right_reachable[1:-1])
            if left_reachable: left_reachable = set(left_reachable[1:-1])
            self.set_reachable_squares('right', right_reachable)
            self.set_reachable_squares('left', left_reachable)
            if new_right: new_right.set_reachable_squares('left', right_reachable)
            if new_left: new_left.set_reachable_squares('right', left_reachable)

        elif move_dir == "left" or move_dir == "right":                 # Update visible pieces in old and new column
            old_down = self._visible_pieces['down']
            old_up = self._visible_pieces['up']
            if old_down: old_down.set_visible_piece('up', old_up)
            if old_up: old_up.set_visible_piece('down', old_down)
            reachable_squares = self._reachable_squares['up'] | self._reachable_squares['down'] | {old_pos}
            if old_down: old_down.set_reachable_squares('up', reachable_squares)
            if old_up: old_up.set_reachable_squares('down', reachable_squares)

            down_piece_squares = {square for square in piece_dict if
                                   square[1] == new_pos[1] and square[0] > new_pos[0]}
            up_piece_squares = {square for square in piece_dict if square[1] == new_pos[1] and square[0] < new_pos[0]}
            if down_piece_squares:
                new_down = piece_dict.get(min(down_piece_squares))
            else:
                new_down = None
            if up_piece_squares:
                new_up = piece_dict.get(max(up_piece_squares))
            else:
                new_up = None
            self.set_visible_piece("down", new_down)
            self.set_visible_piece("up", new_up)
            if new_down: new_down.set_visible_piece("up", self)
            if new_up: new_up.set_visible_piece("down", self)

            down_reachable = self.build_square_string_range(new_pos, new_down)
            up_reachable = self.build_square_string_range(new_pos, new_up)
            if down_reachable: down_reachable = set(down_reachable[1:-1])
            if up_reachable: up_reachable = set(up_reachable[1:-1])
            self.set_reachable_squares('down', down_reachable)
            self.set_reachable_squares('up', up_reachable)
            if new_down: new_down.set_reachable_squares('up', down_reachable)
            if new_up: new_up.set_reachable_squares('down', up_reachable)


class GameBoard(HasamiShogiUtilities):
    """Defines the methods for a Hasami Shogi game board. Used by HasamiShogiGame."""
    def __init__(self):
        """Initializes a 9x9 Hasami Shogi game board as a list of lists. Sets player positions."""
        super().__init__()
        self._black_starting_squares = {'i1', 'i2', 'i3', 'i4', 'i5', 'i6', 'i7', 'i8', 'i9'}
        self._red_starting_squares = {'a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8', 'a9'}
        self._squares = {"RED": self._red_starting_squares, "BLACK": self._black_starting_squares}
        self._squares["NONE"] = self._all_squares - self._squares["RED"] - self._squares["BLACK"]
        self._ind_squares = {square: color for color in self._squares for square in self._squares[color]}
        self._pieces = {
            "RED": {Piece("RED", square, self) for square in self._red_starting_squares},
            "BLACK": {Piece("BLACK", square, self) for square in self._black_starting_squares}
        }
        self._all_pieces = self._pieces["RED"] | self._pieces["BLACK"]
        self._square_piece_dict = {square: piece for square in self._all_squares for piece in self._all_pieces if piece.get_position() == square}
        for piece in self._all_pieces: piece.initialize_visible_piece()

    def get_board_list(self):
        """Returns the board as a list of lists."""
        return [[color for color in [self.get_square(ss) for ss in self._all_squares_in_order]][(9 * x):(9 * (x + 1))] for x in range(0, 9)]

    def get_all_squares(self):
        """Returns all possible squares of board as a set of square strings."""
        return self._all_squares

    def print_board(self):
        """Prints the current board with row/column labels. Abbreviates RED and BLACK and replaces NONE with '.'. """
        print("  " + " ".join(self._col_labels))
        for row in range(9):
            output_string = self._row_labels[row] + " "
            for square in self.get_board_list()[row]:
                if square == "NONE":
                    output_string += '. '
                else:
                    output_string += square[0] + " "
            print(output_string[:-1])

    def string_to_index(self, square_string):
        """Converts row/column string to row/column indices as a tuple, indexed at 0. Assumes valid input."""
        return self._row_labels.index(square_string[0]), self._col_labels.index(square_string[1])

    def index_to_string(self, row, column):
        """Converts row/column index (indexed at 0) to square string. Assumes valid input."""
        return self._row_labels[row] + self._col_labels[column]

    def get_square(self, square_string):
        """Given a square string, returns the value at that square."""
        return self._ind_squares[square_string]

    def set_square(self, square_string, square_value):
        """Sets the value of the given square to the given value."""
        if square_string not in self._all_squares or square_value not in {"RED", "BLACK", "NONE"}:
            return None
        self._ind_squares[square_string] = square_value

    def get_square_piece_dict(self):
        """Returns the dictionary of all occupied squares and their Piece objects."""
        return dict(self._square_piece_dict)

    def get_piece_at_square(self, square):
        """Returns the Piece object at the given square. Returns NONE if no piece at square."""
        return self._square_piece_dict.get(square, default="NONE")

    def set_square_piece(self, square, piece):
        """Sets the given square to the given piece."""
        self._square_piece_dict[square] = piece

    def del_square_piece(self, square):
        """Deletes the entry for the given square in the occupant dictionary."""
        del self._square_piece_dict[square]

    def move_piece(self, piece_loc, destination):
        """Moves the piece at the given location to the destination."""
        self._square_piece_dict[piece_loc].move_piece(destination)


class HasamiShogiGame:
    """Defines the methods for a game of Hasami Shogi."""
    def __init__(self):
        """Creates a new board, sets game state to UNFINISHED, active player to BLACK, captured pieces to 0."""
        self._game_board = GameBoard()
        self._game_state = "UNFINISHED"     # UNFINISHED, RED_WON, BLACK_WON
        self._active_player = "BLACK"       # BLACK, RED
        self._inactive_player = "RED"       # BLACK, RED
        self._captured_pieces = {"RED": 0, "BLACK": 0}
        self._all_squares = self._game_board.get_all_squares()

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
        piece_moving = self.get_square_occupant(moving_from)
        self.set_square_occupant(moving_to, piece_moving)
        self.set_square_occupant(moving_from, "NONE")

    def is_move_legal(self, moving_from, moving_to):
        """Checks if move from first square to second is legal. Returns True if so, False if not."""
        if self.get_game_state() != "UNFINISHED":                                     # Game is finished
            return False

        if moving_from not in self._all_squares or moving_to not in self._all_squares:              # Out of range
            return False

        if self.get_square_occupant(moving_from) != self.get_active_player():         # Wrong color
            return False

        if moving_from[0] != moving_to[0] and moving_from[1] != moving_to[1]:         # Not pure vertical or horizontal
            return False

        if moving_from == moving_to:                                                  # Same square
            return False

        move_path = self.get_game_board().build_square_string_range(moving_from, moving_to)
        return False not in {self.get_square_occupant(x) == "NONE" for x in move_path[1:]}    # Check for clear path.

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
            self.set_square_occupant(captured, "NONE")

    def find_closest_corner(self, moved_to):
        """Finds the closest corner to the new square to check for corner capture."""
        closest_corner = ""
        square_row, square_column = self.get_game_board().string_to_index(moved_to)
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
                    self.set_square_occupant(closest_corner, "NONE")
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
    new_board = GameBoard()
    new_board.move_piece('i6', 'e6')
    pass

if __name__ == '__main__':
    # cProfile.run('main()', sort='cumtime')
    main()
