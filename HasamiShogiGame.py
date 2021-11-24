# Author: Eli Mills
# Date: 11/21/2021
# Description: Portfolio Project - Hasami Shogi

class HasamiShogiBoard:
    """Defines the template for a game board. Used by HasamiShogiGame."""
    def __init__(self):
        """Initializes a new board object. Begins as a completely empty board."""
        self._column_labels = tuple(str(number) for number in range(1, 10))
        self._row_labels = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i')
        self._board = [['NONE']*9]*9
        self._board[0] = ['RED']*9
        self._board[8] = ['BLACK']*9

    def convert_str_to_index(self, square_string):
        """Takes a row-column string and returns the proper list coordinates as a tuple."""
        row = self._row_labels.index(square_string[0].lower())
        column = int(square_string[1]) - 1
        return row, column

    def convert_index_to_str(self, row_index, col_index):
        """Returns a square string based on the given row and column indices."""
        row_string = self._row_labels[row_index]
        col_string = str(col_index + 1)
        return row_string + col_string

    def get_board(self):
        """Returns the current game board as a list of row lists."""
        return self._board

    def get_square(self, square_string):
        """Returns the value at the specified square. Takes row-column string."""
        row, column = self.convert_str_to_index(square_string)
        return self.get_board()[row][column]

    def get_square_by_index(self, row, column):
        """Returns the value at the specified square coordinates."""
        return self.get_board()[row][column]

    def set_square(self, square_string, square_value):
        """Sets the square at the position in the given row-col string to the given value."""
        row, column = self.convert_str_to_index(square_string)
        self.get_board()[row][column] = square_value

    def print_board(self):
        """Prints out the current board."""
        print('  ' + ' '.join(self._column_labels))
        for row in range(9):
            output_row = self._row_labels[row] + " "
            for square in self.get_board()[row]:
                if square == "NONE":
                    output_row += '. '
                else:
                    output_row += square[0] + ' '
            print(output_row[0:-1])

    def get_range(self, square_string1, square_string2):
        """Returns a list representing squares from square 1 to square 2, if a column or row."""
        row1, col1 = self.convert_str_to_index(square_string1)
        row2, col2 = self.convert_str_to_index(square_string2)
        output_range = []
        if row1 != row2 and col1 != col2:
            return None
        if row1 == row2:
            for column in range(min(col1, col2), max(col1, col2) + 1):
                output_range.append(self._board[row1][column])
            return output_range[::-1] if col2 < col1 else output_range
        if col1 == col1:
            for row in range(min(row1, row2), max(row1, row2) + 1):
                output_range.append(self._board[row][col1])
            return output_range[::-1] if row2 < row1 else output_range


class HasamiShogiGame:
    """Defines the methods for playing a game of Hasami Shogi."""
    def __init__(self):
        """Initializes a Hasami Shogi Game by creating a new board and state variables."""
        self._game_board = HasamiShogiBoard()
        self._game_state = 'UNFINISHED'
        self._active_player = 'BLACK'
        self._captured_pieces = {'BLACK': 0, 'RED': 0}

    def get_game_state(self):
        """Returns the current state of the game: UNFINISHED, RED_WON, or BLACK_WON."""
        return self._game_state

    def set_game_state(self, game_state):
        """Sets the game state to the given value."""
        self._game_state = game_state

    def get_active_player(self):
        """Returns which player's turn it is: RED or BLACK."""
        return self._active_player

    def toggle_active_player(self):
        """Switches the active player."""
        if self.get_active_player() == "BLACK":
            self._active_player = "RED"
        else:
            self._active_player = "BLACK"

    def get_game_board(self):
        """Returns the current game board object."""
        return self._game_board

    def get_num_captured_pieces(self, player_color):
        """Returns the number of captured pieces of the given color, RED or BLACK."""
        return self._captured_pieces[player_color]

    def add_captured_pieces(self, player_color, amount):
        """Adds the given amount to the overall count of the given player's captured pieces."""
        self._captured_pieces[player_color] += amount

    def get_square_occupant(self, square_string):
        """Returns the color of the piece on the given square, or NONE if empty."""
        return self.get_game_board().get_square(square_string)

    def get_square_occupant_by_index(self, row, column):
        """Returns the color of the piece on the given square, or NONE if empty."""
        return self.get_game_board().get_square_by_index(row, column)

    def set_square_occupant(self, square_string, square_value):
        """Sets the specified square of the game board to the specified value."""
        self.get_game_board().set_square(square_string, square_value)

    def is_move_legal(self, moved_from, moving_to):
        """Checks if the attempted move is legal. Returns True or False accordingly."""
        try:
            if self.get_square_occupant(moved_from) != self.get_active_player():    # Check correct player moved.
                return False
            if self.get_square_occupant(moving_to) != "NONE":                       # Check that space is available.
                return False
            if moved_from[0] != moving_to[0] or moved_from[1] != moving_to[1]:      # Illegal direction.
                return False
            for space in self.get_game_board().get_range(moved_from, moving_to)[1:-1]:
                if space != "NONE":
                    return False
            return True
        except IndexError:
            return False

    def check_linear_capture(self, moved_to, direction):
        """Checks the newly-moved piece for horizontal (1) or vertical (0) captures, depending on given direction."""
        square_coordinates = self.get_game_board().convert_str_to_index(moved_to)
        square_to_check = list(square_coordinates)
        color = ["BLACK", "RED"]
        color.remove(self.get_active_player())
        color = color[0]
        captured_squares = []

        if square_to_check[direction] + 1 < 9:
            square_to_check[direction] += 1
            while square_to_check[direction] + 1 < 9 and self.get_square_occupant_by_index(*square_to_check) == color:
                captured_squares.append(tuple(square_to_check))
                square_to_check[direction] += 1
            if self.get_square_occupant_by_index(*square_to_check) == self.get_active_player():
                self.add_captured_pieces(color, len(captured_squares))
                for coords in captured_squares:
                    square_string = self.get_game_board().convert_index_to_str(*coords)
                    self.set_square_occupant(square_string, "NONE")

    def check_corner_capture(self, moved_to):
        pass

    def did_move_capture(self, moved_to):
        """Checks if the move just made caused a capture. Returns True or False accordingly."""
        corner_spaces = {'a2', 'a8', 'b1', 'b9', 'h1', 'h9', 'i2', 'i8'}
        self.check_linear_capture(moved_to, 0)
        self.check_linear_capture(moved_to, 1)
        if moved_to in corner_spaces:
            self.check_corner_capture(moved_to)

    def did_move_win(self):
        """Checks if opponent has one or no pieces remaining."""
        win_states = {"BLACK": "RED_WON", "RED": "BLACK_WON"}
        current_player = self.get_active_player()
        if self.get_num_captured_pieces(current_player) > 7:
            self.set_game_state(win_states[current_player])

    def execute_move(self, moved_from, moving_to):
        """Moves the piece to the new square."""
        piece_color = self.get_square_occupant(moved_from)
        self.set_square_occupant(moved_from, "NONE")
        self.set_square_occupant(moving_to, piece_color)


    def make_move(self, moved_from, moving_to):
        """If allowed, makes the given move, updates the game state, and returns True. Returns False if not possible"""
        if self.is_move_legal(moved_from, moving_to):
            self.execute_move(moved_from, moving_to)
            self.did_move_capture(moving_to)
            self.did_move_win()
            return True
        return False


def main():
    new_game = HasamiShogiGame()
    while new_game.get_game_state() == "UNFINISHED":
        new_game.get_game_board().print_board()
        move_from = input("Piece to move: ")
        move_to = input("Move to: ")
        new_game.make_move(move_from, move_to)
    new_game.get_game_board().print_board()
    print(new_game.get_game_state())



if __name__ == '__main__':
    main()

