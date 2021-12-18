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
                                 border_color,
                                 (board_margin + col*square_size, board_margin + row*square_size, square_size, square_size),
                                 1)

    def render_board(self):
        """Draws a blank board."""
        self.draw_screen()
        self.draw_headings()
        self.draw_squares()

    def game_loop_visual(self):
        """Plays a game of Hasami Shogi rendered visually with PyGame."""
        new_game = HasamiShogiGame()
        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
            self.render_board()
            pygame.display.flip()


def main():
    vis_game = VisualGame()
    vis_game.game_loop_visual()


if __name__ == "__main__":
    main()
