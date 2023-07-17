import hasami_shogi.src.model.hasami_shogi_utilities as utils


class GameBoard:
    """Defines the methods for a Hasami Shogi game board. Used by HasamiShogiGame."""

    RED_START = {'a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8', 'a9'}
    BLACK_START = {'i1', 'i2', 'i3', 'i4', 'i5', 'i6', 'i7', 'i8', 'i9'}

    @staticmethod
    def opposite_color(color):
        """Returns RED if BLACK, and vice versa."""
        return {"RED": "BLACK", "BLACK": "RED"}[color]

    @staticmethod
    def find_closest_corner(square):
        """Finds the closest corner to the new square to check for corner capture."""
        closest_corner = ""
        row, col = square
        if row in {"a", "b"}:
            closest_corner += "a"
        elif row in {"h", "i"}:
            closest_corner += "i"
        if col in {"1", "2"}:
            closest_corner += "1"
        elif col in {"8", "9"}:
            closest_corner += "9"
        return closest_corner

    def __init__(self):
        """
        Initializes a Hasami Shogi game board and sets player positions.
        """
        self.square_values = {square: "NONE" for row in utils.BOARD for square in row} \
            | {square: "RED" for square in GameBoard.RED_START} \
            | {square: "BLACK" for square in GameBoard.BLACK_START}

    def get_square(self, square: str) -> str:
        """Given a square string, returns the value at that square."""
        return self.square_values[square]

    def set_square(self, square: str, square_value: str) -> None:
        """Sets the value of the given square to the given value."""
        if square not in self.square_values or square_value not in {"RED", "BLACK", "NONE"}:
            return None
        self.square_values[square] = square_value

    def get_squares_by_color(self, seeking_color: str) -> set[str]:
        """
        Returns set of squares belonging to the given color.
        """
        return {square for square, color in self.square_values.items() if color == seeking_color}

    def get_squares_by_axis(self, axis: str) -> list[str]:
        """
        Returns list of all squares in the given row or column.
        """
        return [square for square in self.square_values.keys() if axis in square]

    def get_occupied_squares_by_axis(self, axis: str) -> list[str]:
        """
        Returns sorted list of all squares that are occupied in the given row or column.
        """
        return [square for square, value in self.square_values.items() if axis in square and value != "NONE"]

    def get_free_squares_by_axis(self, axis: str) -> list[str]:
        """
        Returns sorted list of all squares that are free in the given row or column.
        """
        return [square for square, value in self.square_values.items() if axis in square and value == "NONE"]

    def get_all_squares(self) -> set[str]:
        """Returns all possible squares of board as a set of square strings."""
        return set(self.square_values.keys())

    def get_board_list(self) -> list[list[str]]:
        """Returns the board as a list of lists of square values."""
        return [[self.get_square(square) for square in row] for row in utils.BOARD]

    def print_board(self) -> None:
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

    def serialize_board(self) -> str:
        """
        Returns the current RED and BLACK squares as a string.
        """
        red_list = sorted(list(self.get_squares_by_color("RED")))
        black_list = sorted(list(self.get_squares_by_color("BLACK")))
        red_list.insert(0, "r")
        black_list.insert(0, "b")
        red_list.extend(black_list)
        return "".join(red_list)

