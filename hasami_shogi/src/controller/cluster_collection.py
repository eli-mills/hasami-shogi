from hasami_shogi.src.controller.capture_cluster import ClusterOpResult, Cluster, VertCapCluster, \
    HorCapCluster, VerticalCluster, HorizontalCluster, CaptureCluster
from hasami_shogi.src.controller.game_board import GameBoard


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
        self.initialize_clusters()

    def initialize_clusters(self):
        raise NotImplementedError

    def remove_cluster(self, cluster: Cluster) -> None:
        self.all_clusters and self.all_clusters.remove(cluster)
        for member in cluster.squares:
            if cluster in self.clusters_by_member[member]:
                self.clusters_by_member[member].remove(cluster)
        for border in cluster.get_borders():
            border and self.clusters_by_border[border].remove(cluster)

    def add_cluster(self, cluster: Cluster) -> None:
        self.all_clusters.append(cluster)
        for member in cluster.squares:
            self.clusters_by_member[member].append(cluster)
        for border in cluster.get_borders():
            border and self.clusters_by_border[border].append(cluster)

    def update_clusters_departing(self, square: str) -> None:
        """
        Releases square from existing clusters. Uses results of release operation to update internal state.
        """
        results = ClusterOpResult()

        for cluster in list(self.clusters_by_member[square]):
            results += cluster.release(square)

        for cluster in results.to_remove:
            self.remove_cluster(cluster)

        for cluster in results.to_add:
            self.add_cluster(cluster)

    def update_clusters_arriving(self, square: str) -> None:
        """
        Creates new clusters for square and merges with existing clusters. Uses results of release operation to
        update internal state.
        """
        new_h_cluster = self.H_TYPE({square}, self.board)
        new_v_cluster = self.V_TYPE({square}, self.board)

        h_merges = [cluster for cluster in self.clusters_by_border[square] if cluster.can_merge_with(new_h_cluster)]
        v_merges = [cluster for cluster in self.clusters_by_border[square] if cluster.can_merge_with(new_v_cluster)]

        results = new_h_cluster.merge_with_multiple(h_merges)
        results += new_v_cluster.merge_with_multiple(v_merges)

        for cluster_to_remove in results.to_remove:
            self.remove_cluster(cluster_to_remove)

        self.add_cluster(new_h_cluster)
        self.add_cluster(new_v_cluster)


class CapClusterCollection(ClusterCollection):
    H_TYPE = HorCapCluster
    V_TYPE = VertCapCluster

    def __init__(self, *args, **kwargs):

        self.clusters_by_color = {}
        self.vulnerable_clusters = {}
        self.captured_squares = set()

        super().__init__(*args, **kwargs)

    def initialize_clusters(self):
        black_squares = self.board.get_squares_by_color("BLACK")
        red_squares = self.board.get_squares_by_color("RED")
        black_v_clusters = [self.V_TYPE({sq}, self.board) for sq in black_squares]
        black_h_cluster = self.H_TYPE(black_squares, self.board)
        red_v_clusters = [self.V_TYPE({sq}, self.board) for sq in red_squares]
        red_h_cluster = self.H_TYPE(red_squares, self.board)

        self.all_clusters = [black_h_cluster] + [red_h_cluster] + black_v_clusters + red_v_clusters

        self.clusters_by_color = {
            "BLACK": [black_h_cluster] + black_v_clusters,
            "RED": [red_h_cluster] + red_v_clusters
        }

        self.clusters_by_member = {
            square: [cluster for cluster in self.all_clusters if square in cluster]
            for square in self.board.get_all_squares()
        }

        self.clusters_by_border = {
            border: [cluster for cluster in self.all_clusters if border in cluster.get_borders()]
            for border in self.board.get_all_squares()
        }

        self.vulnerable_clusters = {
            "BLACK": [],
            "RED": []
        }

        self.captured_squares = set()

    def remove_cluster(self, cluster: CaptureCluster) -> None:
        super().remove_cluster(cluster)
        self.clusters_by_color[cluster.color].remove(cluster)
        self.remove_vulnerable_cluster(cluster)

    def add_cluster(self, cluster: CaptureCluster) -> None:
        super().add_cluster(cluster)
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
        self.remove_cluster(large_cluster)

    def report_captured(self, cluster: CaptureCluster):
        self.captured_squares |= cluster.squares

    def clear_captures(self):
        self.captured_squares = set()
