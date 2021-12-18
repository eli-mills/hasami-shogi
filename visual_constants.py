import pygame
from hasami_shogi_utilities import row_labels, col_labels
pygame.font.init()

# SIZES
rows = cols = 9
screen_size = 900
board_size = 720
square_size = board_size // rows
board_margin = (screen_size - board_size) // 2
screen = pygame.display.set_mode((screen_size, screen_size))

# COLORS
black = 0, 0, 0
white = 255, 255, 255
grey = 100, 100, 100
dark_brown = 40, 25, 10
tan = 200, 175, 150
green = 100, 255, 0
red = 255, 0, 0

# BOARD APPEARANCE SETTINGS
screen_color = tan
border_color = dark_brown
heading_color = dark_brown
board_rect = board_margin, board_margin, board_size, board_size
square_rect = board_margin, board_margin, square_size, square_size
board_bg = pygame.image.load("assets/wood.jpeg")
game_font = pygame.font.SysFont("Arial", 32)

# HEADINGS AND TITLES
pygame.display.set_caption("Hasami Shogi")
row_headings = [game_font.render(x, False, heading_color) for x in row_labels]
col_headings = [game_font.render(x, False, heading_color) for x in col_labels]