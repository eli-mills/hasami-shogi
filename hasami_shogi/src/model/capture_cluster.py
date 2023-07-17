from hasami_shogi.src.model.game_board import GameBoard


class ClusterUpdates:
    def __init__(self, cluster: "Cluster", borders: set[str] = None, members: set[str] = None):
        self.cluster: Cluster = cluster
        self.borders: set[str] = borders if borders else set()
        self.members: set[str] = members if members else set()
        self.remove_from_all = False
        self.add_to_all = False

    def __repr__(self):
        return f"Cluster: {self.cluster}, Borders: {self.borders}, Members: {self.members}"

    def add_to_members(self, members: set[str]):
        self.members |= members

    def add_to_borders(self, borders: set[str]):
        self.borders |= borders


class ClusterOpResult:
    def __init__(self):
        self.to_remove: list[ClusterUpdates] = []
        self.to_add: list[ClusterUpdates] = []

    def __bool__(self):
        return self.to_add or self.to_remove

    def __add__(self, other):
        output = ClusterOpResult()
        output.to_remove = self.to_remove + other.to_remove
        output.to_add = self.to_add + other.to_add
        return output

    def __repr__(self):
        return f"Add {self.to_add}; Remove {self.to_remove}"

    def extend_to_remove(self, cluster_updates: list["ClusterUpdates"]):
        self.to_remove.extend(cluster_updates)

    def extend_to_add(self, cluster_updates: list["ClusterUpdates"]):
        self.to_add.extend(cluster_updates)


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

        self.lower_border = self.upper_border = None
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
        self_update_removal = ClusterUpdates(self, members={square})
        result = ClusterOpResult()
        result.extend_to_remove([self_update_removal])

        if len(self) == 1:
            self_update_removal.remove_from_all = True
            return result

        curr_squares = self.squares_sorted

        # Case: square is min
        if square == self.lower_occ:
            self_update_removal.add_to_borders({self.lower_border})
            self.squares_sorted = self.squares_sorted[1:]
            self.squares.remove(square)
            self.lower_border = square
            self.lower_occ = self.squares_sorted[0]
            self_update_add = ClusterUpdates(self, borders={self.lower_border})
            result.extend_to_add([self_update_add])
            return result

        # Case: square is max
        if square == self.upper_occ:
            self_update_removal.add_to_borders({self.upper_border})
            self.squares_sorted = self.squares_sorted[:-1]
            self.squares.remove(square)
            self.upper_border = square
            self.upper_occ = self.squares_sorted[-1]
            self_update_add = ClusterUpdates(self, borders={self.upper_border})
            result.extend_to_add([self_update_add])
            return result

        # Case: square between min and max - self becomes lower, create new upper
        lower_squares = curr_squares[:curr_squares.index(square)]
        upper_squares = curr_squares[curr_squares.index(square) + 1:]

        self.squares_sorted = lower_squares
        self.squares = set(lower_squares)
        self_update_removal.add_to_borders({self.upper_border})
        self.upper_border = square
        self.upper_occ = self.squares_sorted[-1]

        self_update_removal.add_to_members(set(upper_squares))
        self_update_add = ClusterUpdates(self, borders={self.upper_border})

        upper_cluster = type(self)(upper_squares, self.board)
        new_cluster_add = ClusterUpdates(upper_cluster)
        new_cluster_add.add_to_all = True

        result.extend_to_add([new_cluster_add, self_update_add])
        return result

    def can_merge_with(self, merging_cluster: "Cluster") -> bool:
        try:
            self.merge_validation(merging_cluster)
        except ValueError:
            return False
        return True

    def merge(self, merging_cluster: "Cluster") -> ClusterOpResult:
        """
        Merge merging_cluster into self. Raise ValueError if merge not possible.
        """
        self.merge_validation(merging_cluster)
        self.squares |= merging_cluster.squares

        lower_cluster = self if self.upper_occ <= merging_cluster.lower_occ else merging_cluster
        upper_cluster = merging_cluster if self == lower_cluster else self

        self.squares_sorted = lower_cluster.squares_sorted + upper_cluster.squares_sorted
        self.lower_occ = lower_cluster.lower_occ
        self.upper_occ = upper_cluster.upper_occ
        self.lower_border = lower_cluster.lower_border
        self.upper_border = upper_cluster.upper_border

        remove_merging = ClusterUpdates(merging_cluster)
        remove_merging.remove_from_all = True
        add_self_to_merging_squares = ClusterUpdates(self, members=merging_cluster.squares)
        add_self_to_merging_squares.add_to_borders({self.lower_border if self == upper_cluster else self.upper_border})

        results = ClusterOpResult()
        results.extend_to_remove([remove_merging])
        results.extend_to_add([add_self_to_merging_squares])

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

    def __repr__(self):
        return self.color + super().__repr__()

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
