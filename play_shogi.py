from HasamiShogiGame import HasamiShogiGame


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


if __name__ == "__main__":
    main()
