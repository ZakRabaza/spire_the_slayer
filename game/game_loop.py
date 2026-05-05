from game.models import Card, Deck, Player, Enemy
from game.combat import CombatEngine
from db.database import (
    get_run, get_deck_for_run,
    get_enemy_for_floor, get_reward_cards,
    save_run_after_combat, end_run
)

MAX_FLOORS = 10


class Color:
    RESET = "\033[0m"
    BOLD = "\033[1m"

    # text colors
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # bright variants
    BRED = "\033[91m"
    BGREEN = "\033[92m"
    BYELLOW = "\033[93m"
    BBLUE = "\033[94m"
    BCYAN = "\033[96m"

    @staticmethod
    def red(text):    return f"\033[31m{text}\033[0m"

    @staticmethod
    def green(text):  return f"\033[32m{text}\033[0m"

    @staticmethod
    def yellow(text): return f"\033[33m{text}\033[0m"

    @staticmethod
    def blue(text):   return f"\033[34m{text}\033[0m"

    @staticmethod
    def cyan(text):   return f"\033[36m{text}\033[0m"

    @staticmethod
    def bold(text):   return f"\033[1m{text}\033[0m"

    @staticmethod
    def hp_color(hp: int, max_hp: int) -> str:
        ratio = hp / max_hp
        if ratio > 0.5:
            return Color.green(f"{hp}/{max_hp}")
        elif ratio > 0.25:
            return Color.yellow(f"{hp}/{max_hp}")
        else:
            return Color.red(f"{hp}/{max_hp}")


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

def display_hand(hand: list[Card]):
    width = 22

    def card_lines(i: int, card: Card) -> list[str]:
        lines = []
        lines.append(f"  ┌{'─' * (width - 3)}[{Color.yellow(str(i))}]┐")
        lines.append(f"  │ {Color.bold(card.name):<{width + 7}}│")
        lines.append(f"  │ {Color.yellow(f'Cost: {card.cost}'):<{width + 7}}│")
        lines.append(f"  │ {card.description[:width - 1]:<{width - 1}}│")
        if card.damage > 0:
            lines.append(f"  │ {Color.red(f'Damage: {card.damage}'):<{width + 7}}│")
        else:
            lines.append(f"  │{' ' * width}  │")
        if card.block > 0:
            lines.append(f"  │ {Color.cyan(f'Block:  {card.block}'):<{width + 7}}│")
        else:
            lines.append(f"  │{' ' * width}  │")
        lines.append(f"  └{'─' * width}┘")
        return lines

    all_cards_lines = [card_lines(i, card) for i, card in enumerate(hand, 1)]

    print(f"\n{Color.bold('Your hand:')}")
    for row in zip(*all_cards_lines):
        print("".join(row))


def display_enemy(enemy: Enemy):
    intent = enemy.get_intent()
    width = 40

    print(f"\n  ┌{'─' * width}┐")
    print(f"  │ {Color.bold(enemy.name):<{width + 7}}│")
    print(f"  │ HP: {Color.hp_color(enemy.hp, enemy.max_hp):<{width + 8}}│")
    if enemy.block > 0:
        print(f"  │ {Color.cyan(f'Block: {enemy.block}'):<{width + 8}}│")
    else:
        print(f"  │{' ' * width}  │")

    if intent['type'] == 'attack':
        dmg = intent['value'] + enemy.strength
        print(f"  │ Intent: {Color.red(intent['desc']):<{width + 9}}│")
        print(f"  │ {Color.red(f'Damage: {dmg}'):<{width + 7}}│")
    elif intent['type'] == 'defend':
        block_val = intent['value']
        print(f"  │ Intent: {Color.cyan(intent['desc']):<{width + 7}}│")
        print(f"  │ {Color.cyan(f'Block: {block_val}'):<{width + 7}}│")
    elif intent['type'] == 'buff':
        buff_val = intent['value']
        print(f"  │ Intent: {Color.yellow(intent['desc']):<{width + 7}}│")
        print(f"  │ {Color.yellow(f'Strength +{buff_val}'):<{width + 7}}│")
    print(f"  └{'─' * width}┘")


def run_combat(player: Player, enemy: Enemy) -> bool:
    combat = CombatEngine(player, enemy)
    combat.start_combat()

    while not combat.is_over:
        print(f"\n{Color.blue('─' * 40)}")
        print(f"{Color.bold(player.name)} "
              f"HP: {Color.hp_color(player.hp, player.max_hp)} "
              f"Block: {Color.cyan(str(player.block))} "
              f"Energy: {Color.yellow(str(player.energy))}")
        display_enemy(enemy)
        print(f"{Color.blue('─' * 40)}")

        display_hand(player.deck.hand)

        print(f"\n  {Color.yellow('0.')} End turn")
        action = input(f"\n{Color.bold('Your choice: ')}").strip()

        if action == "0":
            combat.end_turn()
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
        print(f"\n{Color.blue('═' * 40)}")
        print(Color.bold(f"Floor {current_floor}"))
        print(f"{Color.blue('═' * 40)}")

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





