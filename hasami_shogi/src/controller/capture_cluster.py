class CaptureCluster:

    def __init__(self, squares: dict):
        self.squares: dict = squares
        self.color: str = squares.values()[0]
        self.lower_occ, self.upper_occ = min(squares), max(squares)
        self.lower_border = self.upper_border = None

        self.validation()
        self.find_lower_border()
        self.find_upper_border()

    def __len__(self):
        return len(self.squares)

    def __repr__(self):
        return set(self.squares)

    def validation(self):
        if [val for val in self.squares.values() if val != self.color]:
            raise ValueError(f"Squares must be all same color: {self.squares}")
        if [sq for sq in self.squares if sq[0] != self.lower_occ[0]] and [sq for sq in self.squares if sq[1] != self.lower_occ[1]]:
            raise ValueError(f"Squares must be all in one line: {self.squares}")

    def raise_if_bad_square(self, square: str) -> None:
        if square not in self.squares:
            raise ValueError(f"{square} not in self.squares {self.squares}")

    def merge_validation(self, merging_cluster: "CaptureCluster"):
        if self.upper_occ != merging_cluster.lower_border and self.upper_occ != merging_cluster.lower_border:
            raise ValueError(f"Cannot merge the two clusters: {self} {merging_cluster}")
        if type(self) != type(merging_cluster):
            raise ValueError(f"Cannot merge two clusters of different type: {self} {merging_cluster}")
        if self.color != merging_cluster.color:
            raise ValueError(f"Cannot merge two clusters of different color: {self} {merging_cluster}")

    def find_lower_border(self):
        """Set self.lower_border"""
        raise NotImplementedError

    def find_upper_border(self):
        """Set self.upper_border"""
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
            self.lower_border = square
            self.update_lower_occ()
            return [self]

        # Case: square is max
        if square == self.upper_occ:
            self.upper_border = square
            self.update_upper_occ()
            return [self]

        # Case: square between min and max
        lower_squares = curr_squares[:curr_squares.index(square)]
        upper_squares = curr_squares[curr_squares.index(square) + 1:]
        return [type(self)(lower_squares), type(self)(upper_squares)]

    def merge(self, merging_cluster: "CaptureCluster") -> "CaptureCluster":
        self.squares |= merging_cluster.squares
        self.lower_occ = min(self.lower_occ, merging_cluster.lower_occ)
        self.upper_occ = max(self.upper_occ, merging_cluster.upper_occ)
        self.find_upper_border()
        self.find_lower_border()
        return self

    def get_border_squares(self) -> set[str]:
        return {sq for sq in {self.lower_border, self.upper_border} if sq}


class VerticalCaptureCluster(CaptureCluster):
    def find_lower_border(self):
        if self.lower_border == "":
            return
        row, col = self.lower_occ
        prev_row = chr(ord(row) - 1)
        self.lower_border = prev_row + col if "a" <= prev_row <= "i" else ""

    def find_upper_border(self):
        if self.upper_border == "":
            return
        row, col = self.upper_occ
        next_row = chr(ord(row) + 1)
        self.upper_border = next_row + col if "a" <= next_row <= "i" else ""


class HorizontalCaptureCluster(CaptureCluster):
    def find_lower_border(self):
        if self.lower_border == "":
            return
        row, col = self.lower_occ
        prev_col = chr(ord(col) - 1)
        self.lower_border = row + prev_col if "1" <= prev_col <= "9" else ""

    def find_upper_border(self):
        if self.upper_border == "":
            return
        row, col = self.upper_occ
        next_col = chr(ord(col) + 1)
        self.upper_border = row + next_col if "1" <= next_col <= "9" else ""
