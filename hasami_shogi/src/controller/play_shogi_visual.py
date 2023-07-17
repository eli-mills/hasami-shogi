from hasami_shogi.src.view.visual_game import VisualGame


def main(num_players=1, player_color="BLACK"):
    vis_game = VisualGame(num_players, 3, player_color)
    vis_game.game_loop_visual()


if __name__ == "__main__":
    main()
