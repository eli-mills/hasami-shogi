import unittest
from hasami_shogi.src.controller.game_board import GameBoard


class TestInit(unittest.TestCase):
    """Defines tests for the init method of the GameBoard class."""
    def test_board_setup(self):
        """Asserts that board initializes correctly."""
        new_board = GameBoard()
        expected_board = [
            ['RED', 'RED', 'RED', 'RED', 'RED', 'RED', 'RED', 'RED', 'RED'],
            ['NONE', 'NONE', 'NONE', 'NONE', 'NONE', 'NONE', 'NONE', 'NONE', 'NONE'],
            ['NONE', 'NONE', 'NONE', 'NONE', 'NONE', 'NONE', 'NONE', 'NONE', 'NONE'],
            ['NONE', 'NONE', 'NONE', 'NONE', 'NONE', 'NONE', 'NONE', 'NONE', 'NONE'],
            ['NONE', 'NONE', 'NONE', 'NONE', 'NONE', 'NONE', 'NONE', 'NONE', 'NONE'],
            ['NONE', 'NONE', 'NONE', 'NONE', 'NONE', 'NONE', 'NONE', 'NONE', 'NONE'],
            ['NONE', 'NONE', 'NONE', 'NONE', 'NONE', 'NONE', 'NONE', 'NONE', 'NONE'],
            ['NONE', 'NONE', 'NONE', 'NONE', 'NONE', 'NONE', 'NONE', 'NONE', 'NONE'],
            ['BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK']
        ]
        test_board = new_board._board
        self.assertEqual(expected_board, test_board)
        test_board = new_board.get_board_list()
        self.assertEqual(expected_board, test_board)


class TestStringConversion(unittest.TestCase):
    """Defines tests for the string to index and index to string methods."""
    def test_basic_case_to_index(self):
        """Asserts that strings correctly convert to indices of the list."""
        new_board = GameBoard()
        test_indices = new_board.string_to_index("e5")
        expected_indices = (4, 4)
        self.assertEqual(test_indices, expected_indices)

    def test_corner_squares_to_index(self):
        """Asserts that the corner strings convert correctly."""
        new_board = GameBoard()
        tests = [
            new_board.string_to_index("a1"),
            new_board.string_to_index("a9"),
            new_board.string_to_index("i1"),
            new_board.string_to_index("i9")
        ]
        exp_vals = [
            (0, 0),
            (0, 8),
            (8, 0),
            (8, 8)
        ]
        self.assertEqual(exp_vals, tests)

    def test_basic_case_to_string(self):
        """Asserts that valid coordinates are correctly converted to square string."""
        new_game = GameBoard()
        test_string = new_game.index_to_string(3, 6)
        exp_string = "d7"
        self.assertEqual(exp_string, test_string)

    def test_corner_squares_to_string(self):
        """Asserts that the corner indices correctly convert to a string."""
        new_board = GameBoard()

        tests = [
            new_board.index_to_string(0, 0),
            new_board.index_to_string(0, 8),
            new_board.index_to_string(8, 0),
            new_board.index_to_string(8, 8)
        ]

        exp_vals = ["a1", "a9", "i1", "i9"]

        self.assertEqual(exp_vals, tests)


class TestSquareValues(unittest.TestCase):
    """Defines tests for handling square values."""
    def test_get_square(self):
        """Asserts that the correct square values are retrieved at the correct square strings."""
        new_board = GameBoard()
        test1 = new_board.get_square("a1")
        test2 = new_board.get_square("a5")
        test3 = new_board.get_square("a9")
        test4 = new_board.get_square("e5")
        test5 = new_board.get_square("i1")
        test6 = new_board.get_square("i5")
        test7 = new_board.get_square("i9")

        self.assertEqual("RED", test1)
        self.assertEqual("RED", test2)
        self.assertEqual("RED", test3)
        self.assertEqual("NONE", test4)
        self.assertEqual("BLACK", test5)
        self.assertEqual("BLACK", test6)
        self.assertEqual("BLACK", test7)

    def test_set_square(self):
        """Asserts that the correct square is set to the correct value."""
        new_board = GameBoard()
        new_board.set_square("e5", "BLACK")
        new_board.set_square("a1", "NONE")
        test1 = new_board.get_square("e5")
        test2 = new_board.get_square("a1")
        self.assertEqual("BLACK", test1)
        self.assertEqual("NONE", test2)


class TestBuildSquareStringRange(unittest.TestCase):
    """Defines tests for the build square string range function."""
    def test_horizontal(self):
        """Asserts that a horizontal (row) range returns correctly."""
        new_board = GameBoard()

        test1 = new_board.build_square_string_range("a1", "a9")
        test2 = new_board.build_square_string_range("e1", "e9")
        test3 = new_board.build_square_string_range("i1", "i9")

        exp1 = ['a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8', 'a9']
        exp2 = ['e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'e7', 'e8', 'e9']
        exp3 = ['i1', 'i2', 'i3', 'i4', 'i5', 'i6', 'i7', 'i8', 'i9']

        self.assertEqual(exp1, test1)
        self.assertEqual(exp2, test2)
        self.assertEqual(exp3, test3)

    def test_vertical(self):
        """Asserts that a vertical range (column) returns correctly."""
        new_board = GameBoard()
        test1 = new_board.build_square_string_range("a1", "i1")
        test2 = new_board.build_square_string_range("a5", "i5")
        test3 = new_board.build_square_string_range("a9", "i9")

        exp1 = ['a1', 'b1', 'c1', 'd1', 'e1', 'f1', 'g1', 'h1', 'i1']
        exp2 = ['a5', 'b5', 'c5', 'd5', 'e5', 'f5', 'g5', 'h5', 'i5']
        exp3 = ['a9', 'b9', 'c9', 'd9', 'e9', 'f9', 'g9', 'h9', 'i9']

        self.assertEqual(exp1, test1)
        self.assertEqual(exp2, test2)
        self.assertEqual(exp3, test3)

    def test_partial_ranges(self):
        """Asserts that a partial row or column returns correctly."""
        new_board = GameBoard()

        test_hor1 = new_board.build_square_string_range("a3", "a6")
        test_hor2 = new_board.build_square_string_range("d2", "d7")
        test_hor3 = new_board.build_square_string_range("i4", "i8")
        test_ver1 = new_board.build_square_string_range("a1", "f1")
        test_ver2 = new_board.build_square_string_range("c6", "g6")
        test_ver3 = new_board.build_square_string_range("d9", "h9")

        exp_hor1 = ['a3', 'a4', 'a5', 'a6']
        exp_hor2 = ['d2', 'd3', 'd4', 'd5', 'd6', 'd7']
        exp_hor3 = ['i4', 'i5', 'i6', 'i7', 'i8']
        exp_ver1 = ['a1', 'b1', 'c1', 'd1', 'e1', 'f1']
        exp_ver2 = ['c6', 'd6', 'e6', 'f6', 'g6']
        exp_ver3 = ['d9', 'e9', 'f9', 'g9', 'h9']

        self.assertEqual(exp_hor1, test_hor1)
        self.assertEqual(exp_hor2, test_hor2)
        self.assertEqual(exp_hor3, test_hor3)
        self.assertEqual(exp_ver1, test_ver1)
        self.assertEqual(exp_ver2, test_ver2)
        self.assertEqual(exp_ver3, test_ver3)

    def test_backwards_ranges(self):
        """Asserts that ranges always go from square1 to square2."""
        new_board = GameBoard()
        test1 = new_board.build_square_string_range("a9", "a1")
        test2 = new_board.build_square_string_range("i9", "i1")
        test3 = new_board.build_square_string_range("i1", "a1")
        test4 = new_board.build_square_string_range("i9", "a9")

        exp1 = ['a9', 'a8', 'a7', 'a6', 'a5', 'a4', 'a3', 'a2', 'a1']
        exp2 = ['i9', 'i8', 'i7', 'i6', 'i5', 'i4', 'i3', 'i2', 'i1']
        exp3 = ['i1', 'h1', 'g1', 'f1', 'e1', 'd1', 'c1', 'b1', 'a1']
        exp4 = ['i9', 'h9', 'g9', 'f9', 'e9', 'd9', 'c9', 'b9', 'a9']

        self.assertEqual(exp1, test1)
        self.assertEqual(exp2, test2)
        self.assertEqual(exp3, test3)
        self.assertEqual(exp4, test4)

    def test_single_range(self):
        """Asserts that a range of 1 returns the one square."""
        new_board = GameBoard()
        test = new_board.build_square_string_range("e4", "e4")
        self.assertEqual(["e4"], test)


if __name__ == "__main__":
    unittest.main()
