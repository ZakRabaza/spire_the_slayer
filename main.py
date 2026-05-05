from db.database import create_run, get_ongoing_runs
from game.game_loop import game_loop

def main():
    print("═" * 40)
    print("  Spire the Slayer")
    print("═" * 40)

    ongoing_runs = get_ongoing_runs()

    if ongoing_runs:
        print("\nOngoing runs:")
        for run in ongoing_runs:
            print(f"  {run['id']}. {run['player_name']} "
                  f"— Floor {run['current_floor']} "
                  f"— HP {run['current_hp']}/{run['max_hp']}")
        print("\n  0. Start a new run")

        while True:
            try:
                choice = int(input("\nYour choice: "))
                if choice == 0:
                    break
                if any(r['id'] == choice for r in ongoing_runs):
                    print(f"\nResuming run {choice}...")
                    game_loop(choice)
                    return
                print("Enter a valid run id.")
            except ValueError:
                print("Enter a valid number.")

    # new run
    name = input("\nEnter your name: ").strip()
    if not name:
        name = "Player"

    run_id = create_run(name)
    print(f"Run created — good luck, {name}!")
    game_loop(run_id)


if __name__ == "__main__":
    main()