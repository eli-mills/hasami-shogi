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

    def get_square(self, square_string):
        """Returns the value at the specified square. Takes row-column string."""
        row, column = self.convert_str_to_index(square_string)
        return self._board[row][column]

    def set_square(self, square_string, square_value):
        """Sets the square at the position in the given row-col string to the given value."""
        row, column = self.convert_str_to_index(square_string)
        self._board[row][column] = square_value

    def get_board(self):
        """Returns the current game board as a list of row lists."""
        return self._board

    def print_board(self):
        """Prints out the current board."""
        print('  ' + ' '.join(self._column_labels))
        for row in range(9):
            print(self._row_labels[row] + ' ' + ' '.join(self._board[row]))

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

    def get_square_occupant(self, square_string):
        """Returns the color of the piece on the given square, or NONE if empty."""
        return self._game_board.get_square(square_string)

    def set_square_occupant(self, square_string, square_value):
        """Sets the specified square of the game board to the specified value."""
        self._game_board.set_square(square_string, square_value)

    def is_move_legal(self, moved_from, moving_to):
        """Checks if the attempted move is legal. Returns True or False accordingly."""
        try:
            if self.get_square_occupant(moved_from) != self.get_active_player():    # Check correct player moved.
                return False
            if self.get_square_occupant(moving_to) != "NONE":                       # Check that space is available.
                return False
            if moved_from[0] != moving_to[0] or moved_from[1] != moving_to[1]:      # Illegal direction.
                return False
        except IndexError:
            return False



    def did_move_capture(self, moved_to):
        """Checks if the move just made caused a capture. Returns True or False accordingly."""
        pass

    def did_move_win(self):
        """Checks if opponent has one or no pieces remaining."""
        pass

    def execute_move(self, moved_from, moving_to):
        """Moves the piece to the new square."""
        pass

    def execute_capture(self, moved_to):
        """Removes the captured pieces and updates the captured amounts."""

    def make_move(self, moved_from, moving_to):
        """If allowed, makes the given move, updates the game state, and returns True. Returns False if not possible"""
        if self.is_move_legal(moved_from, moving_to):
            self.execute_move()
            if self.did_move_capture(moving_to):
                self.execute_capture(moving_to)
                if self.did_move_win():
                    pass
            return True
        return False


def main():
    new_board = HasamiShogiBoard()
    new_board.print_board()
    print(new_board.convert_str_to_index('c5'))
    print(new_board.get_square('i6'))
    print(new_board.get_square('f5'))
    print(new_board.get_range('i1', 'a1'))


if __name__ == '__main__':
    main()

