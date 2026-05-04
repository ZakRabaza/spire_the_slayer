from db.database import create_run
from game.game_loop import game_loop

def main():
    print("═" * 40)
    print("  Spire the Slayer")
    print("═" * 40)

    name = input("Enter your name: ").strip()
    if not name:
        name = "Player"

    run_id = create_run(name)
    print(f"Run created — good luck, {name}!")

    game_loop(run_id)

if __name__ == "__main__":
    main()