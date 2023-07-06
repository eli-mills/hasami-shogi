from hasami_shogi.src.controller.game_board import GameBoard


class ClusterOpResult:
    def __init__(self):
        self.to_remove = []
        self.to_add = []

    def __bool__(self):
        return self.to_add or self.to_remove

    def __add__(self, other):
        output = ClusterOpResult()
        output.to_remove = self.to_remove + other.to_remove
        output.to_add = self.to_add + other.to_add
        return output

    def __repr__(self):
        return f"Add {self.to_add}; Remove {self.to_remove}"

    def extend_to_remove(self, cluster_list: list["Cluster"]):
        self.to_remove.extend(cluster_list)

    def extend_to_add(self, cluster_list: list["Cluster"]):
        self.to_add.extend(cluster_list)

    def combine_another_result(self, result: "ClusterOpResult"):
        self.to_remove.extend(result.to_remove)
        self.to_add.extend(result.to_add)


class Cluster:

    def __init__(self, squares: list[str], board: GameBoard):
        """
        Square list must be sorted.
        """
        self.board: GameBoard = board
        self.squares: set[str] = set(squares)
        self.squares_sorted: list[str] = squares
        self.lower_occ, self.upper_occ = self.squares_sorted[0], self.squares_sorted[-1]
        self.color: str = self.board.get_square(self.lower_occ)
        self.size = len(self.squares)

        self.lower_border = self.upper_border = None
        self.find_lower_border()
        self.find_upper_border()

    def __len__(self):
        return self.size

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

    def merge_validation(self, merging_cluster: "Cluster"):
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

    def update_lower_occ(self):
        self.lower_occ = min(self.squares)

    def update_upper_occ(self):
        self.upper_occ = max(self.squares)

    def release(self, square: str) -> ClusterOpResult:
        self.raise_if_bad_square(square)
        result = ClusterOpResult()

        if len(self) == 1:
            result.extend_to_remove([self])
            return result

        curr_squares = self.squares_sorted

        # Case: square is min
        if square == self.lower_occ:
            result.extend_to_remove([self])
            result.extend_to_add([type(self)(curr_squares[1:], self.board)])
            # TODO: modify self instead of instantiating new cluster, result removes AND adds self
            return result

        # Case: square is max
        if square == self.upper_occ:
            result.extend_to_remove([self])
            result.extend_to_add([type(self)(curr_squares[:-1], self.board)])
            return result

        # Case: square between min and max
        lower_squares = curr_squares[:curr_squares.index(square)]
        upper_squares = curr_squares[curr_squares.index(square) + 1:]
        result.extend_to_add([
            type(self)(lower_squares, self.board),
            type(self)(upper_squares, self.board)
        ])
        result.extend_to_remove([self])
        return result

    def can_merge_with(self, merging_cluster: "Cluster") -> bool:
        try:
            self.merge_validation(merging_cluster)
        except ValueError:
            return False
        return True

    def merge(self, merging_cluster: "Cluster") -> ClusterOpResult:
        """
        Raise ValueError if merge not possible.
        """
        self.merge_validation(merging_cluster)
        self.squares |= merging_cluster.squares
        self.size += merging_cluster.size

        lower_cluster = self if self.upper_occ <= merging_cluster.lower_occ else merging_cluster
        upper_cluster = merging_cluster if self == lower_cluster else self

        self.squares_sorted = lower_cluster.squares_sorted + upper_cluster.squares_sorted
        self.lower_occ = lower_cluster.lower_occ
        self.upper_occ = upper_cluster.upper_occ
        self.find_upper_border()
        self.find_lower_border()

        results = ClusterOpResult()
        results.extend_to_remove([merging_cluster])

        return results

    def merge_with_multiple(self, cluster_list: list["Cluster"]) -> ClusterOpResult:
        """
        Merges with every cluster in list, becoming only remaining cluster. Every cluster on list will be set to remove.
        """
        results = ClusterOpResult()
        for cluster in cluster_list:
            results += self.merge(cluster)
        return results

    def get_borders(self) -> set[str]:
        return {self.lower_border, self.upper_border}

    def get_other_border(self, square: str) -> str:
        border_squares: set = self.get_borders()
        if square not in border_squares:
            return ""
        border_squares.remove(square)
        return border_squares.pop()

    def is_at_edge(self):
        return "" in self.get_borders()


class VerticalCluster(Cluster):
    LOWER_BORDERS = {
        "a": "",
        "b": "a",
        "c": "b",
        "d": "c",
        "e": "d",
        "f": "e",
        "g": "f",
        "h": "g",
        "i": "h"
    }

    UPPER_BORDERS = {
        "a": "b",
        "b": "c",
        "c": "d",
        "d": "e",
        "e": "f",
        "f": "g",
        "g": "h",
        "h": "i",
        "i": ""
    }

    def find_lower_border(self):
        if self.lower_border == "":
            return
        row, col = self.lower_occ
        # prev_row = chr(ord(row) - 1)
        # self.lower_border = prev_row + col if "a" <= prev_row <= "i" else ""
        prev_row = self.LOWER_BORDERS[row]
        self.lower_border = prev_row + col if prev_row else ""

    def find_upper_border(self):
        if self.upper_border == "":
            return
        row, col = self.upper_occ
        next_row = self.UPPER_BORDERS[row]
        self.upper_border = next_row + col if next_row else ""


class HorizontalCluster(Cluster):
    LOWER_BORDERS = {
        "1": "",
        "2": "1",
        "3": "2",
        "4": "3",
        "5": "4",
        "6": "5",
        "7": "6",
        "8": "7",
        "9": "8"
    }

    UPPER_BORDERS = {
        "1": "2",
        "2": "3",
        "3": "4",
        "4": "5",
        "5": "6",
        "6": "7",
        "7": "8",
        "8": "9",
        "9": ""
    }

    def find_lower_border(self):
        if self.lower_border == "":
            return
        row, col = self.lower_occ
        prev_col = self.LOWER_BORDERS[col]
        self.lower_border = row + prev_col if prev_col else ""

    def find_upper_border(self):
        if self.upper_border == "":
            return
        row, col = self.upper_occ
        next_col = self.UPPER_BORDERS[col]
        self.upper_border = row + next_col if next_col else ""


class CaptureCluster(Cluster):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.opp_color: str = self.board.opposite_color(self.color)
        self.risky_border = ""
        self.is_captured = False
        self.check_if_capturable()

    def check_if_capturable(self) -> None:
        if self.risky_border and self.board.get_square(self.risky_border) == self.opp_color:
            self.is_captured = True
            self.risky_border = ""
            return None
        if not self.lower_border or not self.upper_border:
            self.risky_border = ""
            return None

        lb_val = self.board.get_square(self.lower_border)
        ub_val = self.board.get_square(self.upper_border)
        if lb_val == ub_val == "NONE":
            self.risky_border = ""
            return None
        if lb_val == "NONE":
            self.risky_border = self.lower_border
        elif ub_val == "NONE":
            self.risky_border = self.upper_border
        else:
            self.risky_border = ""
        return None

    def merge(self, *args, **kwargs) -> ClusterOpResult:
        """
        Raise ValueError if merge not possible.
        """
        results = super().merge(*args, **kwargs)
        self.check_if_capturable()
        return results


class Tube(Cluster):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.color != "NONE":
            raise ValueError(f"Tube initialized with occupied squares: {self}")


class VertCapCluster(CaptureCluster, VerticalCluster):
    pass


class HorCapCluster(CaptureCluster, HorizontalCluster):
    pass


class VertTube(Tube, VerticalCluster):
    pass


class HorTube(Tube, HorizontalCluster):
    pass
