from hasami_shogi.src.controller.hasami_shogi_utilities import *
from hasami_shogi.src.controller.player import Player
from hasami_shogi.src.controller.game_board import GameBoard


class AIPlayer(Player):
    """
    Defines the methods for an AI Hasami Shogi player. Inherits from regular Player class.
    """

    @staticmethod
    def get_center_heuristic(square_string):
        """
        Takes a square string and returns a point value based on how close it is to the center of the board.
        O(1).
        """
        row, col = string_to_index(square_string)
        return (8 - row) * row * (8 - col) * col

    @staticmethod
    def find_cap_partner(game_piece_dict, pair):
        """
        Takes a game dict {'RED': {pieces}, 'BLACK': {pieces}}, and a capturing, captured pair.
        Returns tuple: square_string that would complete a capture, and how many pieces would be captured, or None if
        no capturing square found. O(N).
        """
        all_pieces = get_all_pieces(game_piece_dict)
        capturing_piece, captured_piece = pair
        captured_color = get_piece_color(game_piece_dict, captured_piece)
        captured_pieces = game_piece_dict[captured_color]

        # Search direction: capturing -> captured
        prev_square = captured_piece
        next_square = get_next_square(capturing_piece, captured_piece)  # O(1)

        if next_square is None:
            # Check for corner capture: O(1)
            if capturing_piece in CORNER_CAP_PIECES:
                partner_square = CORNER_CAP_PIECES[capturing_piece]
                if partner_square not in all_pieces:  # Corner partner is empty
                    return partner_square, 1  # Corner captures only one

        pot_cap_count = 1  # Know at least 1 will be captured

        # Check for linear capture: O(N)
        while next_square is not None and next_square in captured_pieces:  # Checking for >1 capture
            pot_cap_count += 1
            prev_square, next_square = next_square, get_next_square(prev_square,
                                                                    next_square)
        if next_square not in all_pieces and next_square is not None:  # Partner square available
            return next_square, pot_cap_count

        return None  # Partner square occupied or end of board reached.

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.best_move = None
        self.best_score = None
        self.alpha = None
        self.beta = None
        self.is_maximizing = self.get_color() == "BLACK"
        self.initialize_best_move()

    def initialize_best_move(self):
        self.best_score = {
            "BLACK": -9999,
            "RED": 9999
        }[self.get_color()]
        self.alpha = -9999
        self.beta = 9999

    def update_best_move(self, score, move):
        if self.is_maximizing:
            if score > self.best_score:
                self.best_move = move
                self.best_score = score
            if self.best_score > self.alpha:
                self.alpha = self.best_score
        else:
            if score < self.best_score:
                self.best_move = move
                self.best_score = score
            if self.best_score < self.beta:
                self.beta = self.best_score

    def find_pot_cap_squares(self, game_piece_dict, capturing_color, active=True):
        """
        Takes game piece dict, color to capture, and optional whether player is active. Returns square: value dict
        for every square where a capture would result from a capturing color piece moving there.

        O(N^2)

        Calls:  get_adjacent_squares
                self.find_cap_partner: O(N)
        """
        captured_color = GameBoard.opposite_color(capturing_color)
        capturing_pieces = game_piece_dict[capturing_color]
        captured_pieces = game_piece_dict[captured_color]
        pot_caps = {}

        # Check if adjacent squares of opposite color (capture potential).
        for cap_piece in capturing_pieces:  # O(N)
            for adj_square in get_adjacent_squares(cap_piece):  # O(1)
                if adj_square in captured_pieces:  # Potential capture pair found.
                    cap_pair = cap_piece, adj_square
                    if not active and self.find_cap_partner(game_piece_dict,
                                                            cap_pair[
                                                            ::-1]):  # O(N)
                        continue  # In this case, one of the capturing pieces will be captured first.

                    cap_square_and_value = self.find_cap_partner(
                        game_piece_dict, cap_pair)  # O(N)

                    # Add capture square and value to output
                    if cap_square_and_value:
                        square, value = cap_square_and_value
                        if square in pot_caps:
                            pot_caps[square] += value
                        else:
                            pot_caps[square] = value
        return pot_caps

    @staticmethod
    def find_reachable_pieces(game_piece_dict, square_to_reach, color_to_move):
        """
        Checks if a given square is reachable with any of the given color's pieces. Returns set of pieces that can
        reach the given square.

        O(N^2)

        Calls: build_square_string O(N)
        """
        all_pieces = get_all_pieces(game_piece_dict)
        moving_pieces = game_piece_dict[color_to_move]
        output = set()

        for piece_to_move in moving_pieces:  # O(N)
            path = build_square_string_range(piece_to_move,
                                             square_to_reach)  # O(N)
            if path:
                if not any([x in all_pieces for x in
                            path[1:]]):  # Check clear path. O(N)
                    output.add(piece_to_move)
        return output

    def find_capture_moves(self, game_piece_dict, captures_to_check, capturing_color):
        """
        Given a piece dict and a set of potential capture squares: and their value, returns a tuple of 4-char move,
        capture value tuples sorted by highest to lowest value. Value is positive no matter the color.

        O(N^3)

        Calls: self.find_reachable_pieces O(N^2)
        """
        output = []
        for square_to_reach in captures_to_check:  # O(N)
            square_value = captures_to_check[
                square_to_reach]  # Number of pieces that would be captured.
            possible_pieces = self.find_reachable_pieces(game_piece_dict,
                                                         square_to_reach,
                                                         capturing_color)  # O(N^2)
            for piece in possible_pieces:  # O(N)
                output.append((piece + square_to_reach, square_value))

        return tuple(sorted(output, key=lambda x: x[1], reverse=True))

    @staticmethod
    def evaluate_cap_moves(active_cap_moves, opp_cap_moves, material_advantage):
        """
        Takes game piece dict, active player's capture moves, and opponent's capture moves. Returns score based on
        best possible scenarios for both players. Score represents net material gain for active player.

        O(1)
        """

        if active_cap_moves:
            active_best = active_cap_moves[0][
                1]  # Assumes sorted best to worst move.
        else:
            active_best = 0  # Best move is avoiding capture.
        if opp_cap_moves:
            tradeoff = active_best - opp_cap_moves[0][
                1]  # Both to make best move.
            if tradeoff == 0:  # If active in lead, go for trade.
                tradeoff += material_advantage
            if len(opp_cap_moves) > 1:  # Opp can capture next turn either way.
                opp_next_best = -1 * opp_cap_moves[1][
                    1]  # Active avoids max capture.
            else:
                opp_next_best = 0  # Active completely avoids capture.
            score = max(tradeoff, opp_next_best)
        else:
            score = active_best  # No opposition, active makes best move.

        return score

    def get_capture_heuristic(self, game_piece_dict, player_turn):
        """
        Returns static evaluation of game piece dict {'RED': {pieces}, 'BLACK': {pieces}} based on potential capture
        analysis. Score represents potential net gain for active player (always non-negative).

        Calls:  self.find_pot_cap_squares O(N^2)
                self.find_capture_moves   O(N^3)
                self.evaluate_cap_moves   O(1)
        """
        opponent = GameBoard.opposite_color(player_turn)
        material_advantage = len(game_piece_dict[player_turn]) - len(
            game_piece_dict[opponent])

        # Find all potential captures squares and their values for both players.
        active_pot_caps = self.find_pot_cap_squares(game_piece_dict,
                                                    player_turn)  # O(N^2)
        opp_pot_caps = self.find_pot_cap_squares(game_piece_dict, opponent,
                                                 False)  # O(N^2)

        # Check if any potential capture squares are reachable for both players.
        active_cap_moves = self.find_capture_moves(game_piece_dict,
                                                   active_pot_caps,
                                                   player_turn)  # O(N^3)
        opp_cap_moves = self.find_capture_moves(game_piece_dict, opp_pot_caps,
                                                opponent)  # O(N^3)

        return self.evaluate_cap_moves(active_cap_moves, opp_cap_moves,
                                       material_advantage)

    def get_heuristic(self, game=None):
        """
        Checks a game board and returns a heuristic representing how advantageous it is for the AI. Negative is
        advantageous for RED, positive for BLACK.
        """
        # Constants:
        factor_vic = 9999  # Weight for a winning move
        factor_mat = 200  # Weight for number of pieces on board vs enemy's
        factor_cap = 100  # Weight for setting up a capture
        factor_cen = 1 / 16  # Weight for being in a central position
        factor_color_dict = {"BLACK": {"opp": "RED", "fac": 1},
                             "RED": {"opp": "BLACK", "fac": -1}}

        if not game:
            game = self._game

        # Setup O(1)
        game_pieces = get_game_pieces(game)
        active_player = game.get_active_player()
        active_factor = factor_color_dict[active_player][
            "fac"]  # BLACK = 1, RED = -1

        # Material Heuristic O(1)
        material_points = game.get_num_captured_pieces(
            "RED") - game.get_num_captured_pieces("BLACK")
        material_points *= factor_mat

        center_points = 0

        # Center Heuristic (calls get_center_heuristic, O(1))
        for player in "RED", "BLACK":
            factor_color = factor_color_dict[player]["fac"]
            for piece in game_pieces[player]:
                center_points += self.get_center_heuristic(
                    piece) * factor_cen * factor_color

        # Potential Capture Heuristic (calls get_capture_heuristic)
        pot_cap_points = self.get_capture_heuristic(game_pieces,
                                                    active_player) * factor_cap * active_factor

        # Victory Heuristic
        victory_points = 0
        game_state = game.get_game_state()
        if game_state == "RED_WON":
            victory_points += factor_vic * factor_color_dict["RED"]["fac"]
        elif game_state == "BLACK_WON":
            victory_points += factor_vic * factor_color_dict["BLACK"]["fac"]

        return material_points + center_points + pot_cap_points + victory_points

    def find_adjacent_moves(self, game_piece_dict, player_turn):
        """
        Given a piece dict and active player, returns all moves active can make to squares adjacent to opponent.
        """
        opponent = GameBoard.opposite_color(player_turn)
        opp_pieces = game_piece_dict[opponent]
        active_pieces = game_piece_dict[player_turn]

        opp_adj = set()
        for opp_piece in opp_pieces:
            for adj_square in get_adjacent_squares(opp_piece):
                if adj_square not in active_pieces and adj_square not in opp_pieces:
                    opp_adj.add(adj_square)

        adjacent_moves = []

        for square_to_reach in opp_adj:
            pieces_to_move = self.find_reachable_pieces(game_piece_dict,
                                                        square_to_reach,
                                                        player_turn)
            for piece in pieces_to_move:
                adjacent_moves.append(piece + square_to_reach)

        return adjacent_moves

    def find_all_available_moves(self):
        """
        Returns a list of all possible moves given the current game state. Orders preferable moves first.
        """
        game = self.get_game()
        game_pieces = get_game_pieces(game)
        active_player = game.get_active_player()

        active_pot_caps = self.find_pot_cap_squares(game_pieces, active_player)
        active_cap_moves = self.find_capture_moves(game_pieces, active_pot_caps,
                                                   active_player)  # sorted list of tuples

        capture_moves = [move[0] for move in active_cap_moves]

        adjacent_moves = [x for x in
                          self.find_adjacent_moves(game_pieces, active_player)
                          if x not in capture_moves]

        preferred_moves = capture_moves + adjacent_moves

        center_moves = []
        leftover_moves = []

        for piece in self.get_pieces():
            available_moves = return_valid_moves(self._game, piece)
            for move in available_moves:
                if move not in preferred_moves:
                    if move[2] in "def" and move[3] in "456":
                        center_moves.append(move)
                    else:
                        leftover_moves.append(move)

        preferred_moves += center_moves

        return preferred_moves + leftover_moves

    def make_ai_clone(self):
        """
        Makes an AI to pilot a Player object while calculating next move. Uses given Player's pieces but returns
        them to initial state when done.
        """
        ai_clone = AIPlayer(self.get_game(), self.get_opposing_player().get_color())
        self.set_opposing_player(ai_clone)

    def minimax_helper(self, depth, move=None, alpha=None, beta=None):
        """
        BLACK = max, RED = min
        """
        if self.get_color() == "BLACK":
            sim_max = self
            sim_min = self.get_opposing_player()
            sim_game = self.get_game()
            if move:
                self.make_move(move[:2], move[2:])
        else:
            sim_min = self
            sim_max = self.get_opposing_player()
            sim_game = self.get_game()
            if move:
                self.make_move(move[:2], move[2:])

        # Base case
        if depth == 0 or sim_game.get_game_state() != "UNFINISHED":
            if move:
                self.undo_move()
            result = None, self.get_heuristic(sim_game)
            return result

        # Recursion
        if sim_max == self:
            max_eval = None, -9999
            possible_move_list = self.find_all_available_moves()
            for possible_move in possible_move_list:
                eval = self.get_opposing_player().minimax_helper(depth - 1, possible_move, alpha, beta)
                if eval[1] > max_eval[1]:
                    max_eval = possible_move, eval[1]
                if max_eval[1] > alpha[1]:
                    alpha = possible_move, max_eval[1]
                if beta[1] <= alpha[1]:
                    break
            if move:
                self.undo_move()
            return max_eval
        else:
            min_eval = None, 9999
            possible_move_list = self.find_all_available_moves()
            for possible_move in possible_move_list:
                eval = self.get_opposing_player().minimax_helper(depth - 1, possible_move, alpha, beta)
                if eval[1] < min_eval[1]:
                    min_eval = possible_move, eval[1]
                if min_eval[1] < beta[1]:
                    beta = possible_move, min_eval[1]
                if beta[1] <= alpha[1]:
                    break
            if move:
                self.undo_move()
            return min_eval[0], min_eval[1]

    def minimax(self, depth):
        """Player uses to choose which move is best. Searches all possible moves up to depth. Returns tuple
        move_string, heuristic_value."""

        alpha = None, -9999
        beta = None, 9999
        old_opp = self.get_opposing_player()
        self.make_ai_clone()
        next_move = self.minimax_helper(depth, None, alpha, beta)
        self.set_opposing_player(old_opp)
        return next_move



    def ai_make_move(self, depth):
        next_move = self.minimax(depth)
        print(next_move)
        self.make_move(next_move[0][:2], next_move[0][2:])
