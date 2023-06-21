import unittest
from hasami_shogi.src.controller.hasami_shogi_game import HasamiShogiGame


def run_moves(game, move_list):
    """Takes game object and list of 4-string moves."""
    return [game.make_move(move[:2], move[2:]) for move in move_list]


def set_board(game, square_val_dict):
    """Takes game object and dict of {COLOR:[square_strings]}."""
    for color in square_val_dict.keys():
        for square_string in square_val_dict[color]:
            game.set_square_occupant(square_string, color)


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
        new_game.set_square_occupant("d3", "BLACK")
        test2 = new_game.get_square_occupant("d3")

        self.assertEqual("BLACK", test1_black)
        self.assertEqual("NONE", test1_none)
        self.assertEqual("RED", test1_red)
        self.assertEqual("BLACK", test2)


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
        set_board(new_game, {"BLACK": ["e5"]})
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
        set_board(new_game, {"RED": ["e5"]})
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
                 exp_state, setup=None):
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
        test_state = game.get_game_state()

        self.assertEqual(exp_returns, test_returns)
        self.assertEqual(exp_board, test_board)
        self.assertEqual(exp_player, test_player)
        self.assertEqual(exp_black_captures, test_black_captures)
        self.assertEqual(exp_red_captures, test_red_captures)
        self.assertEqual(exp_state, test_state)

    def test_first_five_moves(self):
        """Asserts that five normal moves correclty executed."""
        moves = ["i5f5", "a7f7", "i1d1", "a9h9", "i3g3"]
        board_set = {"NONE": ["a7", "a9", "i1", "i5", "i3"],
                     "RED": ["f7", "h9"],
                     "BLACK": ["d1", "f5", "g3"]
                     }
        self.template(moves, [True]*5, board_set, "RED", 0, 0, "UNFINISHED")

    def test_horizontal_cap(self):
        """Asserts that horizontal captures behave as expected."""
        moves_black_single = ["i5e5", "a4e4", "i8e8", "a6e6"]
        exp_black_single = {"NONE": ["a4", "a6", "i5", "i8"], "RED": ["e4", "e6"], "BLACK": ["e8"]}

        moves_red_single = ["i7f7", "a6f6", "i5f5"]
        exp_red_single = {"NONE": ["a6", "i5", "i7"], "BLACK": ["f5", "f7"]}

        moves_black_double = ["i5e5", "a4e4", "i6e6", "a7e7"]
        exp_black_double = {"NONE": ["a4", "a7", "i5", "i6"], "RED": ["e4", "e7"]}

        moves_red_double = ["i2f2", "a5e5", "i7e7", "a6e6", "i4e4"]
        exp_red_double = {"NONE": ["a5", "a6", "i2", "i4", "i7"], "BLACK": ["e4", "e7", "f2"]}

        setup_black_multi = {"RED": ["f7"], "BLACK": ["f3", "f4", "f5"]}
        moves_black_multi = ["i6f6", "a2f2"]
        exp_black_multi = {"NONE": ["a2", "i6"], "RED": ["f2", "f7"]}

        setup_red_multi = {"RED": ["d3", "d4", "d5", "d6", "d7"]}
        moves_red_multi = ["i2d2", "a8d8", "i9d9"]
        exp_red_multi = {"NONE": ["a8", "i2", "i9"], "BLACK": ["d2", "d9"]}

        self.template(moves_black_single, [True] * 4, exp_black_single, "BLACK", 1, 0, "UNFINISHED")
        self.template(moves_red_single, [True] * 3, exp_red_single, "RED", 0, 1, "UNFINISHED")
        self.template(moves_black_double, [True] * 4, exp_black_double, "BLACK", 2, 0, "UNFINISHED")
        self.template(moves_red_double, [True] * 5, exp_red_double, "RED", 0, 2, "UNFINISHED")
        self.template(moves_black_multi, [True] * 2, exp_black_multi, "BLACK", 4, 0, "UNFINISHED", setup_black_multi)
        self.template(moves_red_multi, [True] * 3, exp_red_multi, "RED", 0, 6, "UNFINISHED", setup_red_multi)

    def test_vertical_cap(self):
        """Asserts that vertical captures behave as expected."""
        moves_black_single = ["i5e5", "a5d5", "i8e8", "a4f4", "i9e9", "f4f5"]
        exp_black_single = {"NONE": ["a4", "a5", "i5", "i8", "i9"], "BLACK": ["e8", "e9"], "RED": ["d5", "f5"]}

        moves_red_single = ["i7g7", "a7f7", "i2e2", "a8a7", "e2e7"]
        exp_red_single = {"NONE": ["a8", "i2", "i7"], "BLACK": ["e7", "g7"]}

        moves_black_double = ["i3c3", "a5e5", "i8d8", "e5e3", "d8d3", "a3b3"]
        exp_black_double = {"NONE": ["a3", "a5", "i3", "i8"], "RED": ["b3", "e3"]}

        moves_red_double = ["i4d4", "a2e2", "i9g9", "a6f6", "i8i9", "e2e4", "i7i8", "f6f4", "g9g4"]
        exp_red_double = {"NONE": ["a2", "a6", "i4", "i7"], "BLACK": ["d4", "g4"]}

        setup_black_multi = {"BLACK": ["d9", "e9", "f9", "g9", "h9"], "RED": ["i9", "c2"]}
        moves_black_multi = ["i1f1", "c2c9"]
        exp_black_multi = {"NONE": ["i1"], "RED": ["c9", "i9"], "BLACK": ["f1"]}

        setup_red_multi = {"BLACK": ["b2"], "RED": ["c2", "d2", "e2", "f2"]}
        moves_red_multi = ["i2g2"]
        exp_red_multi = {"NONE": ["i2"], "BLACK": ["g2", "b2"]}

        self.template(moves_black_single, [True]*6, exp_black_single, "BLACK", 1, 0, "UNFINISHED")
        self.template(moves_red_single, [True]*5, exp_red_single, "RED", 0, 1, "UNFINISHED")
        self.template(moves_black_double, [True]*6, exp_black_double, "BLACK", 2, 0, "UNFINISHED")
        self.template(moves_red_double, [True]*9, exp_red_double, "RED", 0, 2, "UNFINISHED")
        self.template(moves_black_multi, [True]*2, exp_black_multi, "BLACK", 5, 0, "UNFINISHED", setup_black_multi)
        self.template(moves_red_multi, [True], exp_red_multi, "RED", 0, 4, "UNFINISHED", setup_red_multi)

    def test_corner_cap(self):
        """Asserts that corner captures work properly."""
        board_setup = {
            "NONE": ["i2", "i8"],
            "RED": ["d9", "h1", "i3", "h9", "i9"],
            "BLACK": ["a2", "a9", "b3", "g8", "h9"]
        }
        moves = ["b3b1", "d9b9", "g8i8", "i3i2"]
        exp_board = {
            "NONE": ["a1", "a9", "i1", "i9", "i3"],
            "RED": ["b9", "h1", "i2"],
            "BLACK": ["a2", "b1", "h9"]
        }
        self.template(moves, [True]*4, exp_board, "BLACK", 2, 2, "UNFINISHED", board_setup)

    def test_double_cap_linear(self):
        """Asserts that linear double captures work as intended."""
        board_setup_up_right = {"BLACK": ["c4", "d4", "e4", "f5", "f6", "e7"], "RED": ["b4", "f8", "f2"]}
        moves_up_right = ["e7f7", "f2f4"]
        exp_board_up_right = {"RED": ["b4", "f4", "f8"]}
        self.template(moves_up_right, [True]*2, exp_board_up_right, "BLACK", 6, 0, "UNFINISHED", board_setup_up_right)

        board_setup_up_left = {"BLACK": ["c7", "h3"], "RED": ["d7", "e7", "f7", "g7", "h4", "h5", "h6"]}
        moves_up_left = ["i7h7"]
        exp_board_up_left = {"BLACK": ["c7", "h7", "h3"], "NONE": ["i7"]}
        self.template(moves_up_left, [True], exp_board_up_left, "RED", 0, 7, "UNFINISHED", board_setup_up_left)

        board_setup_down_left = {"RED": ["c3", "f6", "b6"], "BLACK": ["c4", "c5", "d7", "e6"]}
        moves_down_left = ["d7d6", "b6c6"]
        exp_board_down_left = {"RED": ["c3", "c6", "f6"]}
        self.template(moves_down_left, [True]*2, exp_board_down_left, "BLACK", 4, 0, "UNFINISHED", board_setup_down_left)

        board_setup_down_right = {"RED": ["d5", "e4"], "BLACK": ["d3", "d6", "f4"]}
        moves_down_right = ["d3d4"]
        exp_board_down_right = {"BLACK": ["d4", "d6", "f4"]}
        self.template(moves_down_right, [True], exp_board_down_right, "RED", 0, 2, "UNFINISHED", board_setup_down_right)

    def test_double_cap_corner(self):
        """Asserts that a double capture involving a corner behaves as intended."""
        board_setup_bot_right = {"RED": ["i8", "h7", "d9"], "BLACK": ["e9", "f8", "g9"]}
        moves_bot_right = ["f8f9", "h7h9"]
        exp_board_bot_right = {"RED": ["d9", "h9", "i8"], "NONE": ["i9"]}
        self.template(moves_bot_right, [True]*2, exp_board_bot_right, "BLACK", 4, 0, "UNFINISHED", board_setup_bot_right)

        board_setup_top_right = {"RED": ["c9", "d9"], "BLACK": ["a8", "b7", "e9"]}
        moves_top_right = ["b7b9"]
        exp_board_top_right = {"BLACK": ["a8", "b9", "e9"], "NONE": ["a9"]}
        self.template(moves_top_right, [True], exp_board_top_right, "RED", 0, 3, "UNFINISHED", board_setup_top_right)

        board_setup_top_left = {"RED": ["b2", "d1"], "BLACK": ["a1", "c2"]}
        moves_top_left = ["c2c1", "b2b1"]
        exp_board_top_left = {"NONE": ["a1"], "RED": ["b1", "d1"]}
        self.template(moves_top_left, [True]*2, exp_board_top_left, "BLACK", 2, 0, "UNFINISHED", board_setup_top_left)

        board_setup_bot_left = {"RED": ["b1", "c1", "d1", "e1", "f1", "g1", "i1"], "BLACK": ["a1", "h9"]}
        moves_bot_left = ["h9h1"]
        exp_board_bot_left = {"BLACK": ["a1", "h1"], "NONE": ["i1"]}
        self.template(moves_bot_left, [True], exp_board_bot_left, "RED", 0, 7, "UNFINISHED", board_setup_bot_left)

    def test_no_cap(self):
        """Asserts that moving into a capture position does not trigger a capture on the player that moved."""
        moves_hor_single = ["i3f3", "a3e3", "i5f5", "a4f4"]
        exp_board_hor_single = {
            "NONE": ["a3", "a4", "i3", "i5"],
            "BLACK": ["f3", "f5"],
            "RED": ["e3", "f4"]
        }
        self.template(moves_hor_single, [True]*4, exp_board_hor_single, "BLACK", 0, 0, "UNFINISHED")

        moves_ver_single = ["i2e2", "a5d5", "e2e3", "a6f6", "e3e4", "f6f5", "e4e5"]
        exp_board_ver_single = {
            "NONE": ["a5", "a6", "i2"],
            "BLACK": ["e5"],
            "RED": ["d5", "f5"]
        }
        self.template(moves_ver_single, [True]*7, exp_board_ver_single, "RED", 0, 0, "UNFINISHED")

        board_setup_hor_multi = {
            "RED": ["d8", "e5", "e6", "e7"],
            "BLACK": ["e4", "f9"]
        }
        moves_hor_multi = ["f9e9", "d8e8"]
        exp_board_hor_multi = {
            "RED": ["e5", "e6", "e7", "e8"],
            "BLACK": ["e4", "e9"]
        }
        self.template(moves_hor_multi, [True]*2, exp_board_hor_multi, "BLACK", 0, 0, "UNFINISHED", board_setup_hor_multi)

        board_setup_ver_multi = {
            "RED": ["c9", "h9"],
            "BLACK": ["d9", "e9", "f7", "g9"]
        }
        moves_ver_multi = ["f7f9"]
        exp_board_ver_multi = {
            "RED": ["c9", "h9"],
            "BLACK": ["d9", "e9", "f9", "g9"]
        }
        self.template(moves_ver_multi, [True], exp_board_ver_multi, "RED", 0, 0, "UNFINISHED", board_setup_ver_multi)

    def test_no_double_cap(self):
        """Asserts that double cap formation does not double capture if the moving piece is only part of one branch."""
        board_setup_up_right1 = {"BLACK": ["c4", "d4", "e4", "f5", "f6", "e7"], "RED": ["b4", "f9", "f4"]}
        moves_up_right1 = ["e7f7", "f9f8"]
        exp_board_up_right1 = {"RED": ["b4", "f4", "f8"], "BLACK": ["c4", "d4", "e4"]}
        self.template(moves_up_right1, [True]*2, exp_board_up_right1, "BLACK", 3, 0, "UNFINISHED", board_setup_up_right1)

        board_setup_up_right2 = {"BLACK": ["c4", "d4", "e4", "f5", "f6", "e7"], "RED": ["b3", "f8", "f4"]}
        moves_up_right2 = ["e7f7", "b3b4"]
        exp_board_up_right2 = {"RED": ["b4", "f4", "f8"], "BLACK": ["f5", "f6", "f7"]}
        self.template(moves_up_right2, [True] * 2, exp_board_up_right2, "BLACK", 3, 0, "UNFINISHED", board_setup_up_right2)

        board_setup_down_left1 = {"BLACK": ["d3", "f6", "c6"], "RED": ["c4", "c5", "d6", "e6"]}
        moves_down_left1 = ["d3c3"]
        exp_board_down_left1 = {"BLACK": ["c3", "c6", "f6"], "RED": {"d6", "e6"}}
        self.template(moves_down_left1, [True], exp_board_down_left1, "RED", 0, 2, "UNFINISHED", board_setup_down_left1)

        board_setup_down_left2 = {"BLACK": ["c3", "c6", "f5"], "RED": ["c4", "c5", "d6", "e6"]}
        moves_down_left2 = ["f5f6"]
        exp_board_down_left2 = {"BLACK": ["c3", "c6", "f6"], "RED": {"c4", "c5"}}
        self.template(moves_down_left2, [True], exp_board_down_left2, "RED", 0, 2, "UNFINISHED", board_setup_down_left2)


class TestWinCases(TestNormalGames):
    def test_hor_cap_single_win(self):
        """Asserts that a single horizontal capture triggers a win."""
        moves = [
            "i1e1", "a2e2", "i3e3", "a4e4", "i5e5", "a6e6", "i7e7", "a8e8",
            "i9e9", "a1a2", "e1a1", "a5a4", "e5a5", "a7a6", "e7a7"
        ]
        exp_board = {
            "NONE": ["a2", "a3", "a4", "a6", "a8", "i1", "i3", "i5", "i7", "i9"],
            "BLACK": ["a1", "a5", "a7", "e9", "e3"],
            "RED": ["a9"]
        }
        self.template(moves, [True]*15, exp_board, "RED", 0, 8, "BLACK_WON")

    def test_ver_cap_single_win(self):
        """Asserts that a single vertical capture triggers a win."""
        moves = [
            "i1b1", "a9c9", "i2d2", "a8e8", "i3f3", "a7g7",         # Setup
            "b1b5", "c9c5", "d2d5", "e8e5", "f3f5", "g7g5",         # First round of captures
            "i9b9", "c5c4", "i8d8", "e5e4", "i7f7", "g5g4",         # Setup
            "b9b5", "c4c5", "d8d5", "e4e5", "f7f5", "g4g5",         # Second round of captures
            "i6b6", "c5c6", "i4b4", "c6c4"                          # Last round of captures
        ]
        exp_board = {
            "NONE": ["a7", "a8", "a9", "i1", "i2", "i3", "i4", "i6", "i7", "i8", "i9"],
            "RED": ["c4", "e5", "g5"]
        }
        self.template(moves, [True]*28, exp_board, "BLACK", 8, 0, "RED_WON")

    def test_hor_cap_multi_win(self):
        """Asserts that a horizontal move where multiple pieces are captured triggers a win."""
        board_setup = {
            "BLACK": ["e2", "d3", "f2", "g3", "g4", "g5", "g6", "g7", "g8"],
            "RED": ["d1", "g1"]
        }
        moves = ["e2d2", "a4d4", "f2g2", "a9g9"]
        exp_board = {
            "NONE": ["a4", "a9"],
            "RED": ["d1", "d4", "g1", "g9"],
        }
        self.template(moves, [True]*4, exp_board, "BLACK", 9, 0, "RED_WON", board_setup)

    def test_double_cap_win(self):
        """Asserts that a win on a double capture works."""
        board_setup = {
            "BLACK": ["a2", "d1", "g1", "f9", "b3"],
            "RED": ["c2", "f2", "f3", "f4", "f5", "f6", "f7", "f8"]
        }
        moves = ["g1f1", "c2c1", "b3b1"]
        exp_board = {
            "BLACK": ["a2", "b1", "f1", "f9", "d1"],
            "NONE": ["a1"]
        }
        self.template(moves, [True]*3, exp_board, "RED", 0, 9, "BLACK_WON", board_setup)


if __name__ == "__main__":
    unittest.main()
