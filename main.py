from db.database import create_run
from game.game_loop import game_loop, select_run
from game.display import display_tile
from game.colors import Color


def main():
    display_tile()
    run_id = select_run()

    if run_id is not None:
        print(Color.bold(f"\nResuming run {run_id}..."))
        game_loop(run_id)
        return

    # new run
    name = input("\nEnter your name: ").strip()[:20]
    if not name:
        name = "Player"

    run_id = create_run(name)
    print(f"Run created — good luck, {name}!")
    game_loop(run_id)


if __name__ == "__main__":
    main()