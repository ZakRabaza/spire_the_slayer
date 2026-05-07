from game.models import Card, Deck, Player, Enemy
from game.combat import CombatEngine
from game.colors import Color
from game.display import (
    display_hand, display_enemy, display_player, display_floor, display_separator, display_ongoing_runs, display_rewards,
    display_draw_pile, display_discard_pile
)
from db.database import (
    get_run, get_deck_for_run,get_enemy_for_floor, get_reward_cards, save_run_after_combat, end_run, get_ongoing_runs
)


MAX_FLOORS = 10

def build_player(run_id: int) -> tuple[Player, int]:
    """
        Load a run from the database and reconstruct the Player object.
        Returns the player and the current floor number.
    """
    run = get_run(run_id)
    cards = get_deck_for_run(run_id)
    deck = Deck(cards)
    player = Player(
        name=run['player_name'],
        hp=run['current_hp'],
        max_hp=run['max_hp'],
        deck=deck
    )
    return player, run['current_floor']

def run_combat(player: Player, enemy: Enemy) -> bool:
    combat = CombatEngine(player, enemy)
    combat.start_combat()

    while not combat.is_over:
        print(f"\n")
        display_separator()
        display_player(player)
        display_enemy(enemy)
        display_separator()

        display_hand(player.deck.hand)

        print(f"\n  {Color.blue('0.')} End turn")
        print(f"  {Color.blue('d.')} View draw pile "
              f"{Color.blue(str(len(player.deck.draw_pile)))} cards")
        print(f"  {Color.blue('x.')} View discard pile "
              f"{Color.blue(str(len(player.deck.discard_pile)))} cards")

        action = input(f"\n{Color.bold('Your choice: ')}").strip()

        if action == "0":
            combat.end_turn()
            continue

        if action == "d":
            display_draw_pile(player.deck.draw_pile)
            input(f"\n{Color.bold(Color.blue('Press Enter to continue...'))}")
            continue

        if action == "x":
            display_discard_pile(player.deck.discard_pile)
            input(f"\n{Color.bold(Color.blue('Press Enter to continue...'))}")
            continue

        if not action.isdigit():
            print(Color.red("Enter a number."))
            continue

        index = int(action) - 1

        if index < 0 or index >= len(player.deck.hand):
            print(Color.red(f"Enter a number between 1 and {len(player.deck.hand)}."))
            continue

        card = player.deck.hand[index]

        try:
            combat.play_card(card)
        except ValueError as e:
            print(Color.red(f"Cannot play card: {e}"))

    return combat.player_won

def offer_reward(run_id: int, player: Player, current_floor: int):
    """
        Show 3 random playable cards and let the player pick one.
        Player can skip by entering 0.
        Saves progress to the database.
    """
    rewards = get_reward_cards(3)

    display_rewards(rewards)

    while True:
        try:
            choice = int(input(f"\n{Color.bold('Your choice: ')}"))
            if choice == 0:
                chosen_id = None
                break
            if 1 <= choice <= len(rewards):
                chosen_id = rewards[choice - 1].id
                print(Color.green(f"Added {rewards[choice - 1].name} to your deck."))
                break
            print(Color.red(f"Enter a number between 0 and {len(rewards)}."))
        except ValueError:
            print(Color.red("Enter a valid number."))

    save_run_after_combat(
        run_id=run_id,
        current_hp=player.hp,
        current_floor=current_floor + 1,
        reward_card_id=chosen_id
    )

def game_loop(run_id: int):
    """
        Main game loop — fight enemies floor by floor until the player wins or is defeated.
    """
    player, current_floor = build_player(run_id)

    print(f"\nWelcome, {player.name}!")
    print(f"Starting on floor {current_floor}.")

    while current_floor <= MAX_FLOORS:
        display_floor(current_floor)

        enemy = get_enemy_for_floor(current_floor)
        print(f"An enemy appears: {enemy.name} (hp={enemy.hp})")

        won = run_combat(player, enemy)

        if not won:
            print(Color.red(f"\nYou were defeated on floor {current_floor}."))
            end_run(run_id, "defeat")
            return

        print(f"\nYou defeated {enemy.name}!")
        offer_reward(run_id, player, current_floor)
        current_floor += 1

        if current_floor > MAX_FLOORS:
            print(Color.green("\nYou cleared all floors — Victory!"))
            end_run(run_id, "victory")
            return

        player, current_floor = build_player(run_id)

def select_run() -> int | None:
    """
        Check for ongoing runs and let the player resume one.
        Returns a run_id if the player chose to resume, or None if they want to start a new run.
    """
    ongoing_runs = get_ongoing_runs()

    if not ongoing_runs:
        return None

    display_ongoing_runs(ongoing_runs)

    while True:
        try:
            choice = int(input("\nYour choice: "))
            if choice == 0:
                return None
            if any(r['id'] == choice for r in ongoing_runs):
                return choice
            print(Color.red("Enter a valid run id."))
        except ValueError:
            print(Color.red("Enter a valid number."))

