from HasamiShogiGame import HasamiShogiGame
import pygame, sys

pygame.font.init()

screen_size = 900
board_size = 720
square_size = board_size // 9
board_margin = (screen_size - board_size) // 2

black = 0, 0, 0
white = 255, 255, 255
grey = 100, 100, 100
dark_brown = 40, 25, 10
tan = 200, 175, 150

screen_color = tan
border_color = dark_brown
heading_color = dark_brown

board_rect = board_margin, board_margin, board_size, board_size
square_rect = board_margin, board_margin, square_size, square_size
board_bg = pygame.image.load("wood.jpeg")

screen = pygame.display.set_mode((screen_size, screen_size))
pygame.display.set_caption("Hasami Shogi")

rows = 9
cols = 9

game_font = pygame.font.SysFont("Arial", 32)
row_headings = [game_font.render(x, False, heading_color) for x in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']]
col_headings = [game_font.render(x, False, heading_color) for x in ['1', '2', '3', '4', '5', '6', '7', '8', '9']]


def draw_headings():
    """Renders the game headings."""
    for i, col_heading in enumerate(col_headings):
        screen.blit(col_heading, (board_margin + i*square_size + square_size//3, board_margin//2))

    for i, row_heading in enumerate(row_headings):
        screen.blit(row_heading, (board_margin//2,board_margin + i*square_size + square_size//3))


def draw_squares():
    """Draws all squares for the board."""
    for row in range(rows):
        for col in range(cols):
            pygame.draw.rect(screen, border_color, (board_margin + col*square_size, board_margin + row*square_size, square_size, square_size), 1)


while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
    screen.fill(screen_color)
    screen.blit(board_bg, board_rect, (0, 0, board_size, board_size))
    draw_headings()
    draw_squares()
    pygame.display.flip()


def play_game():
    new_game = HasamiShogiGame()
    turn_success = ""
    while new_game.get_game_state() == "UNFINISHED":
        new_game.get_game_board().print_board()
        print('*' * 19 + '\n')
        if turn_success == False:
            print("Move not allowed, repeat turn.")
        if turn_success == True:
            print("Move succeeded.")
        print(new_game.get_active_player() + "'s Move")
        print("Captured Pieces | BLACK:", new_game.get_num_captured_pieces("BLACK"), " RED:",
              new_game.get_num_captured_pieces("RED"))
        print('\n')
        player_move = input("Enter move: ")[:4]
        print('\n' * 100)
        turn_success = new_game.make_move(player_move[:2], player_move[2:])
    print(new_game.get_game_state())


def main():
    play_game()


# if __name__ == "__main__":
#     main()
