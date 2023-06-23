from hasami_shogi import play_shogi_visual as visual
from hasami_shogi import play_shogi_terminal as terminal
import time

USER_PROMPT = "Type a number and press enter: "


def main():
    # Instructions
    print("Welcome to Hasami Shogi, a project by Eli Mills.")
    print("To get started, select a game mode.")
    print()
    time.sleep(1)

    # Get user input
    while True:
        print("Please select from the following options:")
        print("[1] Play in the terminal console.")
        print("[2] Play with a visual game board.")
        print("Enter 'exit' to exit.")
        if (user_input := input(USER_PROMPT)) in ["1", "2"]:
            break
        elif user_input == "exit":
            break
        print("Invalid input. Please try again.")
        print()

    if user_input == "1":
        terminal.main()
    elif user_input == "2":
        visual.main()


if __name__ == "__main__":
    main()
