from game.models import Card, Enemy, Player
from game.colors import Color

def display_tile():
    """
        Display the game title screen.
    """
    width = 40
    print(f"\n{Color.magenta('═' * width)}")
    print(f"\n{Color.bold(Color.magenta(f'Spire the Slayer')):^{width + 15}}")
    print(f"\n{Color.magenta('═' * width)}")

def display_ongoing_runs(ongoing_runs: list[dict]):
    """
        Display all ongoing runs with their current state.
    """
    print(f"\n{Color.bold('Ongoing runs:')}")
    for run in ongoing_runs:
        print(f"  {Color.blue(str(run['id']))}. "
              f"{Color.bold(run['player_name'])} "
              f"— Floor {Color.magenta(str(run['current_floor']))} "
              f"— HP {Color.hp_color(run['current_hp'], run['max_hp'])}")
    print(f"\n  {Color.blue('0.')} Start a new run")

def display_floor(floor: int):
    """
        Display the current floor header.
    """
    width = 40
    print(f"\n{Color.magenta('═' * width)}")
    print(f"{Color.bold(Color.magenta(f'Floor {floor}')):^{width + 15}}")
    print(f"{Color.magenta('═' * width)}")

def display_player(player: Player):
    """
        Display player current state: name, hp, block and energy.
    """
    print(f"{Color.bold(player.name)} "
          f"HP: {Color.hp_color(player.hp, player.max_hp)} "
          f"Block: {Color.cyan(str(player.block))} "
          f"Energy: {Color.yellow(str(player.energy))}")

def display_hand(hand: list[Card]):
    """
        Display all cards in hand side by side with color coding.
        Each card shows name, cost, description, damage and block.
    """
    print(f"\n{Color.bold('Your hand:')}")
    _display_cards(hand)

def display_rewards(rewards: list[Card]):
    """
        Display reward cards side by side with color coding.
        Same layout as hand cards — name, cost, description, damage, block.
    """
    print(f"\n{Color.bold('Choose a card to add to your deck:')}")
    _display_cards(rewards)
    print(f"\n  {Color.blue('0.')} Skip")

def display_enemy(enemy: Enemy):
    """
        Display enemy current state and upcoming action with color coding.
        Attack intent shown in red, defend in cyan, buff in yellow.
    """
    intent = enemy.get_intent()
    width = 40

    print(f"\n  ┌{'─' * width}┐")
    print(f"  │ {Color.bold(Color.magenta(enemy.name)):^{width + 16}}│")
    print(f"  │ HP: {Color.hp_color(enemy.hp, enemy.max_hp):<{width + 4}}│")
    if enemy.block > 0:
        print(f"  │ {Color.cyan(f'Block: {enemy.block}'):<{width + 7}}│")

    if intent['type'] == 'attack':
        dmg = intent['value'] + enemy.strength
        print(f"  │ Intent: {Color.red(intent['desc']):<{width + 0}}│")
        print(f"  │ {Color.red(f'Damage: {dmg}'):<{width + 8}}│")
    elif intent['type'] == 'defend':
        block_val = intent['value']
        print(f"  │ Intent: {Color.cyan(intent['desc']):<{width + 0}}│")
        print(f"  │ {Color.cyan(f'Block: {block_val}'):<{width + 8}}│")
    elif intent['type'] == 'buff':
        buff_val = intent['value']
        print(f"  │ Intent: {Color.yellow(intent['desc']):<{width + 0}}│")
        print(f"  │ {Color.yellow(f'Strength +{buff_val}'):<{width + 8}}│")
    print(f"  └{'─' * width}┘")

def display_separator():
    """
        Display a combat separator line.
    """
    width = 40
    print(f"{Color.blue('─' * width)}")

def _card_lines(i: int, card: Card, width: int = 22) -> list[str]:
    """
        Internal helper, builds the list of lines for a single card.
        Used by both display_hand() and display_rewards().

        f"{'Hi':<{width}}"   # 'Hi        '  — 2 chars + 8 spaces = 10 total
        f"{'Hi':>{width}}"   # '        Hi'  — 8 spaces + 2 chars = 10 total (right align)
        f"{'Hi':^{width}}"   # '    Hi    '  — centered (center align)
    """
    lines = []
    lines.append(f"  ┌{'─' * (width - 3)}[{Color.blue(str(i))}]┐")
    lines.append(f"  │ {Color.bold(card.name):<{width + 7}}│")
    lines.append(f"  │ {Color.yellow(f'Cost: {card.cost}'):<{width + 8}}│")
    lines.append(f"  │ {card.description[:width - 1]:<{width - 1}}│")
    if card.damage > 0:
        lines.append(f"  │ {Color.red(f'Damage: {card.damage}'):<{width + 8}}│")
    else:
        lines.append(f"  │{' ' * width}│")
    if card.block > 0:
        lines.append(f"  │ {Color.cyan(f'Block:  {card.block}'):<{width + 8}}│")
    else:
        lines.append(f"  │{' ' * width}│")
    lines.append(f"  └{'─' * width}┘")
    return lines

def _display_cards(cards: list[Card]):
    """
        Internal helper, displays a list of cards side by side.
        Used by both display_hand() and display_rewards().

        enumerate(iterable, start=0) :
                Return an enumerate object. iterable must be a sequence, an iterator, or some other object which supports iteration.
                The __next__() method of the iterator returned by enumerate() returns a tuple containing a count (from start which defaults to 0)
                and the values obtained from iterating over iterable.

        zip(*iterables, strict=False) :
            Iterate over several iterables in parallel, producing tuples with an item from each one.
    """
    all_cards_lines = [_card_lines(i, card) for i, card in enumerate(cards, 1)]
    for row in zip(*all_cards_lines):
        print("".join(row))