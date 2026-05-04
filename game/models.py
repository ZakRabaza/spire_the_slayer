import random


class Card:
    def __init__(self, id: int, name: str, card_type: str,cost: int, description: str,damage: int, block: int, rarity: str):
        """
            Initialize a Card from a row in the cards table.

            Args:
                id:          Primary key from the database.
                name:        Card name, unique in the catalog.
                card_type:   'attack', 'skill', or 'power'.
                cost:        Energy required to play the card.
                description: Human-readable effect description.
                damage:      Damage dealt to the enemy when played.
                block:       Block gained by the player when played.
                rarity:      'starter', 'common', 'uncommon', or 'rare'.
        """

        self.id = id
        self.name = name
        self.card_type = card_type
        self.cost = cost
        self.description = description
        self.damage = damage
        self.block = block
        self.rarity = rarity

    def __repr__(self):
        """
            Return an unambiguous string representation of the card.
            Used when printing the object or displaying it in a list.
        """
        return f"Card({self.name!r}, cost={self.cost}, dmg={self.damage}, block={self.block})"

    def __eq__(self, other):
        """
            Two cards are equal if they share the same database id,meaning they represent the same card type from the catalog.
            Note: a deck can contain multiple copies of the same card, list.remove() in Deck.discard() removes only the first match.

            isinstance() guards against comparing with non-Card types
            (e.g. strings, integers) which would cause an AttributeError when accessing .id on an object that doesn't have it.
        """
        return isinstance(other, Card) and self.id == other.id

class Deck:
    def __init__(self, cards: list[Card]):
        """
            Initialize the deck from a list of Card objects.

            Args:
                cards: List of Card objects loaded from the database for the current run.
                Typically, 5x Strike + 5x Defend at the start of a new run.

            cards[:] creates a shallow copy so the original list is not affected when the draw pile is shuffled.
            A shallow copy is sufficient because Card objects are never modified, only moved between piles.
            cards[:] is a shallow copy, sufficient because Card objects are never modified in place.
            Upgrades must return a new Card object rather than mutating the existing one.
        """
        self.draw_pile: list[Card] = cards[:]
        self.hand: list[Card] = []
        self.discard_pile: list[Card] = []
        random.shuffle(self.draw_pile)

    def draw(self, n: int = 1):
        """
            Draw n cards from the draw pile into the hand.
            If the draw pile runs empty mid-draw, the discard pile is shuffled back into the draw pile and drawing continues.
            If both piles are empty, drawing stops silently.
        """
        for _ in range(n):
            if not self.draw_pile:
                if not self.discard_pile:
                    return
                self._recycle_discard()
            self.hand.append(self.draw_pile.pop())

    def discard(self, card: Card):
        """
            Discard a single card from the hand to the discard pile.
            Called by CombatEngine when the player plays a card.
        """
        self.hand.remove(card)
        self.discard_pile.append(card)

    def discard_hand(self):
        """
            Move all remaining cards in hand to the discard pile.
            Called at the end of the player's turn via Player.end_turn().

            Uses extend() to add all hand cards to discard in one operation,
            then clear() to empty the hand in place, both faster than looping with append() or reassigning to a new list.
        """
        self.discard_pile.extend(self.hand)
        self.hand.clear()

    def _recycle_discard(self):
        """
            Internal method, do not call directly.
            Copies the discard pile into a new draw pile (shallow copy), clears the discard pile, then shuffles the draw pile.
            Called automatically by draw() when the draw pile runs empty.
        """
        self.draw_pile = self.discard_pile[:]
        self.discard_pile.clear()
        random.shuffle(self.draw_pile)

    def __repr__(self):
        """
            Return a summary of the deck state showing the number of cards in each pile.
            Useful for debugging during combat.
        """
        return (f"Deck(draw={len(self.draw_pile)}, "
                f"hand={len(self.hand)}, discard={len(self.discard_pile)})")

class Player:
    STARTING_ENERGY = 3

    def __init__(self, name: str, hp: int, max_hp: int, deck: "Deck"):
        """
            Initialize a Player for a new run.

            Args:
                name:    Player name, stored in the runs table.
                hp:      Current hit points, persisted after each fight.
                max_hp:  Maximum hit points, default 75 in the runs table.
                deck:    The player's Deck, built from run_cards at game start.
        """
        self.name = name
        self.hp = hp
        self.max_hp = max_hp
        self.block = 0
        self.energy = self.STARTING_ENERGY
        self.strength = 0
        self.deck = deck

    def take_damage(self, amount: int):
        """
            Apply damage to the player, block absorbs first.

            Args:
                amount: Raw damage incoming before block is applied.

            absorbed = min(block, amount) ensures block never absorbs more than the incoming damage,
            leaving remaining block intact when block exceeds the damage amount.
        """
        absorbed = min(self.block, amount)
        self.block -= absorbed
        self.hp -= (amount - absorbed)

    def gain_block(self, amount: int):
        """
            Add block to the player.

            Args:
                amount: Block gained from playing a skill card.

            Block accumulates within a turn — playing multiple
            Defend cards stacks the block values together.
        """
        self.block += amount

    def start_turn(self):
        """
            Begin the player's turn: reset block and energy, draw 5 cards.

            Block resets here rather than at end_turn() so that block gained during the player's turn remains active when the enemy
            attacks at the end of the round.
            Block does not carry over between rounds, this prevents indefinite stacking.
        """
        self.block = 0
        self.energy = self.STARTING_ENERGY
        self.deck.draw(5)

    def end_turn(self):
        """
            End the player's turn by discarding all remaining cards in hand.
            Called by CombatEngine after the player finishes playing cards.
            Block is intentionally NOT reset here, it must remain active for the enemy attack phase that follows.
        """
        self.deck.discard_hand()

    @property
    def is_alive(self) -> bool:
        """
            With @property you call it like an attribute, no parentheses, improve readability and computed on the fly.
            True if the player has more than 0 hp.
            Computed directly from hp on each access, never stored separately to avoid getting out of sync.
        """
        return self.hp > 0

    def __repr__(self):
        """
            Return a summary of the player state showing name,
            current and max hp, and current block.
            Useful for debugging during combat.
        """
        return f"Player({self.name!r}, hp={self.hp}/{self.max_hp}, block={self.block})"

class Enemy:
    def __init__(self, id: int, name: str, max_hp: int, actions: list[dict]):
        """
            Initialize an Enemy from a row in the enemies table.

            Args:
                id:      Primary key from the database.
                name:    Enemy name.
                max_hp:  Maximum hit points, used to reset hp at the start of a fight.
                actions: List of action dicts loaded from the JSONB column in the enemies table.
                         Each action has 'type', 'value', and 'desc'.
                         Example: [{"type": "attack", "value": 6, "desc": "slashes"}]

            _action_index tracks the current position in the action cycle.
            Leading underscore signals it is internal state, not part of the public interface.
        """
        self.id = id
        self.name = name
        self.hp = max_hp
        self.max_hp = max_hp
        self.block = 0
        self.strength = 0
        self.actions = actions
        self._action_index = 0

    def get_intent(self) -> dict:
        """
           Return the action the enemy will perform this turn.
           Shown to the player before they choose a card to play.

           Uses % len(actions) to cycle through actions indefinitely,
           _action_index increments forever but modulo maps it back to a valid index automatically, with no manual reset needed.
        """
        return self.actions[self._action_index % len(self.actions)]

    def act(self, player: "Player"):
        """
            Execute the current action against the player, then advance the action cycle by incrementing _action_index.

            Action types:
                attack: deal action value + self.strength damage to player.
                defend: gain action value as block.
                buff:   permanently increase self.strength by action value, which adds to all future attack damage.
        """
        action = self.get_intent()
        if action["type"] == "attack":
            player.take_damage(action["value"] + self.strength)
        elif action["type"] == "defend":
            self.block += action["value"]
        elif action["type"] == "buff":
            self.strength += action["value"]
        self._action_index += 1

    def take_damage(self, amount: int):
        """
            Apply damage to the enemy, block absorbs first.

            Args:
                amount: Raw damage incoming before block is applied.

            absorbed = min(block, amount) ensures block never absorbs more than the incoming damage,
            leaving remaining block intact when block exceeds the damage amount.
        """
        absorbed = min(self.block, amount)
        self.block -= absorbed
        self.hp -= (amount - absorbed)

    def gain_block(self, amount: int):
        """
            Add block to the enemy.
        """
        self.block += amount

    def start_turn(self):
        """
            Reset block at the start of the enemy's turn.
        """
        self.block = 0

    @property
    def is_alive(self) -> bool:
        """
            With @property you call it like an attribute, no parentheses, improve readability and computed on the fly.
            True if the enemy has more than 0 hp.
            Computed directly from hp on each access, never stored separately to avoid getting out of sync.
        """
        return self.hp > 0

    def __repr__(self):
        """
            Return a summary of the enemy state showing name, current and max hp, and the description of the current intent,
            what the enemy plans to do this turn.
            Useful for debugging during combat.
        """
        return (f"Enemy({self.name!r}, hp={self.hp}/{self.max_hp}, "
                f"intent={self.get_intent()['desc']})")