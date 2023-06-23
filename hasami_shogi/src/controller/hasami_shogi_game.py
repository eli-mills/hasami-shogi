from hasami_shogi.src.controller.game_board import GameBoard


class ShogiMove:
    """Defines data structure for recording a move in Hasami Shogi."""

    def __init__(self):
        self.player = self.move = self.cap_squares = self.cap_color = None


class HasamiShogiGame:
    """Defines the methods for a game of Hasami Shogi."""

    def __init__(self, starting_game=None):
        """Creates a new board, sets game state to UNFINISHED,
        active player to BLACK, captured pieces to 0."""
        if starting_game is None:
            self._game_board = GameBoard()
            self._game_state = "UNFINISHED"  # UNFINISHED, RED_WON, BLACK_WON
            self._active_player = "BLACK"  # BLACK, RED
            self._inactive_player = "RED"  # BLACK, RED
            self._captured_pieces = {"RED": 0, "BLACK": 0}
            self.move_log = []
        else:
            self._game_board = GameBoard(starting_game._game_board)
            self._game_state = starting_game._game_state
            self._active_player = starting_game._active_player
            self._inactive_player = starting_game._inactive_player
            self._captured_pieces = dict(starting_game._captured_pieces)
            self.move_log = []
        self._all_squares = self._game_board.get_all_squares()

    def get_game_board(self):
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

    def sub_num_captured_pieces(self, player_color, num_captured):
        """Subtracts the given number from the captured pieces of the given color."""
        self._captured_pieces[player_color] -= num_captured

    def get_square_occupant(self, square_string):
        """Returns the value at the given square on the board: RED, BLACK, or NONE."""
        return self.get_game_board().get_square(square_string)

    def set_square_occupant(self, square_string, value):
        """Sets the occupant at the given square to the given value."""
        self.get_game_board().set_square(square_string, value)

    def execute_move(self, moving_from, moving_to):
        """(Blindly) moves the piece at the first position to the second position."""
        piece_moving = self.get_square_occupant(moving_from)
        self.set_square_occupant(moving_to, piece_moving)
        self.set_square_occupant(moving_from, "NONE")

    def is_move_legal(self, moving_from, moving_to):
        """Checks if move from first square to second is legal. Returns True if so, False if not."""
        if self.get_game_state() != "UNFINISHED":  # Game is finished
            return False

        if moving_from not in self._all_squares or moving_to not in self._all_squares:  # Out of range
            return False

        if self.get_square_occupant(
                moving_from) != self.get_active_player():  # Wrong color
            return False

        if moving_from[0] != moving_to[0] and moving_from[1] != moving_to[
            1]:  # Not pure vertical or horizontal
            return False

        if moving_from == moving_to:  # Same square
            return False

        move_path = self.get_game_board().build_square_string_range(moving_from,
                                                                    moving_to)
        return False not in {self.get_square_occupant(x) == "NONE" for x in
                             move_path[1:]}  # Check for clear path.

    def find_captured_squares(self, from_square, to_square):
        """Finds capture pattern in given square string range. Returns captured squares if found, else False."""
        capturing_color = self.get_square_occupant(from_square)
        captured_color = {"RED": "BLACK", "BLACK": "RED"}[
            capturing_color]  # Picks opposite color.
        square_string_list = self.get_game_board().build_square_string_range(
            from_square, to_square)  # Square strings
        square_value_list = [self.get_square_occupant(x) for x in
                             square_string_list]  # Values on board
        for index, square_value in enumerate(square_value_list[1:]):
            if square_value == capturing_color:
                if index == 0:  # Two of capturing color in a row, no capture.
                    return False
                end_cap = square_string_list[1:][
                    index]  # Store the other "bread" of the "sandwich".
                return self.get_game_board().build_square_string_range(
                    from_square, end_cap)[1:-1]  # Captured only.
            if square_value != captured_color:  # Breaks on NONE.
                return False

    def check_linear_captures(self, moved_to):
        """Searches four directions around latest move, captures pieces, and updates capture counts."""

        # 1. Determine 4 limits to the edges of the board.
        left_limit = moved_to[0] + '1'
        right_limit = moved_to[0] + '9'
        top_limit = 'a' + moved_to[1]
        bottom_limit = 'i' + moved_to[1]
        search_directions = [left_limit, right_limit, top_limit, bottom_limit]

        # 2. Check each direction for captures up to the edges of the board.
        captured_lists = [self.find_captured_squares(moved_to, limit) for limit
                          in search_directions]
        captured_squares = [square for sublist in captured_lists if sublist for
                            square in sublist]

        # 3. Add captured pieces to the score.
        self.add_num_captured_pieces(self._inactive_player,
                                     len(captured_squares))

        # 4. Change all captured squares to "NONE".
        for captured in captured_squares:
            self.set_square_occupant(captured, "NONE")

        # 5. Update prev move data
        if captured_squares != []:
            if self.move_log[-1].cap_squares is None:
                self.move_log[-1].cap_squares = captured_squares
            else:
                self.move_log[-1].cap_squares.extend(captured_squares)
            self.move_log[-1].cap_color = self._inactive_player

    def find_closest_corner(self, moved_to):
        """Finds the closest corner to the new square to check for corner capture."""
        closest_corner = ""
        square_row, square_column = self.get_game_board().string_to_index(
            moved_to)
        if square_row <= 1:
            closest_corner += "a"
        if square_row >= 7:
            closest_corner += "i"
        if square_column <= 1:
            closest_corner += "1"
        if square_column >= 7:
            closest_corner += "9"
        return closest_corner

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

        closest_corner = self.find_closest_corner(moved_to)

        if closest_corner in capture_scenarios:
            if moved_to in capture_scenarios[closest_corner]:

                # Determine what colors are at the three corner positions:
                moved_to_index = capture_scenarios[closest_corner].index(
                    moved_to)
                capturing_end = capture_scenarios[closest_corner][
                    moved_to_index - 1]
                moved_to_color = self.get_square_occupant(moved_to)
                captured_color = self.get_square_occupant(closest_corner)
                capturing_end_color = self.get_square_occupant(capturing_end)

                # Check for correct pattern:
                if moved_to_color == capturing_end_color and captured_color == self._inactive_player:
                    self.set_square_occupant(closest_corner, "NONE")
                    self.add_num_captured_pieces(self._inactive_player, 1)
                    if self.move_log[-1].cap_squares is None:
                        self.move_log[-1].cap_squares = [closest_corner]
                    else:
                        self.move_log[-1].cap_squares.append(closest_corner)
                    self.move_log[-1].cap_color = self._inactive_player

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
        self.execute_move(moving_from, moving_to)

        # Add to move log
        self.move_log.append(ShogiMove())
        self.move_log[-1].move = moving_from + moving_to
        self.move_log[-1].player = self._active_player

        # Check and execute captures
        self.check_linear_captures(moving_to)
        self.check_corner_capture(moving_to)

        self.check_win()
        self.toggle_active_player()
        return True

    def undo_move(self):
        """Undoes the last move. References last move in self.move_log. Force executes last move in reverse, returns
        any captured pieces, toggles active player, and resets prev move to None. Can only undo up to one move.

        Returns the last move, and opponent pieces to restore if any."""
        if not self.move_log:
            return

        prev_move = self.move_log.pop()
        self._game_state = "UNFINISHED"  # Safe to assume game state was unfinished if move was made
        self.execute_move(prev_move.move[2:], prev_move.move[:2])
        if prev_move.cap_squares is not None:
            for square in prev_move.cap_squares:
                self.set_square_occupant(square, prev_move.cap_color)
            self.sub_num_captured_pieces(prev_move.cap_color,
                                         len(prev_move.cap_squares))
        self.toggle_active_player()  # Assume undo occurs after player switch

        return prev_move.move, prev_move.cap_squares


def main():
    new_game = HasamiShogiGame()
    new_game.make_move('i5', 'e5')
    new_game.undo_move()
    pass


if __name__ == '__main__':
    # cProfile.run('main()', sort='cumtime')
    main()