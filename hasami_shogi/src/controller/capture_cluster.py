from hasami_shogi.src.controller.game_board import GameBoard


class CaptureCluster:
    class ClusterOpResult:
        def __init__(self):
            self.to_remove = []
            self.to_add = []

        def __bool__(self):
            return self.to_add or self.to_remove

        def __add__(self, other):
            output = CaptureCluster.ClusterOpResult()
            output.to_remove = self.to_remove + other.to_remove
            output.to_add = self.to_add + other.to_add
            return output

        def extend_to_remove(self, cluster_list: list["CaptureCluster"]):
            self.to_remove.extend(cluster_list)

        def extend_to_add(self, cluster_list: list["CaptureCluster"]):
            self.to_add.extend(cluster_list)

        def combine_another_result(self, result: "CaptureCluster.ClusterOpResult"):
            self.to_remove.extend(result.to_remove)
            self.to_add.extend(result.to_add)

    def __init__(self, squares: set, color: str, board: GameBoard):
        self.squares: set = squares
        self.color: str = color
        self.lower_occ, self.upper_occ = min(squares), max(squares)
        self.lower_border = self.upper_border = None
        self.lb_value = self.ub_value = None
        self.board = board
        self.risky_border = ""

        # self.validation()
        self.find_lower_border()
        self.find_upper_border()
        self.check_if_capturable()

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
            raise ValueError(f"Cannot merge the two clusters")
        if type(self) != type(merging_cluster):
            raise ValueError(f"Cannot merge two clusters of different type")
        if self.color != merging_cluster.color:
            raise ValueError(f"Cannot merge two clusters of different color")

    def find_lower_border(self):
        """Set self.lower_border"""
        raise NotImplementedError

    def find_upper_border(self):
        """Set self.upper_border"""
        raise NotImplementedError

    def check_if_capturable(self) -> None:
        if not self.lower_border or not self.upper_border:
            self.risky_border = ""
            return None
        if self.board.get_square(self.lower_border) == self.board.get_square(self.upper_border) == "NONE":
            self.risky_border = ""
            return None
        if self.board.get_square(self.lower_border) == "NONE":
            self.risky_border = self.lower_border
            return None
        if self.board.get_square(self.upper_border) == "NONE":
            self.risky_border = self.upper_border
            return None


    def update_lower_occ(self):
        self.lower_occ = min(self.squares)

    def update_upper_occ(self):
        self.upper_occ = max(self.squares)

    def release(self, square: str) -> ClusterOpResult:
        self.raise_if_bad_square(square)
        result = CaptureCluster.ClusterOpResult()

        if len(self.squares) == 1:
            result.extend_to_remove([self])
            return result

        curr_squares = sorted(list(self.squares))

        # Case: square is min
        if square == self.lower_occ:
            result.extend_to_remove([self])
            result.extend_to_add([type(self)(set(curr_squares[1:]), self.color, self.board)])
            return result

        # Case: square is max
        if square == self.upper_occ:
            result.extend_to_remove([self])
            result.extend_to_add([type(self)(set(curr_squares[:-1]), self.color, self.board)])
            return result

        # Case: square between min and max
        lower_squares = curr_squares[:curr_squares.index(square)]
        upper_squares = curr_squares[curr_squares.index(square) + 1:]
        result.extend_to_add([type(self)(set(lower_squares), self.color, self.board), type(self)(set(upper_squares),
                                                                                        self.color, self.board)])
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
        self.check_if_capturable()

        results = CaptureCluster.ClusterOpResult()
        results.extend_to_remove([merging_cluster])

        return results

    def merge_with_multiple(self, cluster_list: list["CaptureCluster"]) -> ClusterOpResult:
        """
        Merges with every cluster in list, becoming only remaining cluster. Every cluster on list will be set to remove.
        """
        results = CaptureCluster.ClusterOpResult()
        for cluster in cluster_list:
            results += self.merge(cluster)
        return results

    def get_borders(self) -> set[str]:
        return {self.lower_border, self.upper_border}

    def get_other_border(self, square: str) -> str:
        border_squares = self.get_borders()
        if square not in border_squares:
            return ""
        border_squares.remove(square)
        return border_squares.pop()

    def is_at_edge(self):
        return "" in self.get_borders()

    def reveal_capturing_square(self) -> str:
        """
        Returns the square that, if an enemy took, would capture this cluster. If none exists, returns empty string.
        """
        if "" in self.get_borders():
            return ""
        return


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
