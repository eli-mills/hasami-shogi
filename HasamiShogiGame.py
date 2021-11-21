# Author: Eli Mills
# Date: 11/21/2021
# Description: Portfolio Project - Hasami Shogi

class HasamiShogiBoard:
    """Defines the template for a game board. Used by HasamiShogiGame."""
    def __init__(self):
        """Initializes a new board object. Begins as a completely empty board."""
        self._column_labels = tuple(str(number) for number in range(1, 10))
        self._row_labels = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i')
        self._board = [['.']*9]*9
        self._board[0] = ['R']*9
        self._board[8] = ['B']*9

    def convert_str_to_coords(self, square_string):
        """Takes a row-column string and returns the proper list coordinates as a tuple."""
        row = self._row_labels.index(square_string[0])
        column = int(square_string[1])
        return row, column

    def get_square(self, square_string):
        """Returns the value at the specified square. Takes row-column string."""
        row, column = self.convert_str_to_coords(square_string)
        return self._board[row][column]

    def set_square(self, square_string, square_value):
        """Sets the square at the position in the given row-col string to the given value."""
        row, column = self.convert_str_to_coords(square_string)
        self._board[row][column] = square_value

    def get_board(self):
        """Returns the current game board as a list of row lists."""
        return self._board

    def print_board(self):
        """Prints out the current board."""
        print('  ' + ' '.join(self._column_labels))
        for row in range(9):
            print(self._row_labels[row] + ' ' + ' '.join(self._board[row]))


class HasamiShogiGame:
    """Defines the methods for playing a game of Hasami Shogi."""
    def __init__(self):
        """Initializes a Hasami Shogi Game by setting up and preparing the board and pieces."""
        pass

    def get_game_state(self):
        """Returns the current state of the game: UNFINISHED, RED_WON, or BLACK_WON."""
        pass

    def get_active_player(self):
        """Returns which player's turn it is: RED or BLACK."""
        pass

    def get_num_captured_pieces(self, player_color):
        """Returns the number of captured pieces of the given color, RED or BLACK."""
        pass

    def get_square_occupant(self, square):
        """Returns the color of the piece on the given square, or NONE if empty."""
        pass

    def make_move(self, moved_from, moving_to):
        """If allowed, makes the given move, updates the game state, and returns True. Returns False if not possible"""
        pass


def main():
    new_board = HasamiShogiBoard()
    new_board.print_board()


if __name__ == '__main__':
    main()

