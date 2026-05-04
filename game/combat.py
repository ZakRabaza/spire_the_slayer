from game.models import Card, Player, Enemy

class CombatEngine:
    def __init__(self, player: Player, enemy: Enemy):
        """
            Initialize the combat engine with a player and enemy.
            The caller is responsible for creating both objects before passing them in.
        """
        self.player = player
        self.enemy = enemy

    def start_combat(self):
        """
            Begin the fight, draw the player's opening hand.
            Called once before the first turn.
        """
        self.player.start_turn()

    def play_card(self, card: Card):
        """
            Play a card from the player's hand.
            Raises ValueError if the card is not in hand or the player has insufficient energy.
        """
        if card not in self.player.deck.hand:
            raise ValueError(f"{card.name} is not in hand")
        if self.player.energy < card.cost:
            raise ValueError(f"Not enough energy to play {card.name}")

        self.player.energy -= card.cost

        if card.damage > 0:
            self.enemy.take_damage(card.damage + self.player.strength)
        if card.block > 0:
            self.player.gain_block(card.block)

        self.player.deck.discard(card)

    def end_turn(self):
        """
            End the player's turn and let the enemy act.
            Order: discard hand → enemy start_turn → enemy acts → player start_turn.
        """
        self.player.end_turn()
        self.enemy.start_turn()
        if self.enemy.is_alive:
            self.enemy.act(self.player)
        if self.player.is_alive:
            self.player.start_turn()

    @property
    def is_over(self) -> bool:
        """
            True if either the player or enemy has reached 0 hp.
        """
        return not self.player.is_alive or not self.enemy.is_alive

    @property
    def player_won(self) -> bool:
        """
            True if the enemy is dead and the player is still alive.
            Only meaningful when is_over is True.
        """
        return not self.enemy.is_alive and self.player.is_alive