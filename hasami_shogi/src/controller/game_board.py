import hasami_shogi.src.controller.hasami_shogi_utilities as utils


class GameBoard:
    """Defines the methods for a Hasami Shogi game board. Used by HasamiShogiGame."""

    RED_START = {'a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8', 'a9'}
    BLACK_START = {'i1', 'i2', 'i3', 'i4', 'i5', 'i6', 'i7', 'i8', 'i9'}

    def __init__(self):
        """
        Initializes a Hasami Shogi game board and sets player positions.
        """
        self.square_values = {square: "NONE" for row in utils.BOARD for square in row} \
            | {square: "RED" for square in GameBoard.RED_START} \
            | {square: "BLACK" for square in GameBoard.BLACK_START}

    def get_squares_by_color(self, seeking_color):
        return {square for square, color in self.square_values.items() if color == seeking_color}

    def get_board_list(self):
        """Returns the board as a list of lists."""
        return [[self.get_square(square) for square in row] for row in utils.BOARD]

    def get_all_squares(self):
        """Returns all possible squares of board as a set of square strings."""
        return set(self.square_values.keys())

    def print_board(self):
        """Prints the current board with row/column labels. Abbreviates RED and BLACK and replaces NONE with '.'. """
        print("  " + " ".join(utils.COL_LABELS))
        for row in range(9):
            output_string = utils.ROW_LABELS[row] + " "
            for square in self.get_board_list()[row]:
                if square == "NONE":
                    output_string += '. '
                else:
                    output_string += square[0] + " "
            print(output_string[:-1])

    def get_square(self, square_string):
        """Given a square string, returns the value at that square."""
        return self.square_values[square_string]

    def set_square(self, square_string, square_value):
        """Sets the value of the given square to the given value."""
        if square_string not in self.square_values or square_value not in {"RED", "BLACK", "NONE"}:
            return None
        self.square_values[square_string] = square_value
