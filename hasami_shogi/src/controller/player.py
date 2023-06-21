class Player:
    """Defines the methods for a player of Hasami Shogi."""
    def __init__(self, game, color):
        """Initializes a player for Hasami Shogi."""
        self._game = game
        self._color = color
        self._opposing_color = {"RED": "BLACK", "BLACK": "RED"}[color]
        self._pieces = {
            "RED": {'a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8', 'a9'},
            "BLACK": {'i1', 'i2', 'i3', 'i4', 'i5', 'i6', 'i7', 'i8', 'i9'}
        }[color]
        self._opposing_player = None
        self._move_log = []             # List of strings
        self._is_active = False
        self.update_active()

    def update_active(self):
        """Checks the game status and updates whether the Player is the active player."""
        self._is_active = (self._game.get_active_player() == self._color)

    def get_active(self):
        """Returns True if current player is active."""
        return self._is_active

    def get_game(self):
        """Returns the current game."""
        return self._game

    def get_color(self):
        """Returns the player's color."""
        return self._color

    def get_opposing_color(self):
        """Returns the opposing player's color."""
        return self._opposing_color

    def get_opposing_player(self):
        """Returns the opposing player object."""
        return self._opposing_player

    def set_opposing_player(self, player):
        """Sets the given player as opponent and sets self as given player's opponent. Must be opposite colors."""
        if player.get_color() == self._opposing_color:
            self._opposing_player = player
            player._opposing_player = self

    def get_pieces(self):
        """Returns all the current player's pieces as a set."""
        return self._pieces

    def move_piece(self, start, end):
        """Removes start square from piece list and adds end square."""
        self._pieces.remove(start)
        self._pieces.add(end)

    def remove_pieces(self, piece_list):
        """Removes squares in given list from the Player's piece set."""
        for square in piece_list:
            self._pieces.remove(square)

    def add_pieces(self, piece_list):
        """Adds squares in given list to the Player's piece set."""
        for square in piece_list:
            self._pieces.add(square)

    def get_move_log(self):
        """Returns the current move log."""
        return self._move_log

    def add_to_move_log(self, move):
        """Adds a 4-char move to the move log."""
        self._move_log.append(move)

    def check_right_color(self, square):
        """Returns true if square is in player's list."""
        return square in self.get_pieces()

    def remove_captured_pieces(self):
        """Finds and removes the captured squares from the opponent's list."""
        old_set = set(self._opposing_player.get_pieces())
        for piece in old_set:
            if self._game.get_square_occupant(piece) == "NONE":
                self._opposing_player.remove_pieces([piece])

    def make_move(self, start, destination):
        """Makes the given move in the game and updates piece locations in log and opponent's log."""
        prev_captures = self._game.get_num_captured_pieces(self._opposing_color)
        if self._game.make_move(start, destination):
            if self._is_active:
                self.move_piece(start, destination)
            self.add_to_move_log(start+destination)
            self.update_active()
            if self._opposing_player:
                self._opposing_player.add_to_move_log(start+destination)
                self._opposing_player.update_active()
            if prev_captures != self._game.get_num_captured_pieces(self._opposing_color):   # Pieces were captured
                self.remove_captured_pieces()
            return True
        return False

    def undo_move(self):
        """Calls undo_move on HasamiShogiGame and handles restoring correct pieces to both players."""
        results = self._game.undo_move()
        if results is None:
            return
        move, cap_pieces = results
        self.move_piece(move[2:], move[:2])
        if cap_pieces is not None:
            self._opposing_player.add_pieces(cap_pieces)
        self.update_active()

    # def simulate_game(self, moves):
    #     """Simulates a game given a list of moves (4-character string, rcrc). Assumes all moves are valid.
    #     Returns the simulated game, the black player, and the red player in order."""
    #     sim_game = HasamiShogiGame()
    #     black_player = AIPlayer(sim_game, "BLACK")
    #     red_player = AIPlayer(sim_game, "RED")
    #     black_player.set_opposing_player(red_player)
    #     for move_num, move in enumerate(moves):
    #         if move_num%2 == 0:
    #             black_player.make_move(move[:2], move[2:])
    #         else:
    #             red_player.make_move(move[:2], move[2:])
    #     return sim_game, black_player, red_player
    #
    # def get_matching_player(self, player1, player2):
    #     """Returns which of the two players matches the current Player's color. Assumes at least one match."""
    #     return player1 if player1.get_color() == self.get_color() else player2
    #
    # def get_center_heuristic(self, square_string):
    #     """Takes a square string and returns a point value based on how close it is to the center of the board."""
    #     row, col = string_to_index(square_string)
    #     return (8-row)*(row)*(8-col)*(col)
    #
    # def find_cap_partner(self, game_piece_dict, pair):
    #     """Takes a game dict {'RED': {pieces}, 'BLACK': {pieces}}, and a capturing, captured pair.
    #     Returns tuple: square_string that would complete a capture, and how many pieces would be captured, or None if
    #     no capturing square found."""
    #     all_pieces = get_all_pieces(game_piece_dict)
    #     capturing_piece, captured_piece = pair
    #     captured_color = get_piece_color(game_piece_dict, captured_piece)
    #     captured_pieces = game_piece_dict[captured_color]
    #
    #     # Search direction: capturing -> captured
    #     prev_square = captured_piece
    #     next_square = get_next_square(capturing_piece, captured_piece)
    #     if next_square is None:                                                             # Check for corner capture
    #         if capturing_piece in CORNER_CAP_PIECES:
    #             partner_square = CORNER_CAP_PIECES[capturing_piece]
    #             if partner_square not in all_pieces:                          # Corner partner is empty
    #                 return partner_square, 1                                                # Corner captures only one
    #
    #     pot_cap_count = 1                                                                   # Check for linear capture
    #     while next_square is not None and next_square in captured_pieces:                   # Checking for >1 capture
    #         pot_cap_count += 1
    #         prev_square, next_square = next_square, get_next_square(prev_square, next_square)
    #     if next_square not in all_pieces and next_square is not None:         # Partner square available
    #         return next_square, pot_cap_count
    #
    #     return None                                                 # Partner square occupied or end of board reached.
    #
    # def find_pot_cap_squares(self, game_piece_dict, capturing_color, active=True):
    #     """Takes game piece dict, color to capture, and optional whether player is active. Returns square: value dict
    #     for every square where a capture would result from a capturing color piece moving there."""
    #     captured_color = opposite_color(capturing_color)
    #     capturing_pieces = game_piece_dict[capturing_color]
    #     captured_pieces = game_piece_dict[captured_color]
    #     pot_caps = {}
    #
    #     # Check if adjacent squares of opposite color (capture potential).
    #     for cap_piece in capturing_pieces:
    #         for adj_square in get_adjacent_squares(cap_piece):
    #             if adj_square in captured_pieces:                                       # Potential capture pair found.
    #                 cap_pair = cap_piece, adj_square
    #                 if not active and self.find_cap_partner(game_piece_dict, cap_pair[::-1]):
    #                     continue                # In this case, one of the capturing pieces will be captured first.
    #                 cap_square_and_value = self.find_cap_partner(game_piece_dict, cap_pair)
    #                 if cap_square_and_value:
    #                     square, value = cap_square_and_value
    #                     if square in pot_caps:
    #                         pot_caps[square] += value
    #                     else:
    #                         pot_caps[square] = value
    #     return pot_caps
    #
    # def find_reachable_pieces(self, game_piece_dict, square_to_reach, color_to_move):
    #     """Checks if a given square is reachable with any of the given color's pieces. Returns set of pieces that can
    #     reach the given square."""
    #     all_pieces = get_all_pieces(game_piece_dict)
    #     moving_pieces = game_piece_dict[color_to_move]
    #     output = set()
    #
    #     for piece_to_move in moving_pieces:
    #         path = build_square_string_range(piece_to_move, square_to_reach)
    #         if path:
    #             if not any([x in all_pieces for x in path[1:]]):                                        # Path is clear.
    #                 output.add(piece_to_move)
    #     return output
    #
    # def find_capture_moves(self, game_piece_dict, captures_to_check, capturing_color):
    #     """Given a piece dict and a set of potential capture squares: and their value, returns a tuple of 4-char move,
    #     capture value tuples sorted by highest to lowest value. Value is positive no matter the color."""
    #     output = []
    #     for square_to_reach in captures_to_check:
    #         square_value = captures_to_check[square_to_reach]           # Number of pieces that would be captured.
    #         possible_pieces = self.find_reachable_pieces(game_piece_dict, square_to_reach, capturing_color)
    #         for piece in possible_pieces:
    #             output.append((piece+square_to_reach, square_value))
    #
    #     return tuple(sorted(output, key=lambda x: x[1], reverse=True))
    #
    # def evaluate_cap_moves(self, active_cap_moves, opp_cap_moves, material_advantage):
    #     """Takes game piece dict, active player's capture moves, and opponent's capture moves. Returns score based on
    #     best possible scenarios for both players. Score represents net material gain for active player."""
    #
    #     if active_cap_moves:
    #         active_best = active_cap_moves[0][1]                                # Assumes sorted best to worst move.
    #     else:
    #         active_best = 0                                                     # Best move is avoiding capture.
    #     if opp_cap_moves:
    #         tradeoff = active_best - opp_cap_moves[0][1]                        # Both to make best move.
    #         if tradeoff == 0:                                                   # If active in lead, go for trade.
    #             tradeoff += material_advantage
    #         if len(opp_cap_moves) > 1:                                          # Opp can capture next turn either way.
    #             opp_next_best = -1 * opp_cap_moves[1][1]                        # Active avoids max capture.
    #         else:
    #             opp_next_best = 0                                               # Active completely avoids capture.
    #         score = max(tradeoff, opp_next_best)
    #     else:
    #         score = active_best                                                 # No opposition, active makes best move.
    #
    #     return score
    #
    # def get_capture_heuristic(self, game_piece_dict, player_turn):
    #     """Returns static evaluation of game piece dict {'RED': {pieces}, 'BLACK': {pieces}} based on potential capture
    #     analysis. Score represents potential net gain for active player (always non-negative)."""
    #     opponent = opposite_color(player_turn)
    #     material_advantage = len(game_piece_dict[player_turn]) - len(game_piece_dict[opponent])
    #
    #     # Find all potential captures squares and their values for both players.
    #     active_pot_caps = self.find_pot_cap_squares(game_piece_dict, player_turn)
    #     opp_pot_caps = self.find_pot_cap_squares(game_piece_dict, opponent, False)
    #
    #     # Check if any potential capture squares are reachable for both players.
    #     active_cap_moves = self.find_capture_moves(game_piece_dict, active_pot_caps, player_turn)
    #     opp_cap_moves = self.find_capture_moves(game_piece_dict, opp_pot_caps, opponent)
    #
    #     return self.evaluate_cap_moves(active_cap_moves, opp_cap_moves, material_advantage)
    #
    # def get_heuristic(self, game=None):
    #     """Checks a game board and returns a heuristic representing how advantageous it is for the AI. Negative is
    #     advantageous for RED, positive for BLACK."""
    #     # Constants:
    #     factor_vic = 9999
    #     factor_mat = 200
    #     factor_cap = 100
    #     factor_cen = 1/16
    #     factor_color_dict = {"BLACK": {"opp": "RED", "fac": 1}, "RED": {"opp": "BLACK", "fac": -1}}
    #
    #     if not game:
    #         game = self._game
    #
    #     game_pieces = get_game_pieces(game)
    #     active_player = game.get_active_player()
    #     active_factor = factor_color_dict[active_player]["fac"]
    #
    #     # Material Heuristic
    #     material_points = game.get_num_captured_pieces("RED") - game.get_num_captured_pieces("BLACK")
    #     material_points *= factor_mat
    #
    #     center_points = 0
    #
    #     # Center Heuristic
    #     for player in "RED", "BLACK":
    #         factor_color = factor_color_dict[player]["fac"]
    #         for piece in game_pieces[player]:
    #             center_points += self.get_center_heuristic(piece)*factor_cen*factor_color
    #
    #     # Potential Capture Heuristic
    #     pot_cap_points = self.get_capture_heuristic(game_pieces, active_player) * factor_cap * active_factor
    #
    #     # Victory Heuristic
    #     victory_points = 0
    #     game_state = game.get_game_state()
    #     if game_state == "RED_WON":
    #         victory_points += factor_vic * factor_color_dict["RED"]["fac"]
    #     elif game_state == "BLACK_WON":
    #         victory_points += factor_vic * factor_color_dict["BLACK"]["fac"]
    #
    #     return material_points + center_points + pot_cap_points+ victory_points
    #
    # def find_adjacent_moves(self, game_piece_dict, player_turn):
    #     """Given a piece dict and active player, returns all moves active can make to squares adjacent to opponent."""
    #     opponent = opposite_color(player_turn)
    #     opp_pieces = game_piece_dict[opponent]
    #     active_pieces = game_piece_dict[player_turn]
    #
    #     opp_adj = set()
    #     for opp_piece in opp_pieces:
    #         for adj_square in get_adjacent_squares(opp_piece):
    #             if adj_square not in active_pieces and adj_square not in opp_pieces:
    #                 opp_adj.add(adj_square)
    #
    #     adjacent_moves = []
    #
    #     for square_to_reach in opp_adj:
    #         pieces_to_move = self.find_reachable_pieces(game_piece_dict, square_to_reach, player_turn)
    #         for piece in pieces_to_move:
    #             adjacent_moves.append(piece + square_to_reach)
    #
    #     return adjacent_moves
    #
    # def find_all_available_moves(self):
    #     """Returns a list of all possible moves given the current game state. Orders preferable moves first."""
    #     game = self.get_game()
    #     game_pieces = get_game_pieces(game)
    #     active_player = game.get_active_player()
    #
    #     active_pot_caps = self.find_pot_cap_squares(game_pieces, active_player)
    #     active_cap_moves = self.find_capture_moves(game_pieces, active_pot_caps, active_player) # sorted list of tuples
    #
    #     capture_moves = [move[0] for move in active_cap_moves]
    #
    #     adjacent_moves = [x for x in self.find_adjacent_moves(game_pieces, active_player) if x not in capture_moves]
    #
    #     preferred_moves = capture_moves + adjacent_moves
    #
    #     center_moves = []
    #     leftover_moves = []
    #
    #     for piece in self.get_pieces():
    #         available_moves = return_valid_moves(self._game, piece)
    #         for move in available_moves:
    #             if move not in preferred_moves:
    #                 if move[2] in "def" and move[3] in "456":
    #                     center_moves.append(move)
    #                 else:
    #                     leftover_moves.append(move)
    #
    #     preferred_moves += center_moves
    #
    #     return preferred_moves + leftover_moves
    #
    # def minimax(self, depth, move=None, max_player=None, first_time=True, alpha=None, beta=None):
    #     """Player uses to choose which move is best. Searches all possible moves up to depth."""
    #
    #     if first_time:
    #         max_player = (self.get_color() == "BLACK")
    #         alpha = None, -9999
    #         beta = None, 9999
    #
    #     if self.get_color() == "BLACK":
    #         sim_max = pickle.loads(pickle.dumps(self))
    #         sim_min = sim_max.get_opposing_player()
    #         sim_game = sim_max.get_game()
    #         if move: sim_max.make_move(move[:2], move[2:])
    #     else:
    #         sim_min = pickle.loads(pickle.dumps(self))
    #         sim_max = sim_min.get_opposing_player()
    #         sim_game = sim_min.get_game()
    #         if move: sim_min.make_move(move[:2], move[2:])
    #
    #     if depth == 0 or sim_game.get_game_state() != "UNFINISHED":
    #         return None, self.get_heuristic(sim_game)
    #
    #     if max_player:
    #         max_eval = None, -9999
    #         possible_move_list = sim_max.find_all_available_moves()
    #         for possible_move in possible_move_list:
    #             eval = sim_max.minimax(depth-1, possible_move, False, False, alpha, beta)
    #             if eval[1] > max_eval[1]:
    #                 max_eval = possible_move, eval[1]
    #             if max_eval[1] > alpha[1]:
    #                 alpha = possible_move, max_eval[1]
    #             if beta[1] <= alpha[1]:
    #                 break
    #         return max_eval
    #     else:
    #         min_eval = None, 9999
    #         possible_move_list = sim_min.find_all_available_moves()
    #         for possible_move in possible_move_list:
    #             eval = sim_min.minimax(depth-1, possible_move, True, False, alpha, beta)
    #             if eval[1] < min_eval[1]:
    #                 min_eval = possible_move, eval[1]
    #             if min_eval[1] < beta[1]:
    #                 beta = possible_move, min_eval[1]
    #             if beta[1] <= alpha[1]:
    #                 break
    #         return min_eval[0], min_eval[1]
    #
    # def ai_make_move(self, depth):
    #     next_move = self.minimax(depth)
    #     print(next_move)
    #     self.make_move(next_move[:2], next_move[2:])
