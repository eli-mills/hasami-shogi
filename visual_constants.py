import pygame
from hasami_shogi_utilities import row_labels, col_labels
pygame.font.init()

# SIZES
rows = cols = 9
screen_size = 800
board_size = 630
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
red = 175, 0, 0

# BOARD APPEARANCE SETTINGS
screen_color = tan
border_color = dark_brown
heading_color = dark_brown
board_rect = board_margin, board_margin, board_size, board_size
square_rect = board_margin, board_margin, square_size, square_size
board_bg = pygame.image.load("assets/wood.jpeg")
label_font = pygame.font.SysFont("Arial", 24)
stat_font = pygame.font.SysFont("Arial", 18)
victory_font = pygame.font.SysFont("Arial", 68)

# HEADINGS AND TITLES
pygame.display.set_caption("Hasami Shogi")
row_headings = [label_font.render(x, False, heading_color) for x in row_labels]
col_headings = [label_font.render(x, False, heading_color) for x in col_labels]
stat_height_1 = board_margin + board_size + board_margin//4
stat_height_2 = board_margin + board_size + board_margin//2
stat_height_3 = board_margin + board_size + 3*board_margin//4
capture_align_1 = board_margin + board_size//8
capture_align_2 = board_margin + board_size//2
player_align = board_margin + 3*board_size//4
