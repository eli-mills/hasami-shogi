import unittest
from HasamiShogiGame import HasamiShogiGame


def run_moves(game, move_list):
    return [game.make_move(move[:2], move[2:]) for move in move_list]


class TestInit(unittest.TestCase):
    """Defines tests for the init method and all data members."""
    def test_game_state(self):
        """Asserts that the game state can be retrieved and set properly."""
        new_game = HasamiShogiGame()
        test1 = new_game.get_game_state()
        new_game.set_game_state("RED_WON")
        test2 = new_game.get_game_state()

        self.assertEqual("UNFINISHED", test1)
        self.assertEqual("RED_WON", test2)

    def test_active_player(self):
        """Asserts that the get and toggle methods work correctly for active and inactive player."""
        new_game = HasamiShogiGame()
        test1_active = new_game.get_active_player()
        test1_inactive = new_game._inactive_player
        new_game.toggle_active_player()
        test2_active = new_game.get_active_player()
        test2_inactive = new_game._inactive_player

        self.assertEqual("BLACK", test1_active)
        self.assertEqual("RED", test1_inactive)
        self.assertEqual("RED", test2_active)
        self.assertEqual("BLACK", test2_inactive)

    def test_captured_pieces(self):
        """Asserts that both players start at 0, and that the proper amount is added."""
        new_game = HasamiShogiGame()
        test1_black = new_game.get_num_captured_pieces("BLACK")
        test1_red = new_game.get_num_captured_pieces("RED")
        new_game.add_num_captured_pieces("BLACK", 1)
        new_game.add_num_captured_pieces("RED", 5)
        test2_black = new_game.get_num_captured_pieces("BLACK")
        test2_red = new_game.get_num_captured_pieces("RED")

        self.assertEqual(0, test1_black)
        self.assertEqual(0, test1_red)
        self.assertEqual(1, test2_black)
        self.assertEqual(5, test2_red)

    def test_square_occupant(self):
        """Asserts that the square occupant can be set and retrieved."""
        new_game = HasamiShogiGame()
        test1_black = new_game.get_square_occupant("i5")
        test1_none = new_game.get_square_occupant("e5")
        test1_red = new_game.get_square_occupant("a4")
        new_game.set_square_occupant("d3", "HELLO")
        test2 = new_game.get_square_occupant("d3")

        self.assertEqual("BLACK", test1_black)
        self.assertEqual("NONE", test1_none)
        self.assertEqual("RED", test1_red)
        self.assertEqual("HELLO", test2)