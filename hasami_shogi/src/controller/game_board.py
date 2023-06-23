class GameBoard:
    """Defines the methods for a Hasami Shogi game board. Used by HasamiShogiGame."""
    def __init__(self):
        """
        Initializes a 9x9 Hasami Shogi game board as a list of lists. Sets player positions. Optional
        default GameBoard object.
        """
        self._row_labels = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']
        self._col_labels = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
        self._all_squares_in_order = [row + col for row in self._row_labels for col in self._col_labels]
        self._all_squares = set(self._all_squares_in_order)

        # Initialize game board
        self._board = [["NONE" for x in range(9)] for x in range(9)]
        self._board[0] = ["RED" for x in range(9)]
        self._board[8] = ["BLACK" for x in range(9)]

        self.squares_by_color = {
            "RED": {'a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8', 'a9'},
            "BLACK": {'i1', 'i2', 'i3', 'i4', 'i5', 'i6', 'i7', 'i8', 'i9'}
        }
        self.square_values = {square: "NONE" for square in self._all_squares}
        self.square_values |= {square: color for color in self.squares_by_color for square in self.squares_by_color[
            color]}

    def get_squares_by_color(self, color):
        try:
            return set(self.squares_by_color[color])
        except KeyError as e:
            raise KeyError("get_squares_by_color was provided a color other than RED or BLACK") from e

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
        return self.square_values[square_string]

    def set_square(self, square_string, square_value):
        """Sets the value of the given square to the given value."""
        if square_string not in self._all_squares or square_value not in {"RED", "BLACK", "NONE"}:
            return None
        current_value = self.square_values[square_string]
        if current_value in {"RED", "BLACK"}:
            self.squares_by_color[current_value].remove(square_string)
        self.square_values[square_string] = square_value
        if square_value in {"RED", "BLACK"}:
            self.squares_by_color[square_value].add(square_string)

    def build_square_string_range(self, square_string_from, square_string_to):
        """Returns list of square strings from first square to second. Range cannot be diagonal. Assumes valid input."""
        # 1. Convert square strings to indices.
        row_from, col_from = self._row_labels.index(square_string_from[0]), int(square_string_from[1])-1
        row_to, col_to = self._row_labels.index(square_string_to[0]), int(square_string_to[1])-1

        # 2. Generate ranges. There should be exactly one range of length 0.
        row_min, row_max = min(row_to, row_from), max(row_to, row_from)
        col_min, col_max = min(col_to, col_from), max(col_to, col_from)
        row_range, col_range = range(row_min, row_max + 1), range(col_min, col_max + 1)

        # 3. Generate list of square strings from ranges. Reverse output if necessary.
        output_range = []
        for row_index in row_range:
            for col_index in col_range:
                output_range.append(self._row_labels[row_index] + self._col_labels[col_index])
        return output_range if row_from <= row_to and col_from <= col_to else output_range[::-1]
