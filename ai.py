from HasamiShogiGame import HasamiShogiGame
from hasami_shogi_utilities import *


class AIPlayer(Player):
    """Defines the methods for an AI Hasami Shogi player. Inherits from regular Player class."""

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

    def get_heuristic(self, game=None):
        """Checks a game board and returns a heuristic representing how advantageous it is for the AI."""
        if not game:
            game = self._game
        material_points = game.get_num_captured_pieces("RED") - game.get_num_captured_pieces("BLACK")
        return material_points

    def possible_heuristics(self):
        """Evaluates all possible moves and their appropriate heuristics."""
        output = []
        for piece in self.get_pieces():
            possible_moves = return_valid_moves(self._game, piece)
            for move in possible_moves:
                move_log_copy = list(self.get_move_log())
                move_log_copy.append(move[:2]+move[2:])
                sim_game, sim_black, sim_red = self.simulate_game(move_log_copy)
                sim_player = self.get_matching_player(sim_black, sim_red)
                score = sim_player.get_heuristic()
                output.append([move, score])
        return output

    def compare_moves(self, movescore1, movescore2, find_max):
        """Returns the largest or smallest value of the two [move, score] lists depending if find_max True."""
        if find_max:
            return movescore1 if movescore1[1] >= movescore2[1] else movescore2
        else:
            return movescore1 if movescore1[1] <= movescore2[1] else movescore2

    def find_best_move(self, move_list, find_max):
        """Given a list of [move, score] lists, finds the maximum or minimum depending on find_max."""
        best_move = move_list[0]
        for move in move_list:
            if find_max and move[1] > best_move[1]:
                best_move = move
            elif not find_max and move[1] < best_move[1]:
                best_move = move
        return best_move

    def find_all_available_moves(self):
        """Returns a list of all possible moves given the current game state."""
        output = []
        for piece in self.get_pieces():
            available_moves = return_valid_moves(self._game, piece)
            for move in available_moves:
                output.append(move)
        return output

    def minimax(self, moves, depth, max_player=None, first_time=True, alpha=None, beta=None):
        """Player uses to choose which move is best. Searches all possible moves up to depth."""
        #print("Entering minimax", max_player, depth, moves[-1])
        self.call_count += 1
        sim_game, sim_max, sim_min = self.simulate_game(moves)
        if depth == 0 or sim_game.get_game_state() != "UNFINISHED":
            return None, self.get_heuristic(sim_game)

        if first_time:
            max_player = (self.get_color() == "BLACK")
            alpha = None, -9999
            beta = None, 9999

        if max_player:
            max_eval = None, -9999
            for possible_move in sim_max.find_all_available_moves():
                new_moves = list(moves)
                new_moves.append(possible_move)
                eval = self.minimax(new_moves, depth-1, False, False, alpha, beta)
                #print(eval)
                #print(max_eval)
                if eval[1] > max_eval[1]:
                    max_eval = possible_move, eval[1]
                if max_eval[1] > alpha[1]:
                    alpha = possible_move, max_eval[1]
                if beta[1] <= alpha[1]:
                    break
            return max_eval
        else:
            min_eval = None, 9999
            for possible_move in sim_min.find_all_available_moves():
                new_moves = list(moves)
                new_moves.append(possible_move)
                eval = self.minimax(new_moves, depth-1, True, False, alpha, beta)
                # print(eval)
                # print(min_eval)
                if eval[1] < min_eval[1]:
                    min_eval = possible_move, eval[1]
                if min_eval[1] < beta[1]:
                    beta = possible_move, min_eval[1]
                if beta[1] <= alpha[1]:
                    break
            return min_eval



def main():
    new_game = HasamiShogiGame()
    player_red = AIPlayer(new_game, "RED")
    player_black = Player(new_game, "BLACK")
    player_red.set_opposing_player(player_black)

    player_black.make_move("i3", "e3")
    player_red.make_move("a4", "e4")
    player_black.make_move("i8", "e8")
    new_game.get_game_board().print_board()
    print(player_red.minimax(player_red.get_move_log(), 3))


if __name__ == '__main__':
    main()
