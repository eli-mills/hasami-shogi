import unittest
from HasamiShogiGame import HasamiShogiGame


def run_moves(game, move_list):
    return [game.make_move(move[:2], move[2:]) for move in move_list]


class TestInit(unittest.TestCase):
    """Defines tests for the init method."""