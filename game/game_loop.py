from game.models import Deck, Player, Enemy
from game.combat import CombatEngine
from db.database import (
    get_run, get_deck_for_run,
    get_enemy_for_floor, get_reward_cards,
    save_run_after_combat, end_run
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
    """
        Run a full fight between player and enemy.
        Returns True if the player won, False if defeated.
    """
    combat = CombatEngine(player, enemy)
    combat.start_combat()

    while not combat.is_over:
        print(f"\n{'─' * 40}")
        print(f"{player} | {enemy}")
        print(f"Energy: {player.energy} | Intent: {enemy.get_intent()['desc']}")
        print(f"Hand: {[c.name for c in player.deck.hand]}")
        print("─" * 40)

        action = input("Play card (name) or 'end' to end turn: ").strip().lower()

        if action == "end":
            combat.end_turn()
            continue

        card = next((c for c in player.deck.hand
                     if c.name.lower() == action), None)

        if card is None:
            print(f"Card '{action}' not found in hand.")
            continue

        try:
            combat.play_card(card)
        except ValueError as e:
            print(f"Cannot play card: {e}")

    return combat.player_won


def offer_reward(run_id: int, player: Player, current_floor: int):
    """
        Show 3 random playable cards and let the player pick one.
        Player can skip by entering 0.
        Saves progress to the database.
    """
    rewards = get_reward_cards(3)

    print("\nChoose a card to add to your deck:")
    for i, card in enumerate(rewards, 1):
        print(f"  {i}. {card}")
    print("  0. Skip")

    while True:
        try:
            choice = int(input("Your choice: "))
            if choice == 0:
                chosen_id = None
                break
            if 1 <= choice <= len(rewards):
                chosen_id = rewards[choice - 1].id
                print(f"Added {rewards[choice - 1].name} to your deck.")
                break
            print(f"Enter a number between 0 and {len(rewards)}.")
        except ValueError:
            print("Enter a valid number.")

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
        print(f"\n{'═' * 40}")
        print(f"Floor {current_floor}")
        print(f"═" * 40)

        enemy = get_enemy_for_floor(current_floor)
        print(f"An enemy appears: {enemy.name} (hp={enemy.hp})")

        won = run_combat(player, enemy)

        if not won:
            print(f"\nYou were defeated on floor {current_floor}.")
            end_run(run_id, "defeat")
            return

        print(f"\nYou defeated {enemy.name}!")
        offer_reward(run_id, player, current_floor)
        current_floor += 1

        if current_floor > MAX_FLOORS:
            print("\nYou cleared all floors — Victory!")
            end_run(run_id, "victory")
            return

        player, current_floor = build_player(run_id)