import hasami_shogi.src.controller.hasami_shogi_utilities as utils


class GameBoard:
    """Defines the methods for a Hasami Shogi game board. Used by HasamiShogiGame."""

    def __init__(self):
        """
        Initializes a 9x9 Hasami Shogi game board as a list of lists. Sets player positions. Optional
        default GameBoard object.
        """
        self.squares_by_color = {
            "RED": {'a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8', 'a9'},
            "BLACK": {'i1', 'i2', 'i3', 'i4', 'i5', 'i6', 'i7', 'i8', 'i9'}
        }
        self.square_values = {square: "NONE" for row in utils.BOARD for square in row}
        self.square_values |= {square: color for color in self.squares_by_color for square in self.squares_by_color[
            color]}

    def get_squares_by_color(self, color):
        try:
            return set(self.squares_by_color[color])
        except KeyError as e:
            raise KeyError("get_squares_by_color was provided a color other than RED or BLACK") from e

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
        current_value = self.square_values[square_string]
        if current_value in {"RED", "BLACK"}:
            self.squares_by_color[current_value].remove(square_string)
        self.square_values[square_string] = square_value
        if square_value in {"RED", "BLACK"}:
            self.squares_by_color[square_value].add(square_string)
