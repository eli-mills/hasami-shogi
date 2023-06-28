class CaptureCluster:
    class ClusterOpResult:
        def __init__(self):
            self.to_remove = []
            self.to_add = []

        def extend_to_remove(self, cluster_list: list["CaptureCluster"]):
            self.to_remove.extend(cluster_list)

        def extend_to_add(self, cluster_list: list["CaptureCluster"]):
            self.to_add.extend(cluster_list)

    def __init__(self, squares: set, color: str):
        self.squares: set = squares
        self.color: str = color
        self.lower_occ, self.upper_occ = min(squares), max(squares)
        self.lower_border = self.upper_border = None

        self.validation()
        self.find_lower_border()
        self.find_upper_border()

    def __len__(self):
        return len(self.squares)

    def __repr__(self):
        return type(self).__name__ + repr(self.squares)

    def __contains__(self, item):
        return item in self.squares

    def validation(self):
        if [sq for sq in self.squares if sq[0] != self.lower_occ[0]] and [sq for sq in self.squares if sq[1] != self.lower_occ[1]]:
            raise ValueError(f"Squares must be all in one line: {self.squares}")

    def raise_if_bad_square(self, square: str) -> None:
        if square not in self.squares:
            raise ValueError(f"{square} not in self.squares {self.squares}")

    def merge_validation(self, merging_cluster: "CaptureCluster"):
        if self.upper_occ != merging_cluster.lower_border and merging_cluster.upper_occ != self.lower_border:
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

    def remove(self, square: str) -> ClusterOpResult:
        self.raise_if_bad_square(square)
        result = CaptureCluster.ClusterOpResult()

        if len(self.squares) == 1:
            result.extend_to_remove([self])
            return result

        curr_squares = sorted(list(self.squares))
        self.squares.remove(square)

        # Case: square is min
        if square == self.lower_occ:
            self.lower_border = square
            self.update_lower_occ()
            return result

        # Case: square is max
        if square == self.upper_occ:
            self.upper_border = square
            self.update_upper_occ()
            return result

        # Case: square between min and max
        lower_squares = curr_squares[:curr_squares.index(square)]
        upper_squares = curr_squares[curr_squares.index(square) + 1:]
        result.extend_to_add([type(self)(set(lower_squares), self.color), type(self)(set(upper_squares), self.color)])
        result.extend_to_remove([self])
        return result

    def can_merge_with(self, merging_cluster: "CaptureCluster") -> bool:
        try:
            self.merge_validation(merging_cluster)
        except ValueError:
            return False
        return True

    def merge(self, merging_cluster: "CaptureCluster") -> ClusterOpResult:
        """
        Raise ValueError if merge not possible.
        """
        self.merge_validation(merging_cluster)
        self.squares |= merging_cluster.squares
        self.lower_occ = min(self.lower_occ, merging_cluster.lower_occ)
        self.upper_occ = max(self.upper_occ, merging_cluster.upper_occ)
        self.find_upper_border()
        self.find_lower_border()

        results = CaptureCluster.ClusterOpResult()
        results.extend_to_remove([merging_cluster])

        return results

    def get_borders(self) -> set[str]:
        return {self.lower_border, self.upper_border}

    def get_other_border(self, square: str) -> str:
        border_squares = self.get_borders()
        if square not in border_squares:
            return ""
        border_squares.remove(square)
        return border_squares.pop()

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
