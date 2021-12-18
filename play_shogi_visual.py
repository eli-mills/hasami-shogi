from HasamiShogiGame import HasamiShogiGame
from visual_constants import *
import pygame
import sys


class VisualGame():
    """Contains methods and data members used to visually render a game of Hasami Shogi."""
    def __init__(self):
        """Initialize an instance of a visual Hasami Shogi game."""
        self._selected_square = None
        self._game = HasamiShogiGame()

    def draw_screen(self):
        """Renders the background screen for the game."""
        screen.fill(screen_color)
        screen.blit(board_bg, board_rect, (0, 0, board_size, board_size))

    def draw_headings(self):
        """Renders the game headings."""
        for i, col_heading in enumerate(col_headings):
            screen.blit(col_heading, (board_margin + i*square_size + square_size//3, board_margin//2))

        for i, row_heading in enumerate(row_headings):
            screen.blit(row_heading, (board_margin//2,board_margin + i*square_size + square_size//3))

    def draw_squares(self):
        """Draws all squares for the board."""
        for row in range(rows):
            for col in range(cols):
                pygame.draw.rect(screen,
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
                    pygame.draw.circle(screen, red, center, 25)
                elif square_color == "BLACK":
                    pygame.draw.circle(screen, black, center, 25)

    def draw_game_stats(self):
        """Creates and positions the game stats, including pieces captured, player turn, and game status."""
        capture_caption = stat_font.render("Pieces Captured:", False, heading_color)
        player_caption = stat_font.render("Current Player:", False, heading_color)
        red_text = stat_font.render("RED", False, red)
        black_text = stat_font.render("BLACK", False, black)
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
                screen.blit(victory_font.render("RED WON!", False, red, grey), victory_coords)
            else:
                width, height = victory_font.size("BLACK WON!")
                victory_coords = screen_size // 2 - width // 2, screen_size // 2 - height // 2
                screen.blit(victory_font.render("BLACK WON!", False, black, grey), victory_coords)

        screen.blit(capture_caption, (capture_align_1, stat_height_1))
        screen.blit(player_caption, (player_align, stat_height_1))
        screen.blit(red_text, (capture_align_1, stat_height_2))
        screen.blit(black_text, (capture_align_1, stat_height_3))
        screen.blit(red_caps, (capture_align_2, stat_height_2))
        screen.blit(black_caps, (capture_align_2, stat_height_3))
        screen.blit(current_player, (player_align, stat_height_2))

    def render_selection(self):
        """Generates a green outline around the selected square."""
        if self._selected_square:
            x, y = self.square_string_to_gcoord(self._selected_square)
            selection_rect = (
                    ((x - board_margin) // square_size) * square_size + board_margin,
                    ((y - board_margin) // square_size) * square_size + board_margin,
                    square_size,
                    square_size)
            pygame.draw.rect(screen, green, selection_rect, 2)

    def render_board(self):
        """Draws a blank board."""
        self.draw_screen()
        self.draw_headings()
        self.draw_squares()
        self.draw_pieces()
        self.draw_game_stats()
        self.render_selection()

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
        y = board_margin + row_labels.index(row)*square_size
        x = board_margin + col_labels.index(col)*square_size
        return x, y

    def click_handler(self, gcoord):
        """Defines steps to take when the player clicks a square with the given game coordinates."""
        if not self.check_in_board_bounds(gcoord):
            return
        text_pos = self.gcoord_to_square_string(gcoord)
        if not self._selected_square:
            if self._game.get_square_occupant(text_pos) != self._game.get_active_player():
                return
            self._selected_square = text_pos
        elif self._selected_square == text_pos:
            self._selected_square = None        # Reset selection
        else:
            self._game.make_move(self._selected_square, text_pos)
            self._selected_square = None

    def event_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.click_handler(event.pos)  # Return value to be used for tracking previous click.

    def game_loop_visual(self):
        """Plays a game of Hasami Shogi rendered visually with PyGame."""
        new_game = HasamiShogiGame()
        click = None
        while 1:
            self.render_board()
            self.event_handler()
            pygame.display.flip()



def main():
    vis_game = VisualGame()
    vis_game.game_loop_visual()


if __name__ == "__main__":
    main()
