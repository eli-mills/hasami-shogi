from hasami_shogi.src.model.hasami_shogi_utilities import *
from hasami_shogi.src.model.player import Player


class AIPlayer(Player):
    """
    Defines the methods for an AI Hasami Shogi player. Inherits from regular Player class.
    """

    H_WIN = 9999                    # Weight for a winning move
    H_MATERIAL = 200                # Weight for number of pieces on board vs enemy's
    H_CAPTURE = 100                # Weight for setting up a capture
    H_POT_CAP = 20
    H_CENTER = 1 / 16             # Weight for being in a central position

    def __init__(self, *args, **kwargs):
        """
        Calls Player initializer with appropriate args, then adds additional properties.
        """
        super().__init__(*args, **kwargs)
        self.alpha = None                               # Saves maximizer's best move
        self.beta = None                                # Saves minimizer's best move
        self.is_maximizing = self.get_color() == "BLACK"
        self.initial_best_score = -9999 if self.is_maximizing else 9999

    def __repr__(self):
        """
        Defines how self should be printed.
        """
        return type(self).__name__ + self._color

    def make_move(self, start: str, dest: str):
        """
        Overrides parent method to add extra validation, in case proposed moves are invalid.
        """
        init_move_log_length = len(self.get_game().move_log)
        move_was_successful = super().make_move(start, dest)
        if not move_was_successful:
            raise ValueError(f"AI {self} made illegal move {start}{dest} with pieces {self.get_pieces()}")
        if self.get_active():
            raise ValueError(f"Game failed to update active after valid move {start}{dest} by {self}.")
        if len(self.get_game().move_log) != init_move_log_length + 1:
            raise ValueError(f"Move log failed to update for valid move {start}{dest} by {self} with.")

    def find_pot_cap_squares(self) -> dict[str, int]:
        """
        Returns dict of squares that, if taken by player, would result in dict[square] pieces being captured.
        """
        for cluster in self.get_game().clusters.vulnerable_clusters[self.get_opposing_color()]:
            risky_border_val = self.get_game().get_square_occupant(cluster.risky_border)
            if risky_border_val != "NONE":
                raise ValueError(f"Opponent cluster risky border is out of sync with board state: {cluster} risky "
                                 f"border at {cluster.risky_border} has board value {risky_border_val}")
        vulnerable_clusters = self.get_game().clusters.vulnerable_clusters[self.get_opposing_color()]
        return {cluster.risky_border: len(cluster) for cluster in vulnerable_clusters}

    def find_reachable_pieces(self, square_to_reach: str) -> set[str]:
        """
        Returns set of own pieces that can reach the given square.
        """
        reachable_squares = self.get_game().tubes.get_squares_by_border(square_to_reach)
        reachable_squares |= self.get_game().tubes.get_squares_by_member(square_to_reach)

        return self.get_pieces() & reachable_squares

    def find_capture_moves(self) -> list[tuple[str, int]]:
        """
        Returns a list of tuples of the form (move, num_captures), sorted by which move will result in the most
        pieces captured.
        """
        squares_to_check = self.find_pot_cap_squares()
        output = [(piece + square_to_reach, square_value) for square_to_reach, square_value in squares_to_check.items()
                  for piece in self.find_reachable_pieces(square_to_reach)]
        return list(sorted(output, key=lambda x: x[1], reverse=True))

    def find_adjacent_moves(self) -> list[str]:
        """
        Returns all moves to squares adjacent to opponent.
        """
        opp_pieces = self.get_opposing_player().get_pieces()
        active_pieces = self.get_pieces()

        opponent_adjacent_squares = {adj_square for opp_piece in opp_pieces
                                     for adj_square in get_adjacent_squares(opp_piece)
                                     if adj_square not in opp_pieces | active_pieces}

        adjacent_moves = [piece + square_to_reach for square_to_reach in opponent_adjacent_squares
                          for piece in self.find_reachable_pieces(square_to_reach)]

        return adjacent_moves

    def get_all_valid_moves(self) -> set[str]:
        """
        Returns set of all valid moves given current game state.
        """
        return {move for piece in self.get_pieces() for move in self.get_game().return_valid_moves(piece)}

    def order_available_moves(self) -> list[str]:
        """
        Returns a list of all possible moves given the current game state. Orders preferable moves first.
        """
        if not self.get_active():
            raise Exception("order_available_moves called by inactive Player.")

        capture_moves = [move[0] for move in self.find_capture_moves()]
        adjacent_moves = [x for x in self.find_adjacent_moves() if x not in capture_moves]
        preferred_moves = capture_moves + adjacent_moves
        remaining_moves = [move for move in self.get_all_valid_moves() if move not in preferred_moves]
        center_moves = [move for move in remaining_moves if move[2] in "def" and move[3] in "456"]  # ends in center
        leftover_moves = [move for move in remaining_moves if move not in center_moves]

        return preferred_moves + center_moves + leftover_moves

    def get_center_heuristic(self) -> int:
        """
        Returns a score based on how many own pieces are close to the center of the board.
        """
        output = 0
        for piece in self.get_pieces():
            row, col = string_to_index(piece)
            output += (8 - row) * row * (8 - col) * col
        return output

    def get_capture_heuristic(self) -> int:
        """
        Returns a score based on how many potential captures active can get, less how many opp would get on next turn.
        """
        material_advantage = len(self.get_pieces()) - len(self.get_opposing_player().get_pieces())

        # Check if any potential capture squares are reachable for both players, assume sorted best first.
        active_cap_moves = self.find_capture_moves()
        active_best = active_cap_moves[0][1] if active_cap_moves else 0
        opp_cap_moves = self.get_opposing_player().find_capture_moves()

        if not opp_cap_moves:           # No opposition, active makes best move.
            return active_best

        opp_best = opp_cap_moves[0][1]
        opp_next_best = opp_cap_moves[1][1] if len(opp_cap_moves) > 1 else 0
        tradeoff = active_best - opp_best + material_advantage      # Play more aggressive/timid based on material

        return max(tradeoff, opp_next_best)

    def get_potential_capture_heuristic(self) -> int:
        """
        Find all risky clusters and compare.
        """
        active_potential_captures = [cluster.squares for cluster in self.get_game().clusters.vulnerable_clusters[
                                         self.get_opposing_color()]]
        opp_potential_captures = [cluster.squares for cluster in self.get_game().clusters.vulnerable_clusters[
            self.get_color()]]
        num_active = len(set().union(*active_potential_captures))
        num_opp = len(set().union(*opp_potential_captures))
        return num_active - num_opp

    def get_heuristic(self) -> float:
        """
        Returns an evaluation of the current board state. Will be signed according to whether current player is max.
        """

        material_points = (len(self.get_pieces()) - len(self.get_opposing_player().get_pieces())) * AIPlayer.H_MATERIAL
        center_points = (self.get_center_heuristic() - self.get_opposing_player().get_center_heuristic()) * \
                        AIPlayer.H_CENTER
        cap_points = self.get_capture_heuristic() * AIPlayer.H_CAPTURE
        # pot_cap_points = self.get_potential_capture_heuristic() * AIPlayer.H_POT_CAP
        victory_points = AIPlayer.H_WIN if self.did_win() else 0

        total = material_points + center_points + cap_points + victory_points
        return total if self.is_maximizing else -total

    def make_ai_clone(self):
        """
        Makes an AI to pilot a Player object while calculating next move. Uses given Player's pieces but returns
        them to initial state when done.
        """
        ai_clone = AIPlayer(self.get_game(), self.get_opposing_player().get_color())
        self.set_opposing_player(ai_clone)

    def is_better_score(self, better_score: float, worse_score: float) -> bool:
        return better_score > worse_score if self.is_maximizing else better_score < worse_score

    def minimax_helper(self, depth: int, alpha: float, beta: float) -> tuple[str, float]:
        """
        Recurses alternating player moves until depth is 0 to find the most advantageous move for each player.
        """
        # Base case
        if depth == 0 or self.get_game().get_game_state() != "UNFINISHED":
            return "", self.get_heuristic()

        # Recursion
        best_score = self.initial_best_score
        best_move = ""
        possible_move_list = self.order_available_moves()

        for index, possible_move in enumerate(possible_move_list):
            self.make_move(possible_move[:2], possible_move[2:])
            sub_move, sub_score = self.get_opposing_player().minimax_helper(depth - 1, alpha, beta)
            self.undo_move()

            # Evaluation
            if self.is_better_score(sub_score, best_score):
                best_move, best_score = possible_move, sub_score
            if self.is_better_score(best_score, alpha):
                alpha = best_score
            if self.is_better_score(best_score, beta):
                beta = best_score

            # Cut short if no move will gain further advantage
            if beta <= alpha:
                break

        return best_move, best_score

    def minimax(self, depth: int) -> tuple[str, float]:
        """
        Finds the best move to make assuming opponent plays optimally. Tuple returned is (best_move, heuristic).
        """
        old_opp = self.get_opposing_player()
        self.make_ai_clone()

        next_move, heuristic = self.minimax_helper(depth, -9999, 9999)

        self.set_opposing_player(old_opp)
        print(next_move, heuristic)
        return next_move, heuristic

    def ai_make_move(self, depth: int):
        next_move = self.minimax(depth)
        self.make_move(next_move[0][:2], next_move[0][2:])


if __name__ == '__main__':
    from hasami_shogi.src.model.hasami_shogi_game import HasamiShogiGame
    import cProfile
    import pstats
    from pstats import SortKey

    g = HasamiShogiGame()
    ai1 = AIPlayer(g, "BLACK")
    ai2 = AIPlayer(g, "RED")
    ai1.set_opposing_player(ai2)
    # ai1.make_move("i5", "e5")
    # ai2.make_move("a5", "d5")
    # ai1.make_move("i1", "b1")
    cProfile.run("ai1.minimax(3)", "../controller/minimax.profile")
    p = pstats.Stats("minimax.profile")
    p.strip_dirs().sort_stats(SortKey.CUMULATIVE).print_stats()
    p.print_callees()
