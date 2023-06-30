from hasami_shogi.src.controller.hasami_shogi_utilities import *
from hasami_shogi.src.controller.player import Player


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
        super().__init__(*args, **kwargs)
        self.alpha = None
        self.beta = None
        self.is_maximizing = self.get_color() == "BLACK"
        self.initial_best_score = -9999 if self.is_maximizing else 9999
        self.print_piece_sets = False

    def __repr__(self):
        return type(self).__name__ + self._color

    def find_cap_partner(self, capturing_piece, captured_piece):
        """
        Takes a game dict {'RED': {pieces}, 'BLACK': {pieces}}, and a capturing, captured pair.
        Returns tuple: square_string that would complete a capture, and how many pieces would be captured, or None if
        no capturing square found. O(N).
        """
        captured_pieces = self.get_opposing_player().get_pieces()
        all_pieces = self.get_pieces() | captured_pieces

        # Search direction: capturing -> captured
        prev_square = captured_piece
        next_square = get_next_square(capturing_piece, captured_piece)
        pot_cap_count = 1  # Know at least 1 will be captured

        # Check for linear capture
        while next_square is not None and next_square in captured_pieces:  # Checking for >1 capture
            pot_cap_count += 1
            prev_square, next_square = next_square, get_next_square(prev_square, next_square)

        if next_square is not None and next_square not in all_pieces:  # Partner square available
            return next_square, pot_cap_count

        # Check for corner capture
        partner_square = CORNER_CAP_PIECES.get(capturing_piece, None)
        if next_square is None and partner_square is not None and partner_square not in all_pieces:
            return partner_square, 1  # Corner captures only one

        return None, None  # Partner square occupied or end of board reached.

    def find_pot_cap_squares(self):
        """
        Takes game piece dict, color to capture, and optional whether player is active. Returns square: value dict
        for every square where a capture would result from a capturing color piece moving there.
        """
        # capturing_pieces = self.get_pieces()
        # captured_pieces = self.get_opposing_player().get_pieces()
        # potential_cap_pairs = {
        #     capturing_piece: {adj_square for adj_square in get_adjacent_squares(capturing_piece)}
        #     .intersection(captured_pieces) for capturing_piece in capturing_pieces
        # }
        #
        # pot_caps = {}
        #
        # for capturing_piece, captured_partners in potential_cap_pairs.items():
        #     for captured_partner in captured_partners:
        #         if not self.get_active() and self.find_cap_partner(captured_partner, capturing_piece):
        #             continue
        #         square, value = self.find_cap_partner(capturing_piece, captured_partner)
        #         if square and value:
        #             pot_caps[square] = pot_caps.get(square, 0) + value
        #
        # return pot_caps
        for cluster in self.get_game().clusters.vulnerable_clusters[self.get_opposing_color()]:
            risky_border_val = self.get_game().get_square_occupant(cluster.risky_border)
            if risky_border_val != "NONE":
                raise ValueError(f"Opponent cluster risky border is out of sync with board state: {cluster} risky "
                                 f"border at {cluster.risky_border} has board value {risky_border_val}")
        vulnerable_clusters = self.get_game().clusters.vulnerable_clusters[self.get_opposing_color()]
        return {cluster.risky_border: len(cluster) for cluster in vulnerable_clusters}

    def find_reachable_pieces(self, square_to_reach):
        """
        Checks if a given square is reachable with any of the given color's pieces. Returns set of pieces that can
        reach the given square.
        """
        return {piece for piece in self.get_pieces() if self.get_game().path_is_clear(piece, square_to_reach)}

    def find_capture_moves(self):
        """
        Given a piece dict and a set of potential capture squares: and their value, returns a tuple of 4-char move,
        capture value tuples sorted by highest to lowest value. Value is positive no matter the color.

        Calls: self.find_reachable_pieces
        """
        squares_to_check = self.find_pot_cap_squares()
        output = [(piece + square_to_reach, square_value) for square_to_reach, square_value in squares_to_check.items()
                  for piece in self.find_reachable_pieces(square_to_reach)]
        return tuple(sorted(output, key=lambda x: x[1], reverse=True))

    def find_adjacent_moves(self):
        """
        Given a piece dict and active player, returns all moves active can make to squares adjacent to opponent.
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

    def order_available_moves(self):
        """
        Returns a list of all possible moves given the current game state. Orders preferable moves first.
        """
        if not self.get_active():
            raise Exception("order_available_moves called by inactive Player.")

        capture_moves = [move[0] for move in self.find_capture_moves()]
        if any([move[:2]==move[2:] for move in capture_moves]):
            raise(ValueError(f"Illegal move proposed by capture_moves: {capture_moves}"))
        adjacent_moves = [x for x in self.find_adjacent_moves() if x not in capture_moves]
        if any([move[:2]==move[2:] for move in adjacent_moves]):
            raise(ValueError(f"Illegal move proposed by adjacent_moves: {adjacent_moves}"))
        preferred_moves = capture_moves + adjacent_moves

        remaining_moves = [move for move in self.get_all_valid_moves() if move not in preferred_moves]
        if any([move[:2]==move[2:] for move in remaining_moves]):
            raise(ValueError(f"Illegal move proposed by remaining_moves: {remaining_moves}"))
        center_moves = [move for move in remaining_moves if move[2] in "def" and move[3] in "456"]  # ends in center
        leftover_moves = [move for move in remaining_moves if move not in center_moves]

        return preferred_moves + center_moves + leftover_moves  # [:-int(len(leftover_moves)//1.2)]

    def get_center_heuristic(self):
        """
        Takes a square string and returns a point value based on how close it is to the center of the board.
        O(1).
        """
        output = 0
        for piece in self.get_pieces():
            row, col = string_to_index(piece)
            output += (8 - row) * row * (8 - col) * col
        return output

    def get_capture_heuristic(self):
        """
        Returns static evaluation of game piece dict {'RED': {pieces}, 'BLACK': {pieces}} based on potential capture
        analysis. Score represents potential net gain for active player (always non-negative).
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

    # def get_potential_capture_heuristic(self):
    #     """
    #     Find all risky clusters and compare.
    #     """
    #     active_potential_captures = [cluster.squares for cluster in self.get_game().clusters.vulnerable_clusters[
    #                                      self.get_opposing_color()]]
    #     opp_potential_captures = [cluster.squares for cluster in self.get_game().clusters.vulnerable_clusters[
    #         self.get_color()]]
    #     num_active = len(set().union(*active_potential_captures))
    #     num_opp = len(set().union(*opp_potential_captures))
    #     return num_active - num_opp

    def get_heuristic(self):
        """
        Checks a game board and returns a heuristic representing how advantageous it is for the AI. Negative is
        advantageous for RED, positive for BLACK.
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

    def evaluate_better_score(self, better_score, worse_score):
        if self.is_maximizing:
            return better_score > worse_score
        return better_score < worse_score

    def minimax_helper(self, depth, alpha, beta):
        """
        BLACK = max, RED = min
        """
        # Base case
        if depth == 0 or self.get_game().get_game_state() != "UNFINISHED":
            return None, self.get_heuristic()

        # Recursion
        best_score = self.initial_best_score
        best_move = None

        possible_move_list = self.order_available_moves()

        for index, possible_move in enumerate(possible_move_list):
            init_move_log_length = len(self.get_game().move_log)
            if not self.make_move(possible_move[:2], possible_move[2:]):
                raise ValueError(f"AI {self} made illegal move {possible_move} with pieces {self.get_pieces()}")
            if self.get_active():
                raise ValueError(f"Game failed to update active after valid move {possible_move} by {self}.")
            if len(self.get_game().move_log) != init_move_log_length + 1:
                raise ValueError(f"Move log failed to update for valid move {possible_move} by {self} with.")

            sub_move, sub_score = self.get_opposing_player().minimax_helper(depth - 1, alpha, beta)

            self.undo_move()

            if len(self.get_game().move_log) != init_move_log_length:
                raise ValueError(f"Undo move failed for {self}")

            # Evaluation
            if self.evaluate_better_score(sub_score, best_score):
                best_move, best_score = possible_move, sub_score
            if self.evaluate_better_score(best_score, alpha):
                alpha = best_score
            if self.evaluate_better_score(best_score, beta):
                beta = best_score

            # Cut short if no move will gain further advantage
            if beta <= alpha:
                break

        return best_move, best_score

    def minimax(self, depth):
        """Player uses to choose which move is best. Searches all possible moves up to depth. Returns tuple
        move_string, heuristic_value."""
        old_opp = self.get_opposing_player()
        self.make_ai_clone()
        self.print_piece_sets = True

        next_move, heuristic = self.minimax_helper(depth, -9999, 9999)

        self.set_opposing_player(old_opp)
        return next_move, heuristic

    def ai_make_move(self, depth):
        next_move = self.minimax(depth)
        print(next_move)
        self.make_move(next_move[0][:2], next_move[0][2:])


if __name__ == '__main__':
    from hasami_shogi.src.controller.hasami_shogi_game import HasamiShogiGame
    import cProfile
    import pstats
    from pstats import SortKey

    g = HasamiShogiGame()
    ai1 = AIPlayer(g, "BLACK")
    ai2 = AIPlayer(g, "RED")
    ai1.set_opposing_player(ai2)
    # ai1.make_move("i5", "e5")
    # print(ai1.positional_score)
    # ai2.make_move("a5", "d5")
    # print(ai2.positional_score)
    # ai1.make_move("i1", "b1")
    # print(ai1.positional_score)
    # ai1.undo_move()
    # ai2.undo_move()
    # ai1.undo_move()
    # print(ai1.positional_score)
    # print(ai2.positional_score)
    cProfile.run("ai1.minimax(3)", "minimax-stats")
    p = pstats.Stats("minimax-stats")
    p.strip_dirs().sort_stats(SortKey.CUMULATIVE).print_stats()
    p.print_callees()
