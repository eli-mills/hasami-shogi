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

    def render_board(self):
        """Draws a blank board."""
        self.draw_screen()
        self.draw_headings()
        self.draw_squares()

    def check_in_board_bounds(self, gcoord):
        """Returns True if given coordinate is within the game board bounds."""
        x, y = gcoord
        return board_margin < x < board_margin + board_size and board_margin < y < board_margin + board_size

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
            self._selected_square = text_pos
        elif self._selected_square == text_pos:
            self._selected_square = None        # Reset selection
        else:
            self._game.make_move(self._selected_square, text_pos)
            # self._game.get_game_board().print_board()
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
            self.render_selection()
            pygame.display.flip()



def main():
    vis_game = VisualGame()
    vis_game.game_loop_visual()


if __name__ == "__main__":
    main()
