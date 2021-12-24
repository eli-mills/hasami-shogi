from HasamiShogiGame import HasamiShogiGame
from hasami_shogi_utilities import *


class AIPlayer(Player):
    """Defines the methods for an AI Hasami Shogi player. Inherits from regular Player class."""

    # def __init__(self, *args, **kwargs):
    #     """Inherits from Player."""
    #     super().__init__(*args, **kwargs)
    #     self._simulation_memo = {}

    def simulate_game(self, moves):
        """Simulates a game given a list of moves (4-character string, rcrc). Assumes all moves are valid.
        Returns the simulated game, the black player, and the red player in order."""
        sim_game = HasamiShogiGame()
        black_player = AIPlayer(sim_game, "BLACK")
        red_player = AIPlayer(sim_game, "RED")
        black_player.set_opposing_player(red_player)
        for move_num, move in enumerate(moves):
            if move_num%2 == 0:
                black_player.make_move(move[:2], move[2:])
            else:
                red_player.make_move(move[:2], move[2:])
        return sim_game, black_player, red_player

    def get_matching_player(self, player1, player2):
        """Returns which of the two players matches the current Player's color. Assumes at least one match."""
        return player1 if player1.get_color() == self.get_color() else player2

    def get_center_heuristic(self, square_string):
        """Takes a square string and returns a point value based on how close it is to the center of the board."""
        row, col = string_to_index(square_string)
        return (8-row)*(row)*(8-col)*(col)

    def find_capture_partner_square(self, game_piece_dict, pair, capturing_color):
        """Takes a game dict {'RED': {pieces}, 'BLACK': {pieces}}, a red,black pair, and color to capture.
        Returns a square_string, cap_count tuple, or None if no capturing square found."""
        red_pieces = game_piece_dict["RED"]
        black_pieces = game_piece_dict["BLACK"]

        pieces = red_pieces, black_pieces
        capturing_index = ["RED", "BLACK"].index(capturing_color)
        captured_index = capturing_index*(-1) + 1

        # Check if blank square on either side and potential chain.
        capturing_piece, captured_piece = pair[capturing_index], pair[captured_index]
        # Search direction: red capturing
        prev_square = captured_piece
        next_square = get_next_square_in_line(capturing_piece, captured_piece)
        if next_square is None:                                                             # Check for corner capture
            if capturing_piece in corner_capturing_pieces:
                partner_square = corner_capturing_pieces[capturing_piece]
                if partner_square not in red_pieces and partner_square not in black_pieces:
                    return partner_square, 1

        pot_cap_count = 1                                                                   # Check for linear capture
        while next_square is not None and next_square in pieces[captured_index]:
            pot_cap_count += 1
            prev_square, next_square = next_square, get_next_square_in_line(prev_square, next_square)
        if next_square not in red_pieces and next_square not in black_pieces and next_square is not None:
            return next_square, pot_cap_count

        return None

    def find_potential_captures(self, game_piece_dict, capturing_color):
        red_pieces = game_piece_dict["RED"]
        black_pieces = game_piece_dict["BLACK"]
        pieces = red_pieces, black_pieces
        capturing_index = ["RED", "BLACK"].index(capturing_color)
        captured_index = capturing_index * (-1) + 1
        capturing_pieces, captured_pieces = pieces[capturing_index], pieces[captured_index]
        pot_caps = {}

        # Check if adjacent squares of opposite color (capture potential).
        for piece in capturing_pieces:
            for adj_square in get_adjacent_squares(piece):
                if adj_square in captured_pieces:
                    cap_pair = [None, None]
                    cap_pair[capturing_index] = piece
                    cap_pair[captured_index] = adj_square
                    cap_square_and_value = self.find_capture_partner_square(game_piece_dict, tuple(cap_pair), capturing_color)
                    if cap_square_and_value:
                        square, value = cap_square_and_value[0], cap_square_and_value[1]
                        if square in pot_caps:
                            pot_caps[square] += value
                        else:
                            pot_caps[square] = value
        return pot_caps

    def find_reachable_pieces(self, game_piece_dict, square_to_reach, color_to_move):
        """Checks if a given square is reachable with any of the given color's pieces. Returns set of pieces that can
        reach the given square."""
        red_pieces = game_piece_dict["RED"]
        black_pieces = game_piece_dict["BLACK"]
        moving_pieces = game_piece_dict[color_to_move]
        output = set()

        for piece_to_move in moving_pieces:
            path = build_square_string_range(piece_to_move, square_to_reach)
            if path:
                if not any([x in red_pieces or x in black_pieces for x in path[1:]]):
                    output.add(piece_to_move)
        return output

    def find_capture_moves(self, game_piece_dict, captures_to_check, capturing_color):
        """Given a piece dict and a set of potential capture squares: and their value, returns a list of 4-char move,
        capture value tuples sorted by highest to lowest value. Value is positive no matter the color.
        Also returns a dict of reachable squares with list of movable pieces, and vice versa."""
        output = []
        for square_to_reach in captures_to_check:
            square_value = captures_to_check[square_to_reach]
            possible_pieces = self.find_reachable_pieces(game_piece_dict, square_to_reach, capturing_color)
            for piece in possible_pieces:
                output.append((piece+square_to_reach, square_value))

        return tuple(sorted(output, key=lambda x: x[1], reverse=True))

    def get_capture_heuristic(self, game_piece_dict, player_turn):
        """Given a dictionary of game pieces {'RED': {pieces}, 'BLACK': {pieces}}, returns score based on potential
        capture analysis. Score represents potential net gain for active player (always non-negative)."""
        opponent = {"RED": "BLACK", "BLACK": "RED"}[player_turn]
        score = 0

        # Get potential captures squares and their values.
        active_pot_caps = self.find_potential_captures(game_piece_dict, player_turn)
        opp_pot_caps = self.find_potential_captures(game_piece_dict, opponent)

        # Check if potential capture squares are reachable.
        active_cap_moves = self.find_capture_moves(game_piece_dict, active_pot_caps, player_turn)
        opp_cap_moves = self.find_capture_moves(game_piece_dict, opp_pot_caps, opponent)

        # Evaluate
        if active_cap_moves:
            active_best = active_cap_moves[0][1]                            # Assumes sorted best to worst move.
        else:
            active_best = 0                                                 # Best move is avoiding capture.
        if opp_cap_moves:
            tradeoff = active_best - opp_cap_moves[0][1]                    # Both to make best move.
            if len(opp_cap_moves) > 1:                                      # Opp can capture next turn either way.
                opp_next_best = opp_cap_moves[1][1]                         # Active avoids max capture.
            else:
                opp_next_best = 0                                           # Active completely avoids capture.
            score = max(tradeoff, opp_next_best)
        else:
            score = active_best                                             # No opposition, active makes best move.

        return score

    def get_heuristic(self, game=None):
        """Checks a game board and returns a heuristic representing how advantageous it is for the AI. Negative is
        advantageous for RED, positive for BLACK."""
        # Constants:
        factor_vic = 9999
        factor_mat = 200
        factor_cap = 100
        factor_cen = 1/4
        factor_color_dict = {"BLACK": {"opp": "RED", "fac": 1}, "RED": {"opp": "BLACK", "fac": -1}}

        if not game:
            game = self._game

        game_pieces = get_game_pieces(game)
        active_player = game.get_active_player()
        active_factor = factor_color_dict[active_player]["fac"]

        # Material Heuristic
        material_points = game.get_num_captured_pieces("RED") - game.get_num_captured_pieces("BLACK")
        material_points *= factor_mat

        center_points = 0

        # Center Heuristic
        for player in "RED", "BLACK":
            factor_color = factor_color_dict[player]["fac"]
            for piece in game_pieces[player]:
                center_points += self.get_center_heuristic(piece)*factor_cen*factor_color

        # Potential Capture Heuristic
        pot_cap_points = self.get_capture_heuristic(game_pieces, active_player) * factor_cap * active_factor

        # Victory Heuristic
        victory_points = 0
        game_state = game.get_game_state()
        if game_state == "RED_WON":
            victory_points += factor_vic * factor_color_dict["RED"]["fac"]
        elif game_state == "BLACK_WON":
            victory_points += factor_vic * factor_color_dict["BLACK"]["fac"]

        return material_points + center_points + pot_cap_points+ victory_points

    def find_all_available_moves(self):
        """Returns a list of all possible moves given the current game state. Orders preferable moves first."""
        all_moves = []
        game = self.get_game()
        game_pieces = get_game_pieces(game)
        active_player = game.get_active_player()
        opponent = {"RED": "BLACK", "BLACK": "RED"}[active_player]
        active_pieces = game_pieces[active_player]
        opp_pieces = game_pieces[opponent]

        active_pot_caps = self.find_potential_captures(game_pieces, active_player)
        active_cap_moves = self.find_capture_moves(game_pieces, active_pot_caps, active_player) # sorted list of tuples
        capture_moves = [move[0] for move in active_cap_moves]


        opp_adj = set()
        for opp_piece in opp_pieces:
            for adj_square in get_adjacent_squares(opp_piece):
                if adj_square not in active_pieces and adj_square not in opp_pieces:
                    opp_adj.add(adj_square)

        adjacent_moves = []

        for square_to_reach in opp_adj:
            pieces_to_move = self.find_reachable_pieces(game_pieces, square_to_reach, active_player)
            for piece in pieces_to_move:
                adjacent_moves.append(piece+square_to_reach)

        center_moves = []

        for piece in self.get_pieces():
            available_moves = return_valid_moves(self._game, piece)
            for move in available_moves:
                if move[2] in "def" and move[3] in "456":
                    center_moves.append(move)
                all_moves.append(move)

        preferred_moves = capture_moves + [x for x in adjacent_moves if x not in capture_moves]
        preferred_moves += [x for x in center_moves if x not in preferred_moves]

        leftover_moves = [x for x in all_moves if x not in preferred_moves]

        return preferred_moves + leftover_moves

    def minimax(self, depth, moves=None, max_player=None, first_time=True, alpha=None, beta=None, memo=None):
        """Player uses to choose which move is best. Searches all possible moves up to depth."""
        if first_time:
            max_player = (self.get_color() == "BLACK")
            alpha = None, -9999
            beta = None, 9999
            memo = {}
            moves = self.get_move_log()

        sim_game, sim_max, sim_min = self.simulate_game(moves)
        sim_board = tuple(get_game_pieces(sim_game)["RED"]), tuple(get_game_pieces(sim_game)["BLACK"])

        if depth == 0 or sim_game.get_game_state() != "UNFINISHED":
            return None, self.get_heuristic(sim_game)

        if max_player:
            max_eval = None, -9999
            if (sim_board, depth) in memo:
                return memo[(sim_board, depth)]
            if (sim_board, "BLACK") in memo:
                possible_move_list = memo[(sim_board, "BLACK")]
            else:
                possible_move_list = sim_max.find_all_available_moves()
                memo[(sim_board, "BLACK")] = possible_move_list
            for possible_move in possible_move_list:
                new_moves = list(moves)
                new_moves.append(possible_move)
                eval = self.minimax(depth-1, new_moves, False, False, alpha, beta, memo)
                if eval[1] > max_eval[1]:
                    max_eval = possible_move, eval[1]
                if max_eval[1] > alpha[1]:
                    alpha = possible_move, max_eval[1]
                if beta[1] <= alpha[1]:
                    break
            memo[(sim_board, depth)] = max_eval
            return max_eval
        else:
            if (sim_board, depth) in memo:
                return memo[(sim_board, depth)]
            min_eval = None, 9999
            if (sim_board, "RED") in memo:
                possible_move_list = memo[(sim_board, "RED")]
            else:
                possible_move_list = sim_min.find_all_available_moves()
                memo[(sim_board, "RED")] = possible_move_list
            for possible_move in possible_move_list:
                new_moves = list(moves)
                new_moves.append(possible_move)
                eval = self.minimax(depth-1, new_moves, True, False, alpha, beta, memo)
                if eval[1] < min_eval[1]:
                    min_eval = possible_move, eval[1]
                if min_eval[1] < beta[1]:
                    beta = possible_move, min_eval[1]
                if beta[1] <= alpha[1]:
                    break
            memo[(sim_board, depth)] = min_eval
            return min_eval


def terminal_ai():
    new_game = HasamiShogiGame()
    player_black = AIPlayer(new_game, "BLACK")
    player_red = Player(new_game, "RED")
    player_red.set_opposing_player(player_black)
    while new_game.get_game_state() == "UNFINISHED":
        print(new_game.get_active_player(), "'s turn.")
        print("BLACK's pieces:", player_black.get_pieces())
        print("RED's, pieces:", player_red.get_pieces())
        new_game.get_game_board().print_board()
        if new_game.get_active_player() == "BLACK":
            print("AI is thinking.")
            ai_move = player_black.minimax(3)[0]
            player_black.make_move(ai_move[:2], ai_move[2:])
        else:
            player_move = input("Enter a 4-char move.\n")
            player_red.make_move(player_move[:2], player_move[2:])



def main():
    new_game = HasamiShogiGame()
    ai = AIPlayer(new_game, "RED")
    game_pieces = {"RED": {'a3', 'c2', 'h3', 'e7', 'e8', 'e4', 'd4', 'c4', 'b4', 'a1', 'e6'}, "BLACK": {'a2', 'b1', 'f4', 'e5', 'i7', 'a4', 'i9'}}
    print(ai.get_capture_heuristic(game_pieces, "RED"))


if __name__ == '__main__':
    main()
