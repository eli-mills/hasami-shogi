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
        material_points = game.get_num_captured_pieces(self.get_opposing_color()) - game.get_num_captured_pieces(self.get_color())
        return material_points

    def possible_heuristics(self):
        """Evaluates all possible moves and their appropriate heuristics."""
        output = []
        for piece in self.get_pieces():
            possible_moves = return_valid_moves(self._game, piece)
            for move in possible_moves:
                move_log_copy = list(self.get_move_log())
                move_log_copy.append(move[:2]+move[2:])
                # print(move_log_copy)
                sim_game, sim_black, sim_red = self.simulate_game(move_log_copy)
                sim_player = self.get_matching_player(sim_black, sim_red)
                score = sim_player.get_heuristic()
                output.append([move, score])
                # if move == "a2e2":
                #     sim_game.get_game_board().print_board()
        return sorted(output, key=lambda l: l[1], reverse=True)

    def minimax(self, depth, moves):
        """Player uses to choose which move is best. Searches all possible moves up to depth."""
        if self._game.get_game_state != "UNFINISHED":
            return



def main():
    new_game = HasamiShogiGame()
    player_red = AIPlayer(new_game, "RED")
    player_black = Player(new_game, "BLACK")
    player_red.set_opposing_player(player_black)

    player_black.make_move("i3", "e3")
    player_red.make_move("a4", "e4")
    player_black.make_move("i8", "e8")
    new_game.get_game_board().print_board()
    print(player_red.possible_heuristics())


if __name__ == '__main__':
    main()
