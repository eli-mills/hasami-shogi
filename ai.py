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

        pot_caps = {}

        # Check if blank square on either side and potential chain.
        capturing_piece, captured_piece = pair[capturing_index], pair[captured_index]
        # Search direction: red capturing
        prev_square = captured_piece
        next_square = get_next_square_in_line(capturing_piece, captured_piece)
        if next_square is None:                                                             # Check for corner capture
            if capturing_piece in corner_capturing_pieces:
                partner_square = corner_capturing_pieces[capturing_piece]
                if partner_square not in red_pieces and partner_square not in black_pieces:
                    return pot_caps, 1

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
        """Checks if a given square is reachable with any of the given color's pieces."""
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
        capture value tuples sorted by highest to lowest value. Value is positive no matter the color."""
        output = []
        for square_to_reach in captures_to_check:
            square_value = captures_to_check[square_to_reach]
            possible_pieces = self.find_reachable_pieces(game_piece_dict, square_to_reach, capturing_color)
            for piece in possible_pieces:
                output.append((piece+square_to_reach, square_value))

        return sorted(output, key=lambda x: x[1], reverse=True)

    def get_position_heuristic(self, game_piece_dict, player_turn):
        """Given a dictionary of game pieces {'RED': {pieces}, 'BLACK': {pieces}}, returns score based on position."""
        # Get potential captures squares and their values.
        red_pot_caps = self.find_potential_captures(game_piece_dict, "RED")
        black_pot_caps = self.find_potential_captures(game_piece_dict, "BLACK")

        # Check if potential capture squares are reachable.
        red_capture_moves = self.find_capture_moves(game_piece_dict, red_pot_caps, "RED")
        black_capture_moves = self.find_capture_moves(game_piece_dict, black_pot_caps, "BLACK")

        return red_capture_moves, black_capture_moves

        # # Evaluate
        # move_dict = {"RED": red_capture_moves, "BLACK": black_capture_moves}
        # for player in move_dict:
        #     moves = move_dict[player]
        #     if player == player_turn:                           # More points awarded if current player can capture.

    def get_heuristic(self, game=None):
        """Checks a game board and returns a heuristic representing how advantageous it is for the AI."""
        # Constants:
        factor_vic = 9999
        factor_mat = 100
        factor_pos = 50
        factor_cen = 1/4
        factor_color_dict = {"BLACK": {"opp": "RED", "fac": 1}, "RED": {"opp": "BLACK", "fac": -1}}

        if not game:
            game = self._game

        # Material Heuristic
        material_points = game.get_num_captured_pieces("RED") - game.get_num_captured_pieces("BLACK")
        material_points *= factor_mat

        center_points = 0
        position_points = 0
        for player in "RED", "BLACK":
            opponent = factor_color_dict[player]["opp"]
            factor_color = factor_color_dict[player]["fac"]

            for piece in get_game_pieces(game)[player]:
                # Center Heuristic
                center_points += self.get_center_heuristic(piece)*factor_cen*factor_color

                # Positional Heuristic

        return material_points + center_points + position_points

    # def find_all_available_moves(self):
    #     """Evaluates all possible moves and their appropriate heuristics."""
    #     output = []
    #     for piece in self.get_pieces():
    #         possible_moves = return_valid_moves(self._game, piece)
    #         for move in possible_moves:
    #             move_log_copy = list(self.get_move_log())
    #             move_log_copy.append(move[:2]+move[2:])
    #             sim_game, sim_black, sim_red = self.simulate_game(move_log_copy)
    #             score = sim_black.get_heuristic()
    #             output.append([move, score])
    #     if self.get_color() == "BLACK":
    #         output = sorted(output, key=lambda x: x[1], reverse=True)
    #     else:
    #         output = sorted(output, key=lambda x: x[1])
    #     return tuple((x[0] for x in output))

    def find_all_available_moves(self):
        """Returns a list of all possible moves given the current game state."""
        output = []
        for piece in self.get_pieces():
            available_moves = return_valid_moves(self._game, piece)
            for move in available_moves:
                output.append(move)
        return output

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
            return (None, self.get_heuristic(sim_game)) if max_player else (None, self.get_heuristic(sim_game))

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
    game_pieces = {"RED": {'a3', 'c2', 'h3', 'e6', 'e7', 'e8', 'e4', 'd4', 'c4', 'b4', 'a1'}, "BLACK": {'a2', 'b1', 'f4', 'e5', 'i7', 'a4', 'i9'}}
    print(ai.get_position_heuristic(game_pieces, "RED"))


if __name__ == '__main__':
    main()
