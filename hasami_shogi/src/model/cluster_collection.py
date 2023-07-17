from hasami_shogi.src.model.capture_cluster import ClusterOpResult, Cluster, VertCapCluster, \
    HorCapCluster, VerticalCluster, HorizontalCluster, CaptureCluster, VertTube, HorTube, ClusterUpdates
from hasami_shogi.src.model.game_board import GameBoard


class ClusterCollection:
    H_TYPE = HorizontalCluster
    V_TYPE = VerticalCluster

    def __init__(self, *ign, board=None):
        if ign:
            raise ValueError("ClusterCollection only takes 1 kwargs: board.")

        self.board: GameBoard = board

        self.all_clusters = []
        self.clusters_by_member = {}
        self.clusters_by_border = {}
        self.initialize_all_clusters()

    def initialize_all_clusters(self):
        raise NotImplementedError

    def initialize_clusters_by_member(self):
        self.clusters_by_member = {
            square: [cluster for cluster in self.all_clusters if square in cluster]
            for square in self.board.get_all_squares()
        }

    def initialize_clusters_by_border(self):
        self.clusters_by_border = {
            border: [cluster for cluster in self.all_clusters if border in cluster.get_borders()]
            for border in self.board.get_all_squares()
        }

    def get_squares_by_member(self, square: str) -> set[str]:
        output = set()
        for cluster in self.clusters_by_member[square]:
            output |= cluster.squares
        return output

    def get_squares_by_border(self, square: str) -> set[str]:
        output = set()
        for cluster in self.clusters_by_border[square]:
            output |= cluster.squares
        return output

    def remove_from_all(self, cluster: Cluster) -> None:
        self.all_clusters and self.all_clusters.remove(cluster)
        for member in cluster.squares_sorted:
            self.clusters_by_member[member].remove(cluster)
        for border in cluster.get_borders():
            border and self.clusters_by_border[border].remove(cluster)

    def add_to_all(self, cluster: Cluster) -> None:
        self.all_clusters.append(cluster)
        for member in cluster.squares:
            self.clusters_by_member[member].append(cluster)
        for border in cluster.get_borders():
            border and self.clusters_by_border[border].append(cluster)

    def execute_removal(self, cluster_update: ClusterUpdates) -> None:
        if cluster_update.remove_from_all:
            self.remove_from_all(cluster_update.cluster)
        else:
            for member in cluster_update.members:
                self.clusters_by_member[member].remove(cluster_update.cluster)
            for border in cluster_update.borders:
                border and self.clusters_by_border[border].remove(cluster_update.cluster)

    def execute_add(self, cluster_update: ClusterUpdates) -> None:
        if cluster_update.add_to_all:
            self.add_to_all(cluster_update.cluster)
        else:
            for member in cluster_update.members:
                self.clusters_by_member[member].append(cluster_update.cluster)
            for border in cluster_update.borders:
                border and self.clusters_by_border[border].append(cluster_update.cluster)

    def update_clusters_departing(self, square: str) -> None:
        """
        Releases square from existing clusters. Uses results of release operation to update internal state.
        """
        results = ClusterOpResult()

        for cluster in self.clusters_by_member[square]:
            results += cluster.release(square)

        for cluster_update in results.to_remove:
            self.execute_removal(cluster_update)

        for cluster_update in results.to_add:
            self.execute_add(cluster_update)

    def update_clusters_arriving(self, square: str) -> None:
        """
        Creates new clusters for square and merges with existing clusters. Uses results of release operation to
        update internal state.
        """
        new_h_cluster = self.H_TYPE([square], self.board)
        new_v_cluster = self.V_TYPE([square], self.board)

        h_merges = [cluster for cluster in self.clusters_by_border[square] if cluster.can_merge_with(new_h_cluster)]
        v_merges = [cluster for cluster in self.clusters_by_border[square] if cluster.can_merge_with(new_v_cluster)]

        results = new_h_cluster.merge_with_multiple(h_merges)
        results += new_v_cluster.merge_with_multiple(v_merges)

        for cluster_to_remove in results.to_remove:
            self.execute_removal(cluster_to_remove)

        self.add_to_all(new_h_cluster)
        self.add_to_all(new_v_cluster)


class CapClusterCollection(ClusterCollection):
    H_TYPE = HorCapCluster
    V_TYPE = VertCapCluster

    def __init__(self, *args, **kwargs):

        self.clusters_by_color = {}
        self.vulnerable_clusters = {}
        self.captured_squares = set()

        super().__init__(*args, **kwargs)

    def initialize_all_clusters(self):
        black_squares = self.board.get_squares_by_color("BLACK")
        red_squares = self.board.get_squares_by_color("RED")
        black_v_clusters = [self.V_TYPE([sq], self.board) for sq in black_squares]
        black_h_cluster = self.H_TYPE(sorted(list(black_squares)), self.board)
        red_v_clusters = [self.V_TYPE([sq], self.board) for sq in red_squares]
        red_h_cluster = self.H_TYPE(sorted(list(red_squares)), self.board)

        self.all_clusters = [black_h_cluster] + [red_h_cluster] + black_v_clusters + red_v_clusters
        self.initialize_clusters_by_member()
        self.initialize_clusters_by_border()

        self.clusters_by_color = {
            "BLACK": [black_h_cluster] + black_v_clusters,
            "RED": [red_h_cluster] + red_v_clusters
        }

        self.vulnerable_clusters = {
            "BLACK": [],
            "RED": []
        }

        self.captured_squares = set()

    def remove_from_all(self, cluster: CaptureCluster) -> None:
        super().remove_from_all(cluster)
        self.clusters_by_color[cluster.color].remove(cluster)
        self.remove_vulnerable_cluster(cluster)

    def add_to_all(self, cluster: CaptureCluster) -> None:
        super().add_to_all(cluster)
        self.clusters_by_color[cluster.color].append(cluster)

    def update_clusters_departing(self, square: str) -> None:
        super().update_clusters_departing(square)
        self.update_vulnerable_clusters(square)

    def update_clusters_arriving(self, square: str) -> None:
        super().update_clusters_arriving(square)
        self.update_vulnerable_clusters(square)

    def add_vulnerable_cluster(self, cluster):
        if cluster not in self.vulnerable_clusters[cluster.color]:
            self.vulnerable_clusters[cluster.color].append(cluster)

    def remove_vulnerable_cluster(self, cluster):
        if cluster in self.vulnerable_clusters[cluster.color]:
            self.vulnerable_clusters[cluster.color].remove(cluster)

    def update_vulnerable_clusters(self, square: str) -> None:
        """
        Given a square where a piece either left or arrived, updates currently vulnerable clusters.
        """
        for cluster in self.clusters_by_border[square] + self.clusters_by_member[square]:
            cluster.check_if_capturable()
            if cluster.is_captured:
                self.report_captured(cluster)
            if cluster.risky_border:
                self.add_vulnerable_cluster(cluster)
            else:
                self.remove_vulnerable_cluster(cluster)

    def handle_captured_squares(self, captured_squares: list):
        """
        Find the cluster containing all the provided squares and remove, rather than splitting and remerging as each
        piece is deleted.
        """
        if len(captured_squares) <= 1:
            return
        large_cluster = [cluster for cluster in self.clusters_by_member[captured_squares[0]] if len(cluster) == len(
            captured_squares)][0]
        self.execute_removal(large_cluster)

    def report_captured(self, cluster: CaptureCluster):
        self.captured_squares |= cluster.squares

    def clear_captures(self):
        self.captured_squares = set()


class TubeCollection(ClusterCollection):
    H_TYPE = HorTube
    V_TYPE = VertTube

    def initialize_all_clusters(self):
        v_tubes = []
        h_tubes = []

        for col in [str(col_num) for col_num in range(1, 10)]:
            col_squares = sorted(self.board.get_squares_by_axis(col)[1:-1])
            v_tubes.append(self.V_TYPE(col_squares, self.board))

        for row in [chr(row_num) for row_num in range(98, 105)]:
            row_squares = sorted(self.board.get_squares_by_axis(row))
            h_tubes.append(self.H_TYPE(row_squares, self.board))

        self.all_clusters = h_tubes + v_tubes
        self.initialize_clusters_by_member()
        self.initialize_clusters_by_border()

