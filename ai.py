from HasamiShogiGame import HasamiShogiGame
from hasami_shogi_utilities import *

class AIPlayer(Player):
    """Defines the methods for an AI Hasami Shogi player. Inherits from regular Player class."""
    def get_heuristic(self, game=None):
        """Checks a game board and returns a heuristic representing how advantageous it is for the AI."""
        opponent = self._opposing_player.get_color()
        if not game:
            game = self._game
        material_points = game.get_num_captured_pieces(opponent) - game.get_num_captured_pieces(self.get_color())
        return material_points

    def possible_heuristics(self):
        """Evaluates all possible moves and their appropriate heuristics."""
        output = []
        for piece in self.get_pieces():
            possible_moves = return_valid_moves(self._game, piece)
            for move in possible_moves:
                sim_game = HasamiShogiGame()
                sim_player = AIPlayer(sim_game, self.get_color())
                sim_opponent = Player(sim_game, self._opposing_player.get_color())
                sim_player.set_opposing_player(sim_opponent)
                sim_player.simulate_game(self.get_move_log())
                sim_player.make_move(move[:2], move[2:])
                score = sim_player.get_heuristic(sim_game)
                output.append([move, score])
        return output


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
