from hasami_shogi.src.model.game_board import GameBoard


class ClusterUpdates:
    """
    Defines data structure to hold information used by ClusterCollection to update data members.
    """
    def __init__(self, cluster: "Cluster", borders: set[str] = None, members: set[str] = None):
        self.cluster: Cluster = cluster                             # Cluster to add or remove
        self.borders: set[str] = borders if borders else set()      # Borders to update
        self.members: set[str] = members if members else set()      # Members to update
        self.remove_from_all: bool = False                          # Set true to remove cluster from all collections
        self.add_to_all: bool = False                               # Set true to add cluster to all collections

    def __repr__(self) -> str:
        return f"Cluster: {self.cluster}, Borders: {self.borders}, Members: {self.members}"

    def add_to_members(self, members: set[str]) -> None:
        self.members |= members

    def add_to_borders(self, borders: set[str]) -> None:
        self.borders |= borders


class ClusterOpResult:
    """
    Collection of ClusterUpdates and instructions on whether to add or remove.
    """
    def __init__(self):
        self.to_remove: list[ClusterUpdates] = []
        self.to_add: list[ClusterUpdates] = []

    def __bool__(self) -> bool:
        return bool(self.to_add) or bool(self.to_remove)

    def __add__(self, other: "ClusterOpResult") -> "ClusterOpResult":
        output = ClusterOpResult()
        output.to_remove = self.to_remove + other.to_remove
        output.to_add = self.to_add + other.to_add
        return output

    def __repr__(self) -> str:
        return f"Add {self.to_add}; Remove {self.to_remove}"

    def extend_to_remove(self, cluster_updates: list["ClusterUpdates"]) -> None:
        self.to_remove.extend(cluster_updates)

    def extend_to_add(self, cluster_updates: list["ClusterUpdates"]) -> None:
        self.to_add.extend(cluster_updates)


class Cluster:
    """
    Contains methods for maintaining a collection of adjacent squares of the same color.
    """

    def __init__(self, squares: list[str], board: GameBoard):
        """
        Square list must be sorted.
        """
        self.board: GameBoard = board
        self.squares: set[str] = set(squares)
        self.squares_sorted: list[str] = squares
        self.lower_occ: str = self.squares_sorted[0]
        self.upper_occ: str = self.squares_sorted[-1]
        self.color: str = self.board.get_square(self.lower_occ)

        self.lower_border = self.upper_border = None
        self.find_lower_border()
        self.find_upper_border()

    def __len__(self) -> int:
        return len(self.squares)

    def __repr__(self) -> str:
        return type(self).__name__ + repr(self.squares)

    def __contains__(self, item) -> bool:
        return item in self.squares

    def validation(self) -> None:
        if [sq for sq in self.squares if sq[0] != self.lower_occ[0]] and [sq for sq in self.squares if sq[1] != self.lower_occ[1]]:
            raise ValueError(f"Squares must be all in one line: {self.squares}")

    def raise_if_bad_square(self, square: str) -> None:
        if square not in self.squares:
            raise ValueError(f"{square} not in self.squares {self.squares}")

    def merge_validation(self, merging_cluster: "Cluster") -> None:
        """
        Raises exception if merging_cluster is incompatible to merge with self.
        """
        if self.upper_occ != merging_cluster.lower_border and merging_cluster.upper_occ != self.lower_border:
            raise ValueError(f"Cannot merge the two clusters")
        if type(self) != type(merging_cluster):
            raise ValueError(f"Cannot merge two clusters of different type")
        if self.color != merging_cluster.color:
            raise ValueError(f"Cannot merge two clusters of different color")

    def find_lower_border(self) -> None:
        """Set self.lower_border"""
        raise NotImplementedError

    def find_upper_border(self) -> None:
        """Set self.upper_border"""
        raise NotImplementedError

    def update_lower_occ(self) -> None:
        self.lower_occ = min(self.squares)

    def update_upper_occ(self) -> None:
        self.upper_occ = max(self.squares)

    def release(self, square: str) -> ClusterOpResult:
        """
        Handles removing given square from set and creating new clusters from resulting split. Returns these new
        clusters along with instructions on how to update them in the ClusterCollection.
        """
        self.raise_if_bad_square(square)
        cu_remove_self = ClusterUpdates(self, members={square})
        result = ClusterOpResult()
        result.extend_to_remove([cu_remove_self])

        if len(self) == 1:
            cu_remove_self.remove_from_all = True
            return result

        curr_squares = self.squares_sorted

        # Case: square is min
        if square == self.lower_occ:
            cu_remove_self.add_to_borders({self.lower_border})
            self.squares_sorted = self.squares_sorted[1:]
            self.squares.remove(square)
            self.lower_border = square
            self.lower_occ = self.squares_sorted[0]
            cu_add_self = ClusterUpdates(self, borders={self.lower_border})
            result.extend_to_add([cu_add_self])
            return result

        # Case: square is max
        if square == self.upper_occ:
            cu_remove_self.add_to_borders({self.upper_border})
            self.squares_sorted = self.squares_sorted[:-1]
            self.squares.remove(square)
            self.upper_border = square
            self.upper_occ = self.squares_sorted[-1]
            cu_add_self = ClusterUpdates(self, borders={self.upper_border})
            result.extend_to_add([cu_add_self])
            return result

        # Case: square between min and max - self becomes lower, create new upper
        lower_squares = curr_squares[:curr_squares.index(square)]
        upper_squares = curr_squares[curr_squares.index(square) + 1:]

        # ClusterUpdate: remove self from old upper border and squares
        cu_remove_self.add_to_borders({self.upper_border})
        cu_remove_self.add_to_members(set(upper_squares))

        # Update own data members to lower half
        self.squares_sorted = lower_squares
        self.squares = set(lower_squares)
        self.upper_border = square
        self.upper_occ = self.squares_sorted[-1]

        # ClusterUpdate: Add self to new upper_border
        cu_add_self = ClusterUpdates(self, borders={self.upper_border})

        # Create new cluster from upper squares and record updates in new ClusterUpdate
        upper_cluster = type(self)(upper_squares, self.board)
        cu_add_new_cluster = ClusterUpdates(upper_cluster)
        cu_add_new_cluster.add_to_all = True

        result.extend_to_add([cu_add_new_cluster, cu_add_self])
        return result

    def can_merge_with(self, merging_cluster: "Cluster") -> bool:
        """
        Returns False if merging would throw an error, else True.
        """
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

        # Update own data members
        self.squares_sorted = lower_cluster.squares_sorted + upper_cluster.squares_sorted
        self.lower_occ = lower_cluster.lower_occ
        self.upper_occ = upper_cluster.upper_occ
        self.lower_border = lower_cluster.lower_border
        self.upper_border = upper_cluster.upper_border

        # ClusterUpdates: remove all references of merging_cluster, and update self for new members and borders
        cu_remove_merging_cluster = ClusterUpdates(merging_cluster)
        cu_remove_merging_cluster.remove_from_all = True
        cu_add_self_to_new_squares = ClusterUpdates(self, members=merging_cluster.squares)
        cu_add_self_to_new_squares.add_to_borders({self.lower_border if self == upper_cluster else self.upper_border})

        results = ClusterOpResult()
        results.extend_to_remove([cu_remove_merging_cluster])
        results.extend_to_add([cu_add_self_to_new_squares])

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
        """
        Given one of self's borders, returns the other, or "" if square not a border.
        """
        border_squares: set = self.get_borders()
        if square not in border_squares:
            return ""
        border_squares.remove(square)
        return border_squares.pop()


class VerticalCluster(Cluster):
    """
    Defines methods for finding borders in a vertical orientation.
    """
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

    def find_lower_border(self) -> None:
        if self.lower_border == "":
            return
        row, col = self.lower_occ
        prev_row = self.LOWER_BORDERS[row]
        self.lower_border = prev_row + col if prev_row else ""

    def find_upper_border(self) -> None:
        if self.upper_border == "":
            return
        row, col = self.upper_occ
        next_row = self.UPPER_BORDERS[row]
        self.upper_border = next_row + col if next_row else ""


class HorizontalCluster(Cluster):
    """
    Defines methods for finding borders in a horizontal orientation.
    """
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

    def find_lower_border(self) -> None:
        if self.lower_border == "":
            return
        row, col = self.lower_occ
        prev_col = self.LOWER_BORDERS[col]
        self.lower_border = row + prev_col if prev_col else ""

    def find_upper_border(self) -> None:
        if self.upper_border == "":
            return
        row, col = self.upper_occ
        next_col = self.UPPER_BORDERS[col]
        self.upper_border = row + next_col if next_col else ""


class CaptureCluster(Cluster):
    """
    Expands functionality of Cluster to include helpful capture-related methods and properties.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.opp_color: str = self.board.opposite_color(self.color)
        self.risky_border: str = ""                 # Border that, if opponent takes, will result in capture
        self.is_captured: bool = False              # True if opponent just took risky_border
        self.check_if_capturable()

    def __repr__(self) -> str:
        return self.color + super().__repr__()

    def check_if_capturable(self) -> None:
        """
        Updates risky_border and is_captured based on current board.
        """

        # Scenario: capture occurred
        if self.risky_border and self.board.get_square(self.risky_border) == self.opp_color:
            self.is_captured = True
            self.risky_border = ""
            return None

        # Scenario: one side against edge of board
        if not self.lower_border or not self.upper_border:
            self.risky_border = ""
            return None

        # Update risky_border according to board state
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
        Call parent merge, then update capture-related properties.
        """
        results = super().merge(*args, **kwargs)
        self.check_if_capturable()
        return results


class Tube(Cluster):
    """
    Defines methods for a Cluster of empty squares.
    """
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
