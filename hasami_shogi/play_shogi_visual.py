from hasami_shogi.src.view.visual_game import VisualGame


def main():
    vis_game = VisualGame(1, 3, "BLACK")
    vis_game.game_loop_visual()


if __name__ == "__main__":
    main()