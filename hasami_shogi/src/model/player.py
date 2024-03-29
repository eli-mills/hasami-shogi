from hasami_shogi.src.model.hasami_shogi_game import HasamiShogiGame
from hasami_shogi.src.model.game_board import GameBoard


class Player:
    """Defines the methods for a player of Hasami Shogi."""
    def __init__(self, game, color):
        """Initializes a player for Hasami Shogi."""
        self._game = game
        self._color = color
        self._opposing_color = {"RED": "BLACK", "BLACK": "RED"}[color]
        self._opposing_player = None

    def get_active(self) -> bool:
        """Returns True if current player is active."""
        return self._game.get_active_player() == self._color

    def get_game(self) -> HasamiShogiGame:
        """Returns the current game."""
        return self._game

    def get_board(self) -> GameBoard:
        return self.get_game().get_game_board()

    def get_color(self) -> str:
        """Returns the player's color."""
        return self._color

    def get_opposing_color(self) -> str:
        """Returns the opposing player's color."""
        return self._opposing_color

    def get_opposing_player(self) -> "Player":
        """Returns the opposing player object."""
        return self._opposing_player

    def set_opposing_player(self, player: "Player") -> None:
        """Sets the given player as opponent and sets self as given player's opponent. Must be opposite colors."""
        if player.get_color() == self._opposing_color:
            self._opposing_player = player
            player._opposing_player = self

    def get_pieces(self) -> set[str]:
        """Returns all the current player's pieces as a set."""
        return self.get_game().get_game_board().get_squares_by_color(self.get_color())

    def make_move(self, start: str, destination: str) -> bool:
        """Makes the given move in the game and updates piece locations in log and opponent's log."""
        return self._game.make_move(start, destination)

    def undo_move(self) -> None:
        """Calls undo_move on HasamiShogiGame."""
        init_move_log_length = len(self.get_game().move_log)
        self._game.undo_move()
        if len(self.get_game().move_log) != init_move_log_length - 1:
            raise ValueError(f"Undo move failed for {self}")

    def did_win(self) -> bool:
        """True if current game state reflects player victory."""
        return self.get_game().get_game_state()[:-4] == self.get_color()
