from hasami_shogi.src.controller.game_board import GameBoard
from hasami_shogi.src.controller.capture_cluster import CaptureCluster, VertCapCluster, HorCapCluster
from hasami_shogi.src.controller.cluster_collection import CapClusterCollection, TubeCollection
import hasami_shogi.src.controller.hasami_shogi_utilities as utils


class ShogiMove:
    """Defines data structure for recording a move in Hasami Shogi."""

    def __init__(self):
        self.player = \
            self.move = \
            self.cap_color = \
            None
        self.cap_squares = []

    def __repr__(self):
        output = self.move
        output += f" CAPTURED {self.cap_squares}, color {self.cap_color}" if self.cap_squares else ""
        return output


class HasamiShogiGame:
    """Defines the methods for a game of Hasami Shogi."""

    def __init__(self):
        """Creates a new board, sets game state to UNFINISHED,
        active player to BLACK, captured pieces to 0."""
        self._game_board = GameBoard()
        self._game_state = "UNFINISHED"  # UNFINISHED, RED_WON, BLACK_WON
        self._active_player = "BLACK"  # BLACK, RED
        self._inactive_player = "RED"  # BLACK, RED
        self._captured_pieces = {"RED": 0, "BLACK": 0}
        self.move_log = []

        self.clusters = CapClusterCollection(board=self._game_board)
        self.tubes = TubeCollection(board=self._game_board)

    def get_game_board(self) -> GameBoard:
        """Returns the game board object."""
        return self._game_board

    def get_game_state(self):
        """Returns the current game state."""
        return self._game_state

    def set_game_state(self, game_state):
        """Sets the game state to the given value."""
        self._game_state = game_state

    def get_active_player(self):
        """Returns the current player."""
        return self._active_player

    def toggle_active_player(self):
        """Switches the active player to the other color."""
        self._active_player, self._inactive_player = self._inactive_player, self._active_player

    def get_num_captured_pieces(self, player_color):
        """Returns the number of captured pieces of the given color."""
        return self._captured_pieces[player_color]

    def add_num_captured_pieces(self, player_color, num_captured):
        """Adds the given number to the captured pieces of the given color."""
        self._captured_pieces[player_color] += num_captured

    def get_square_occupant(self, square_string):
        """Returns the value at the given square on the board: RED, BLACK, or NONE."""
        return self.get_game_board().get_square(square_string)

    def set_square_occupant(self, square_string, value):
        """Sets the occupant at the given square to the given value."""
        old_value = self.get_square_occupant(square_string)
        self.get_game_board().set_square(square_string, value)
        if old_value != "NONE":
            self.clusters.update_clusters_departing(square_string)
        if value != "NONE":
            self.clusters.update_clusters_arriving(square_string)

    def set_square_occupants(self, list_of_squares, value):
        """
        Sets each square in the given list to the given value.
        """
        for square in list_of_squares:
            self.set_square_occupant(square, value)

    def execute_move(self, moving_from, moving_to):
        """(Blindly) moves the piece at the first position to the second position."""
        piece_moving = self.get_square_occupant(moving_from)
        self.set_square_occupant(moving_from, "NONE")
        self.set_square_occupant(moving_to, piece_moving)

    def path_is_clear(self, moving_from, moving_to):
        move_path = utils.build_square_string_range(moving_from, moving_to)
        return False not in {self.get_square_occupant(x) == "NONE" for x in move_path[1:]}

    def is_move_legal(self, moving_from, moving_to):
        """Checks if move from first square to second is legal. Returns True if so, False if not."""
        return self.get_game_state() == "UNFINISHED"\
            and moving_from in self.get_game_board().get_all_squares()\
            and moving_to in self.get_game_board().get_all_squares()\
            and self.get_square_occupant(moving_from) == self.get_active_player()\
            and utils.move_is_straight(moving_from, moving_to)\
            and moving_from != moving_to\
            and self.path_is_clear(moving_from, moving_to)

    def find_captured_squares(self, from_square, to_square):
        """
        Return list of captured squares between from_ and to_square (exclusive), or False if from_ and to_ do not
        form a valid capture.
        """
        capturing_color = self.get_square_occupant(from_square)
        range_to_check = utils.build_square_string_range(from_square, to_square)[1:]
        square_value_list = [self.get_square_occupant(x) for x in range_to_check]

        end_cap = square_value_list.index(capturing_color) if capturing_color in square_value_list else -1
        first_empty = square_value_list.index("NONE") if "NONE" in square_value_list else -1

        return False if end_cap <= 0 or 0 <= first_empty < end_cap else range_to_check[:end_cap]

    def check_linear_captures(self, moved_to):
        """Searches four directions around latest move, captures pieces, and updates capture counts."""
        if type(moved_to) != str and len(moved_to) != 2:
            raise ValueError(f"check_linear_captures needs a 2-character square string. moved_to = {moved_to}")

        # # Determine 4 limits to the edges of the board.
        # row, col = moved_to
        # search_limits = [f"{row}1", f"{row}9", f"a{col}", f"i{col}"]
        #
        # # Check each direction for captures up to the edges of the board.
        # captured_lists = [self.find_captured_squares(moved_to, limit) for limit in search_limits]
        # captured_squares = [square for sublist in captured_lists if sublist for square in sublist]
        # return captured_squares

        # pot_cap_clusters = [cluster for cluster in self.clusters[self._inactive_player] if cluster.get_other_border(
        #     moved_to)]
        # captured_clusters = [cluster for cluster in pot_cap_clusters if self.get_square_occupant(
        #     cluster.get_other_border(moved_to)) == self._active_player]
        # capture_squares = []
        # for cluster in captured_clusters:
        #     capture_squares += list(cluster.squares)
        #     self.clusters[self._inactive_player].remove(cluster)

        capture_list = list(self.clusters.captured_squares)
        self.clusters.clear_captures()
        return capture_list

    def check_corner_capture(self, moved_to):
        """Checks for a capture in the corner. Removes enemy piece in corner. Must occur after linear check for
        correct prev move data update."""
        capture_scenarios = {
            # Key is the captured piece, lists are capturing positions.
            "a1": ["a2", "b1"],
            "a9": ["a8", "b9"],
            "i1": ["h1", "i2"],
            "i9": ["h9", "i8"]
        }

        closest_corner = GameBoard.find_closest_corner(moved_to)
        capturing_squares = capture_scenarios.get(closest_corner, [])
        if moved_to not in capturing_squares:
            return []

        moved_to_index = capturing_squares.index(moved_to)
        capture_partner = capturing_squares[moved_to_index - 1]

        corner_captured = self.get_square_occupant(capture_partner) == self._active_player and \
            self.get_square_occupant(closest_corner) == self._inactive_player

        return [closest_corner] if corner_captured else []

    def handle_captured_pieces(self, captured_squares):
        """
        Captures the given list of squares, updating score and board state.
        """
        if not captured_squares:
            return None

        self.add_num_captured_pieces(self._inactive_player, len(captured_squares))

        self.set_square_occupants(captured_squares, "NONE")

        # Update data for latest move log entry
        self.move_log[-1].cap_squares.extend(captured_squares)
        self.move_log[-1].cap_color = self._inactive_player

        return None

    def check_win(self):
        """Checks if the number of captured pieces of either color is 8 or 9."""
        if self.get_num_captured_pieces("RED") > 7:
            self.set_game_state("BLACK_WON")
        elif self.get_num_captured_pieces("BLACK") > 7:
            self.set_game_state("RED_WON")

    def make_move(self, moving_from, moving_to):
        """Moves from first square to second and returns True if legal, then updates game variables accordingly."""

        # Check if move is legal and execute
        if not self.is_move_legal(moving_from, moving_to):
            return False
        self.clusters.clear_captures()
        self.execute_move(moving_from, moving_to)

        # Add to move log
        self.move_log.append(ShogiMove())
        self.move_log[-1].move = moving_from + moving_to
        self.move_log[-1].player = self._active_player

        # Check and execute captures
        linear_caps = self.check_linear_captures(moving_to)
        corner_caps = self.check_corner_capture(moving_to)
        self.handle_captured_pieces(linear_caps + corner_caps)

        self.check_win()
        self.toggle_active_player()
        return True

    def undo_move(self):
        """Undoes the last move. References last move in self.move_log. Force executes last move in reverse, returns
        any captured pieces, toggles active player, and resets prev move to None. Can only undo up to one move."""
        if not self.move_log:
            return None

        prev_move = self.move_log.pop()
        self._game_state = "UNFINISHED"  # Safe to assume game state was unfinished if move was made
        self.toggle_active_player()  # Assume undo occurs after player switch
        self.execute_move(prev_move.move[2:], prev_move.move[:2])
        self.set_square_occupants(prev_move.cap_squares, prev_move.cap_color)
        prev_move.cap_color and self.add_num_captured_pieces(prev_move.cap_color, -len(prev_move.cap_squares))

        return None

    def return_valid_moves(self, square_string: str) -> set[str]:
        """Returns all valid moves for the given square. O(1)"""
        if self.get_square_occupant(square_string) != self.get_active_player():
            raise Exception("Given square string is not active player.")

        return {f"{square_string}{dest}" for dest in self.get_game_board().get_reachable_squares(square_string)}


if __name__ == '__main__':
    g = HasamiShogiGame()
    g.make_move("i5", "e5")
    g.make_move("a5", "d5")
    g.make_move("i4", "e4")
    g.undo_move()
    g.undo_move()
    g.undo_move()
    g.get_game_board().print_board()
    pass
