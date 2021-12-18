from HasamiShogiGame import HasamiShogiGame
from visual_constants import *
import pygame
import sys


class VisualGame():
    """Contains methods and data members used to visually render a game of Hasami Shogi."""
    def __init__(self):
        """Initialize an instance of a visual Hasami Shogi game."""
        pass

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

    def render_selection(self, gcoord):
        """Generates a green outline around the selected square."""
        x, y = gcoord
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

    def game_loop_visual(self):
        """Plays a game of Hasami Shogi rendered visually with PyGame."""
        new_game = HasamiShogiGame()
        text_pos = ""
        click_pos = None
        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    click_pos = event.pos
            self.render_board()
            if click_pos:
                if self.check_in_board_bounds(click_pos):
                    text_pos = self.gcoord_to_square_string(click_pos)
                    self.render_selection(click_pos)
            text_pos_render = game_font.render(text_pos, False, heading_color)
            screen.blit(text_pos_render, (screen_size-50, screen_size//2))
            pygame.display.flip()


def main():
    vis_game = VisualGame()
    vis_game.game_loop_visual()


if __name__ == "__main__":
    main()
