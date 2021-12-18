import pygame

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
row_headings = [game_font.render(x, False, heading_color) for x in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']]
col_headings = [game_font.render(x, False, heading_color) for x in ['1', '2', '3', '4', '5', '6', '7', '8', '9']]