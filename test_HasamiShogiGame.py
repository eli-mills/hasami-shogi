import unittest
from HasamiShogiGame import HasamiShogiGame


def run_moves(game, move_list):
    """Takes game object and list of 4-string moves."""
    return [game.make_move(move[:2], move[2:]) for move in move_list]


def set_board(game, square_val_list):
    """Takes game object and list of square-player strings with no spaces."""
    for square_val in square_val_list:
        game.set_square_occupant(square_val[:2], square_val[2:])


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


class TestWrongMakeMove(unittest.TestCase):
    """Defines tests for cases in which the wrong move is made."""
    def test_none_to_none(self):
        """Asserts that make_move returns False to move NONE to NONE and the gameboard is unchanged."""
        new_game = HasamiShogiGame()
        exp_board = list(new_game.get_game_board().get_board_list())
        none_to_none_moves = ["d5b5", "e3e9", "b2g2", "c8c2"]

        test_none_to_none = run_moves(new_game, none_to_none_moves)
        test_board = list(new_game.get_game_board().get_board_list())
        test_player = new_game.get_active_player()

        self.assertEqual([False]*4, test_none_to_none)
        self.assertEqual(exp_board, test_board)
        self.assertEqual("BLACK", test_player)

    def test_none_to_inactive(self):
        """Asserts that moving NONE to the inactive player returns False."""
        new_game = HasamiShogiGame()
        new_game.set_square_occupant("c5", "RED")
        new_game.set_square_occupant("g5", "RED")
        new_game.set_square_occupant("e2", "RED")
        new_game.set_square_occupant("e8", "RED")
        exp_board = list(new_game.get_game_board().get_board_list())
        none_to_red_moves = ["e5c5", "e5g5", "e5e2", "e5e8"]

        test_none_to_red = run_moves(new_game, none_to_red_moves)
        test_board = list(new_game.get_game_board().get_board_list())
        test_player = new_game.get_active_player()
        test_red_cap = new_game.get_num_captured_pieces("RED")

        self.assertEqual([False]*4, test_none_to_red)
        self.assertEqual(exp_board, test_board)
        self.assertEqual("BLACK", test_player)
        self.assertEqual(0, test_red_cap)

    def test_none_to_active(self):
        """Asserts that moving NONE to the active player returns False."""
        new_game = HasamiShogiGame()
        new_game.set_square_occupant("c5", "BLACK")
        new_game.set_square_occupant("g5", "BLACK")
        new_game.set_square_occupant("e2", "BLACK")
        new_game.set_square_occupant("e8", "BLACK")
        exp_board = list(new_game.get_game_board().get_board_list())
        none_to_black_moves = ["e5c5", "e5g5", "e5e2", "e5e8"]

        test_none_to_black = run_moves(new_game, none_to_black_moves)
        test_board = list(new_game.get_game_board().get_board_list())
        test_player = new_game.get_active_player()
        test_red_cap = new_game.get_num_captured_pieces("BLACK")

        self.assertEqual([False]*4, test_none_to_black)
        self.assertEqual(exp_board, test_board)
        self.assertEqual("BLACK", test_player)
        self.assertEqual(0, test_red_cap)

    def test_non_linear(self):
        """Asserts that a non-vertical/horizontal move returns False.."""
        new_game = HasamiShogiGame()
        set_board(new_game, ["e5BLACK"])
        exp_board = list(new_game.get_game_board().get_board_list())
        non_linear_moves = ["e5b2", "e5b8", "e5h8", "e5h2",
                            "e5a1", "e5a9", "e5i1", "e5i9"]

        test_non_linear = run_moves(new_game, non_linear_moves)
        test_board = list(new_game.get_game_board().get_board_list())
        test_player = new_game.get_active_player()

        self.assertEqual([False] * 8, test_non_linear)
        self.assertEqual(exp_board, test_board)
        self.assertEqual("BLACK", test_player)

    def test_move_inactive(self):
        """Asserts that an attempt to move the inactive player returns False."""
        new_game = HasamiShogiGame()
        set_board(new_game, ["e5RED"])
        exp_board = list(new_game.get_game_board().get_board_list())
        inactive_moves = ["e5b5", "e5e9", "e5h5", "e5e1", "e5a5",
                          "e5i5", "a5f5", "a1b1", "a1a2", "a9a8"]

        test_inactive_move = run_moves(new_game, inactive_moves)
        test_board = list(new_game.get_game_board().get_board_list())
        test_player = new_game.get_active_player()

        self.assertEqual([False]*10, test_inactive_move)
        self.assertEqual(exp_board, test_board)
        self.assertEqual("BLACK", test_player)

    def test_move_after_win(self):
        """Asserts that an attempted move returns False if game finished."""
        new_game = HasamiShogiGame()
        exp_board = list(new_game.get_game_board().get_board_list())
        new_game.set_game_state("BLACK_WON")

        test_move_red = new_game.make_move("a4", "f4")
        test_move_black = new_game.make_move("i8", "c8")
        test_board = list(new_game.get_game_board().get_board_list())
        test_player = new_game.get_active_player()

        self.assertFalse(test_move_red)
        self.assertFalse(test_move_black)
        self.assertEqual(exp_board, test_board)
        self.assertEqual("BLACK", test_player)


class TestNormalGames(unittest.TestCase):
    def template(self, move_list, exp_returns, exp_board_set, exp_player, exp_black_captures, exp_red_captures,
                 setup=None):
        game = HasamiShogiGame()
        sim_game = HasamiShogiGame()
        set_board(sim_game, exp_board_set)
        exp_board = list(sim_game.get_game_board().get_board_list())

        if setup:
            set_board(game, setup)

        test_returns = run_moves(game, move_list)
        test_board = list(game.get_game_board().get_board_list())
        test_player = game.get_active_player()
        test_black_captures = game.get_num_captured_pieces("BLACK")
        test_red_captures = game.get_num_captured_pieces("RED")

        self.assertEqual(exp_returns, test_returns)
        self.assertEqual(exp_board, test_board)
        self.assertEqual(exp_player, test_player)
        self.assertEqual(exp_black_captures, test_black_captures)
        self.assertEqual(exp_red_captures, test_red_captures)

    def test_first_five_moves(self):
        """Asserts that five normal moves correclty executed."""
        moves = ["i5f5", "a7f7", "i1d1", "a9h9", "i3g3"]
        board_set = ["a7NONE", "a9NONE", "d1BLACK", "f5BLACK", "f7RED",
                     "h9RED", "i1NONE", "i5NONE", "g3BLACK", "i3NONE"]
        self.template(moves, [True]*5, board_set, "RED", 0, 0)

    def test_horizontal_cap(self):
        """Asserts that horizontal captures behave as expected."""
        moves_black_single = ["i5e5", "a4e4", "i8e8", "a6e6"]
        exp_black_single = ["a4NONE", "a6NONE", "e4RED", "e6RED", "e8BLACK", "i5NONE", "i8NONE"]

        moves_red_single = ["i7f7", "a6f6", "i5f5"]
        exp_red_single = ["a6NONE", "f5BLACK", "f7BLACK", "i5NONE", "i7NONE"]

        moves_black_double = ["i5e5", "a4e4", "i6e6", "a7e7"]
        exp_black_double = ["a4NONE", "a7NONE", "e4RED", "e7RED", "i5NONE", "i6NONE"]

        moves_red_double = ["i4e4", "a5e5", "i2f2", "a6e6", "i7e7"]
        exp_red_double = ["a5NONE", "a6NONE", "e4BLACK", "e7BLACK", "f2BLACK", "i2NONE", "i4NONE", "i7NONE"]

        setup_black_multi = ["f2RED", "f3BLACK", "f4BLACK", "f5BLACK"]
        moves_black_multi = ["i6f6", "a7f7"]
        exp_black_multi = ["a7NONE", "f2RED", "f7RED", "i6NONE"]

        setup_red_multi = ["d3RED", "d4RED", "d5RED", "d6RED", "d7RED"]
        moves_red_multi = ["i2d2", "a8d8", "i9d9"]
        exp_red_multi = ["a8NONE", "d2BLACK", "d9BLACK", "i2NONE", "i9NONE"]

        self.template(moves_black_single, [True]*4, exp_black_single, "BLACK", 1, 0)
        self.template(moves_red_single, [True]*3, exp_red_single, "RED", 0, 1)
        self.template(moves_black_double, [True]*4, exp_black_double, "BLACK", 2, 0)
        self.template(moves_red_double, [True]*5, exp_red_double, "RED", 0, 2)
        self.template(moves_black_multi, [True]*2, exp_black_multi, "BLACK", 4, 0, setup_black_multi)
        self.template(moves_red_multi, [True]*3, exp_red_multi, "RED", 0, 6, setup_red_multi)


