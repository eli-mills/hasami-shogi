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

    def get_range(self, square_string_from, square_string_to):
        """Returns a list of all squares from square 1 to square 2 (inclusive). Assumes indices in range."""
        coords_from = self.string_to_index(square_string_from)
        coords_to = self.string_to_index(square_string_to)
        direction = 1
        if coords_from[1] == coords_to[1]:
            direction -= 1                                   # Return column section if not row.
        coords_list = list(coords_from)
        output_values = []
        search_start = min(coords_from[direction], coords_to[direction])
        search_end = max(coords_from[direction], coords_to[direction])
        for index in range(search_start, search_end + 1):
            current_square = self.index_to_string(*coords_list)
            output_values.append(self.get_square(current_square))
            if coords_from[direction] <= coords_to[direction]:
                coords_list[direction] += 1
            else:
                coords_list[direction] -= 1
        return output_values


class HasamiShogiGame:
    """Defines the methods for a game of Hasami Shogi."""
    def __init__(self):
        """Creates a new board, sets game state to UNFINISHED, active player to BLACK, captured pieces to 0."""
        self._game_board = GameBoard()
        self._game_state = "UNFINISHED"     # UNFINISHED, RED_WON, BLACK_WON
        self._active_player = "BLACK"       # BLACK, RED
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
        self._active_player = {"BLACK": "RED", "RED": "BLACK"}[self._active_player]

    def get_num_captured_pieces(self, player_color):
        """Returns the number of captured pieces of the given color."""
        return self._captured_pieces[player_color]

    def add_num_captured_pieces(self, player_color, num_captured):
        """Adds the given number to the captured pieces of the given color."""
        self._captured_pieces[player_color] += num_captured

    def get_square_occupant(self, square_string):
        """Returns the value at the given square on the board: RED, BLACK, or NONE."""
        return self.get_game_board().get_square(square_string)

    def execute_move(self, moving_from, moving_to):
        """(Blindly) moves the piece at the first position to the second position."""
        piece_moving = self.get_square_occupant(moving_from)
        self.get_game_board().set_square(moving_to, piece_moving)
        self.get_game_board().set_square(moving_from, "NONE")

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
        move_path = self.get_game_board().get_range(moving_from, moving_to)
        return all([x == "NONE" for x in move_path[1:]]) # Check for clear path.



    def make_move(self, moving_from, moving_to):
        """Moves from first square to second and returns True if legal, then updates game variables accordingly."""
        if not self.is_move_legal(moving_from, moving_to):
            return False
        self.execute_move(moving_from, moving_to)
        self.toggle_active_player()
        return True


def main():
    new_game = HasamiShogiGame()
    while new_game.get_game_state() == "UNFINISHED":
        new_game.get_game_board().print_board()
        print('\n'*5)
        print(new_game.get_active_player() + "'s Move \n")
        player_move = input("Enter move: ")[:4]
        print('\n'*20)
        print(new_game.make_move(player_move[:2], player_move[2:]))




if __name__ == "__main__":
    main()