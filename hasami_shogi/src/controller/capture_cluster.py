class CaptureCluster:

    def __init__(self, squares: dict):
        self.squares: dict = squares
        self.color: str = squares.values()[0]
        self.lower_occ, self.upper_occ = min(squares), max(squares)
        self.lower_free, self.upper_free = None

        self.validation()
        self.find_lower_free()
        self.find_upper_free()

    def validation(self):
        if [val for val in self.squares.values() if val != self.color]:
            raise ValueError(f"Squares must be all same color: {self.squares}")
        if [sq for sq in self.squares if sq[0] != self.lower_occ[0]] and [sq for sq in self.squares if sq[1] != self.lower_occ[1]]:
            raise ValueError(f"Squares must be all in one line: {self.squares}")

    def raise_if_bad_square(self, square: str) -> None:
        if square not in self.squares:
            raise ValueError(f"{square} not in self.squares {self.squares}")

    def find_lower_free(self):
        """Set self.lower_free"""
        raise NotImplementedError

    def find_upper_free(self):
        """Set self.upper_free"""
        raise NotImplementedError

    def update_lower_occ(self):
        self.lower_occ = min(self.squares)

    def update_upper_occ(self):
        self.upper_occ = max(self.squares)

    def remove(self, square: str) -> None:
        self.raise_if_bad_square(square)
        if len(self.squares) == 1:
            return []

        curr_squares = list(self.squares.keys())
        del self.squares[square]

        # Case: square is min
        if square == self.lower_occ:
            self.lower_free = square
            self.update_lower_occ()
            return [self]

        # Case: square is max
        if square == self.upper_occ:
            self.upper_free = square
            self.update_upper_occ()
            return [self]

        # Case: square between min and max
        lower_squares = curr_squares[:curr_squares.index(square)]
        upper_squares = curr_squares[curr_squares.index(square) + 1:]
        return [type(self)(lower_squares), type(self)(upper_squares)]


class VerticalCaptureCluster(CaptureCluster):
    def find_lower_free(self):
        if self.lower_free == "":
            return
        row, col = self.lower_occ
        prev_row = chr(ord(row) - 1)
        self.lower_free = prev_row + col if "a" <= prev_row <= "i" else ""

    def find_upper_free(self):
        if self.upper_free == "":
            return
        row, col = self.upper_occ
        next_row = chr(ord(row) + 1)
        self.upper_free = next_row + col if "a" <= next_row <= "i" else ""

class HorizontalCaptureCluster(CaptureCluster):
    def find_lower_free(self):
        if self.lower_free == "":
            return
        row, col = self.lower_occ
        prev_col = chr(ord(col) - 1)
        self.lower_free = row + prev_col if "1" <= prev_col <= "9" else ""

    def find_upper_free(self):
        if self.upper_free == "":
            return
        row, col = self.upper_occ
        next_col = chr(ord(col) + 1)
        self.upper_free = row + next_col if "1" <= next_col <= "9" else ""
