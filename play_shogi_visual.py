from HasamiShogiGame import HasamiShogiGame
from visual_constants import *
from hasami_shogi_utilities import *
from ai import *
import ai
import pygame
import sys


class VisualGame():
    """Contains methods and data members used to visually render a game of Hasami Shogi."""
    def __init__(self, num_players, ai_depth=None, player_color=None):
        """Initialize an instance of a visual Hasami Shogi game."""
        self._selected_square = None
        self._prev_move = None
        self._curr_move = None
        self._game = HasamiShogiGame()
        self._player_red = Player(self._game, "RED")
        self._player_black = Player(self._game, "BLACK")
        self._ai = num_players < 2
        self._ai_depth = ai_depth
        self._zero_player = num_players == 0
        self._just_captured = set()
        self._just_captured_color = None

        if self._ai:
            if num_players == 0:
                self._player_red = AIPlayer(self._game, "RED")
                self._player_black = AIPlayer(self._game, "BLACK")
                self._ai_player = self._player_black
            elif player_color == "RED":
                self._player_black = AIPlayer(self._game, "BLACK")
                self._ai_player = self._player_black
            elif player_color == "BLACK":
                self._player_red = AIPlayer(self._game, "RED")
                self._ai_player = self._player_red

        self._player_red.set_opposing_player(self._player_black)
        self._screen = pygame.display.set_mode((screen_size, screen_size))

    def draw_screen(self):
        """Renders the background screen for the game."""
        self._screen.fill(screen_color)
        self._screen.blit(board_bg, board_rect, (0, 0, board_size, board_size))

    def draw_headings(self):
        """Renders the game headings."""
        for i, col_heading in enumerate(col_headings):
            self._screen.blit(col_heading, (board_margin + i*square_size + square_size//3, board_margin//2))

        for i, row_heading in enumerate(row_headings):
            self._screen.blit(row_heading, (board_margin//2,board_margin + i*square_size + square_size//3))

    def draw_squares(self):
        """Draws all squares for the board."""
        for row in range(rows):
            for col in range(cols):
                pygame.draw.rect(self._screen,
                                 border_color, (
                                     board_margin + col*square_size,
                                     board_margin + row*square_size,
                                     square_size,
                                     square_size
                                 ),
                                 1)

    def draw_pieces(self):
        """Loops through all board squares and draws the appropriate pieces."""
        for row in row_labels:
            for col in col_labels:
                square_string = row + col
                x, y = self.square_string_to_gcoord(square_string)
                center = x + square_size//2, y + square_size//2
                square_color = self._game.get_square_occupant(square_string)
                if square_color == "RED":
                    pygame.draw.circle(self._screen, red, center, piece_size)
                elif square_color == "BLACK":
                    pygame.draw.circle(self._screen, black, center, piece_size)

    def draw_game_stats(self):
        """Creates and positions the game stats, including pieces captured, player turn, and game status."""
        red_caps = stat_font.render(str(self._game.get_num_captured_pieces("RED")), False, red)
        black_caps = stat_font.render(str(self._game.get_num_captured_pieces("BLACK")), False, black)

        if self._game.get_active_player() == "RED":
            current_player = red_text
        else:
            current_player = black_text

        game_state = self._game.get_game_state()

        if game_state != "UNFINISHED":
            if game_state == "RED_WON":
                width, height = victory_font.size("RED WON!")
                victory_coords = screen_size//2 - width//2, screen_size//2 - height//2
                self._screen.blit(victory_font.render("RED WON!", False, red, grey), victory_coords)
            else:
                width, height = victory_font.size("BLACK WON!")
                victory_coords = screen_size // 2 - width // 2, screen_size // 2 - height // 2
                self._screen.blit(victory_font.render("BLACK WON!", False, black, grey), victory_coords)

        self._screen.blit(capture_caption, (capture_align_1, stat_height_1))
        self._screen.blit(player_caption, (player_align, stat_height_1))
        self._screen.blit(red_text, (capture_align_1, stat_height_2))
        self._screen.blit(black_text, (capture_align_1, stat_height_3))
        self._screen.blit(red_caps, (capture_align_2, stat_height_2))
        self._screen.blit(black_caps, (capture_align_2, stat_height_3))
        self._screen.blit(current_player, (player_align, stat_height_2))

    def draw_selection(self):
        """Generates a green outline around the selected square."""
        if self._selected_square:
            x, y = self.square_string_to_gcoord(self._selected_square)
            selection_rect = (
                ((x - board_margin) // square_size) * square_size + board_margin,
                ((y - board_margin) // square_size) * square_size + board_margin,
                square_size,
                square_size
            )
            pygame.draw.rect(self._screen, green, selection_rect, 2)

    def draw_piece_tracking(self):
        """Illustrates pieces that were just moved."""

        if self._prev_move:
            x, y = self.square_string_to_gcoord(self._prev_move)
            pygame.draw.circle(self._screen, grey, (x+square_size//2, y + square_size//2), piece_size)

        if self._curr_move:
            x, y = self.square_string_to_gcoord(self._curr_move)
            pygame.draw.circle(self._screen, green, (x+square_size//2, y+square_size//2), piece_size, 2)

    def draw_possible_moves(self):
        """Draws all possible moves for the selected square."""
        if self._selected_square:
            possible_moves = return_valid_moves(self._game, self._selected_square)
            for square in possible_moves:
                x, y = self.square_string_to_gcoord(square[2:])
                center = x + square_size//2, y + square_size//2
                pygame.draw.circle(self._screen, grey, center, dot_size)

    def draw_just_captured(self):
        """Draws colored x's where pieces were just captured."""
        for piece in self._just_captured:
            x, y = self.square_string_to_gcoord(piece)
            width, height = cap_font.size("X")
            coords = x + (square_size - width)//2, y + (square_size - height)//2
            cap_x = cap_font.render("X", False, self._just_captured_color)
            self._screen.blit(cap_x, coords)

    def render_board(self):
        """Draws a blank board."""
        self.draw_screen()
        self.draw_headings()
        self.draw_squares()
        self.draw_pieces()
        self.draw_just_captured()
        self.draw_selection()
        self.draw_piece_tracking()
        self.draw_possible_moves()
        self.draw_game_stats()

    def check_in_board_bounds(self, gcoord):
        """Returns True if given coordinate is within the game board bounds."""
        x, y = gcoord
        return board_margin < x < board_margin + board_size and board_margin < y < board_margin + board_size

    def gcoord_to_square_string(self, gcoord):
        """Converts the given game coordinates into the appropriate square string."""
        x, y = gcoord
        if self.check_in_board_bounds(gcoord):
            text_pos = row_labels[(y - board_margin) // square_size] + col_labels[(x - board_margin) // square_size]
            return text_pos

    def square_string_to_gcoord(self, square_string):
        """Converts the given square string into a game coordinate."""
        row, col = square_string[0], square_string[1]
        y = board_margin + row_labels.index(row) * square_size
        x = board_margin + col_labels.index(col) * square_size
        return x, y

    def swap_ai_player(self):
        """For a zero-player game, switches ai_player to the other player."""
        if self._ai_player == self._player_black:
            self._ai_player = self._player_red
        else:
            self._ai_player = self._player_black

    def click_handler(self, gcoord):
        """Defines steps to take when the player clicks a square with the given game coordinates."""
        if not self.check_in_board_bounds(gcoord):
            return
        square_string = self.gcoord_to_square_string(gcoord)
        if not self._selected_square:
            if self._game.get_square_occupant(square_string) != self._game.get_active_player():
                return
            self._selected_square = square_string
            self._just_captured = set()
        elif self._selected_square == square_string:
            self._selected_square = None        # Reset selection
        elif self._game.get_square_occupant(square_string) == self._game.get_square_occupant(self._selected_square):
            self._selected_square = square_string
        else:
            inactive_player = {"RED": "BLACK", "BLACK": "RED"}[self._game.get_active_player()]
            prev_game_pieces = get_game_pieces(self._game)[inactive_player]
            if self._player_black.get_active():
                success = self._player_black.make_move(self._selected_square, square_string)
            elif self._player_red.get_active():
                success = self._player_red.make_move(self._selected_square, square_string)
            if success:
                self._curr_move = square_string
                self._prev_move = self._selected_square
            new_pieces = get_game_pieces(self._game)[inactive_player]
            if prev_game_pieces != new_pieces:
                self._just_captured_color = inactive_player
                self._just_captured = prev_game_pieces - new_pieces
            self._selected_square = None

    def check_for_quit(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

    def event_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.click_handler(event.pos)  # Return value to be used for tracking previous click.

    def game_loop_visual(self):
        """Plays a game of Hasami Shogi rendered visually with PyGame."""

        if not self._ai:
            while 1:
                self.render_board()
                self.event_handler()
                pygame.display.flip()
        else:
            while 1:
                self.render_board()
                pygame.display.flip()
                if self._game.get_game_state() == "UNFINISHED":
                    if self._ai_player.get_active():
                        self.check_for_quit()
                        prev_pieces = set(self._ai_player.get_opposing_player().get_pieces())
                        next_move, heuristic = self._ai_player.minimax(self._ai_depth)
                        self._ai_player.make_move(next_move[:2], next_move[2:])
                        self._prev_move = next_move[:2]
                        self._curr_move = next_move[2:]
                        new_pieces = self._ai_player.get_opposing_player().get_pieces()
                        print(heuristic)
                        if new_pieces != prev_pieces:
                            self._just_captured_color = self._ai_player.get_opposing_color()
                            self._just_captured = prev_pieces - new_pieces
                        else:
                            self._just_captured = set()
                        if self._zero_player:
                            self.swap_ai_player()
                    else:
                        self.event_handler()
                else:
                    self.check_for_quit()


def main():
    vis_game = VisualGame(1, 3, "BLACK")
    vis_game.game_loop_visual()


if __name__ == "__main__":
    main()
