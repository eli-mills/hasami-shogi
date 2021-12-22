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


def main():
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


if __name__ == '__main__':
    main()
