# Author: Eli Mills
# Date: 11/25/2021
# Description: Portfolio Project - Hasami Shogi

class GameBoard:
    """Defines the methods for a Hasami Shogi game board. Used by HasamiShogiGame."""
    def __init__(self):
        """Initializes a 9x9 Hasami Shogi game board as a list of lists. Sets player positions."""
        self._board = [["NONE" for x in range(9)] for x in range(9)]
        self._board[0] = ["RED" for x in range(9)]
        self._board[8] = ["BLACK" for x in range(9)]
        self._row_labels = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']
        self._col_labels = ['1', '2', '3', '4', '5', '6', '7', '8', '9']

    def get_board_list(self):
        """Returns the board as a list of lists."""
        return self._board

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
        """Converts the given row/column string to row/column indices as a tuple, indexed at 0."""
        return self._row_labels.index(square_string[0]), self._col_labels.index(square_string[1])

    def index_to_string(self, row, column):
        """Returns a square string generated from the given row and column index (indexed at 0)."""
        return self._row_labels[row] + self._col_labels[column]

    def get_square(self, square_string):
        """Given a square string, returns the value at that square."""
        row, column = self.string_to_index(square_string)
        return self.get_board_list()[row][column]

    def set_square(self, square_string, square_value):
        """Sets the value of the given square to the given value."""
        row, column = self.string_to_index(square_string)
        self.get_board_list()[row][column] = square_value

    def build_square_string_range(self, square_string_from, square_string_to):
        """Returns a list of square strings from the first square to the second. Range cannot be diagonal."""
        row_from, col_from = self._row_labels.index(square_string_from[0]), int(square_string_from[1])-1
        row_to, col_to = self._row_labels.index(square_string_to[0]), int(square_string_to[1])-1
        row_min, row_max = min(row_to, row_from), max(row_to, row_from)
        col_min, col_max = min(col_to, col_from), max(col_to, col_from)
        row_range, col_range = range(row_min, row_max + 1), range(col_min, col_max + 1)
        output_range = []
        for row_index in row_range:
            for col_index in col_range:
                output_range.append(self._row_labels[row_index] + self._col_labels[col_index])
        return output_range if row_from <= row_to and col_from <= col_to else output_range[::-1]


class HasamiShogiGame:
    """Defines the methods for a game of Hasami Shogi."""
    def __init__(self):
        """Creates a new board, sets game state to UNFINISHED, active player to BLACK, captured pieces to 0."""
        self._game_board = GameBoard()
        self._game_state = "UNFINISHED"     # UNFINISHED, RED_WON, BLACK_WON
        self._active_player = "BLACK"       # BLACK, RED
        self._inactive_player = "RED"
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
        piece_moving = self.get_square_occupant(moving_from)
        self.set_square_occupant(moving_to, piece_moving)
        self.set_square_occupant(moving_from, "NONE")

    def is_move_legal(self, moving_from, moving_to):
        """Checks if move from first square to second is legal. Returns True if so, False if not."""
        allowed_rows = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']
        allowed_cols = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
        if moving_from[0] not in allowed_rows or moving_to[0] not in allowed_rows:    # Row out of range
            return False
        if moving_from[1] not in allowed_cols or moving_to[1] not in allowed_cols:    # Column out of range
            return False

        if self.get_square_occupant(moving_from) != self.get_active_player():         # Wrong color
            return False

        if moving_from[0] != moving_to[0] and moving_from[1] != moving_to[1]:         # Not pure vertical or horizontal
            return False

        if moving_from == moving_to:                                                  # Same square
            return False

        move_path = self.get_game_board().build_square_string_range(moving_from, moving_to)
        return all([self.get_square_occupant(x) == "NONE" for x in move_path[1:]])    # Check for clear path.

    def find_captured_squares(self, from_square, to_square):
        """Finds capture pattern in given square string range. Returns captured squares if found, else False."""
        capturing_color = self.get_square_occupant(from_square)
        captured_color = {"RED": "BLACK", "BLACK": "RED"}[capturing_color]
        square_string_list = self.get_game_board().build_square_string_range(from_square, to_square)  # Square strings
        square_value_list = [self.get_square_occupant(x) for x in square_string_list]                 # Values on board
        for index, square_value in enumerate(square_value_list[1:]):
            if square_value == capturing_color:
                if index == 0:
                    return False
                end_cap = square_string_list[1:][index]
                return self.get_game_board().build_square_string_range(from_square, end_cap)[1:-1]
            if square_value != captured_color:
                return False

    def check_linear_captures(self, moved_to):
        """Searches four directions around latest move, captures pieces, and updates capture counts. Returns False if no capture."""
        left_limit = moved_to[0] + '1'
        right_limit = moved_to[0] + '9'
        top_limit = 'a' + moved_to[1]
        bottom_limit = 'i' + moved_to[1]
        search_directions = [left_limit, right_limit, top_limit, bottom_limit]
        captured_lists = [self.find_captured_squares(moved_to, limit) for limit in search_directions]
        captured_squares = [square for sublist in captured_lists if sublist for square in sublist]
        self.add_num_captured_pieces(self._inactive_player, len(captured_squares))
        for captured in captured_squares:
            self.set_square_occupant(captured, "NONE")
        return any(captured_lists)

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
        capture_scenarios = {
            "a1": ["a2", "b1"],
            "a9": ["a8", "b9"],
            "i1": ["h1", "i2"],
            "i9": ["h9", "i8"]
        }

        closest_corner = self.find_closest_corner(moved_to)

        if closest_corner in capture_scenarios:
            if moved_to in capture_scenarios[closest_corner]:
                moved_to_index = capture_scenarios[closest_corner].index(moved_to)
                capturing_end = capture_scenarios[closest_corner][moved_to_index - 1]
                moved_to_color = self.get_square_occupant(moved_to)
                captured_color = self.get_square_occupant(closest_corner)
                capturing_end_color = self.get_square_occupant(capturing_end)
                if moved_to_color == capturing_end_color and captured_color == self._inactive_player:
                    self.set_square_occupant(closest_corner, "NONE")
                    self.add_num_captured_pieces(self._inactive_player, 1)

    def check_win(self):
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


def play_game():
    new_game = HasamiShogiGame()
    while new_game.get_game_state() == "UNFINISHED":
        new_game.get_game_board().print_board()
        print('*' * 100 + '\n')
        print(new_game.get_active_player() + "'s Move")
        print("Captured pieces:")
        print("BLACK:", new_game.get_num_captured_pieces("BLACK"), "RED:", new_game.get_num_captured_pieces("RED"))
        print('\n')
        player_move = input("Enter move: ")[:4]
        print('\n' * 20)
        print(new_game.make_move(player_move[:2], player_move[2:]))
    print(new_game.get_game_state())


def main():
    new_game = HasamiShogiGame()
    print(new_game.is_move_legal("i1", "i1"))

if __name__ == "__main__":
    main()
