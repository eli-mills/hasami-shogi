from hasami_shogi.src.controller.hasami_shogi_game import HasamiShogiGame
from hasami_shogi.src.controller.ai_player import AIPlayer
from hasami_shogi.src.controller.player import Player


def terminal_ai():
    new_game = HasamiShogiGame()
    player_black = AIPlayer(new_game, "BLACK")
    player_red = Player(new_game, "RED")
    player_red.set_opposing_player(player_black)
    while new_game.get_game_state() == "UNFINISHED":
        print(new_game.get_active_player(), "'s turn.")
        print("BLACK's pieces:", player_black.get_pieces())
        print("RED's, pieces:", player_red.get_pieces())
        new_game.get_game_board().print_board()
        if new_game.get_active_player() == "BLACK":
            print("AI is thinking.")
            ai_move = player_black.minimax(3)[0]
            player_black.make_move(ai_move[:2], ai_move[2:])
        else:
            player_move = input("Enter a 4-char move.\n")
            player_red.make_move(player_move[:2], player_move[2:])


def main():
    """Plays a game of Hasami Shogi in terminal."""
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
        if player_move == 'undo':
            new_game.undo_move()
        else:
            turn_success = new_game.make_move(player_move[:2], player_move[2:])
    print(new_game.get_game_state())


if __name__ == '__main__':
    main()

