# tests/test_combat.py
import unittest
from game.models import Card, Deck, Player, Enemy
from game.combat import CombatEngine


class TestCombatEngine(unittest.TestCase):

    def setUp(self):
        strike = Card(1, "Strike", "attack", 1, "Deal 6 damage.", 6, 0, "starter")
        defend = Card(2, "Defend", "skill",  1, "Gain 5 block.",  0, 5, "starter")
        deck = Deck([strike] * 5 + [defend] * 5)
        self.player = Player("Hero", hp=75, max_hp=75, deck=deck)
        self.slime = Enemy(1, "Slime", 25, [
            {"type": "attack", "value": 5, "desc": "slimes you"},
            {"type": "attack", "value": 5, "desc": "slimes you"}
        ])
        self.combat = CombatEngine(self.player, self.slime)
        self.combat.start_combat()

    def _get_card(self, name: str) -> Card:
        """Helper — find a card by name in the player's hand."""
        return next(c for c in self.player.deck.hand if c.name == name)

    # ── start_combat ───────────────────────────────────────

    def test_start_combat_draws_five_cards(self):
        self.assertEqual(len(self.player.deck.hand), 5)

    # ── play_card ──────────────────────────────────────────

    def test_play_strike_deals_damage(self):
        strike = self._get_card("Strike")
        self.combat.play_card(strike)
        self.assertEqual(self.slime.hp, 19, "Strike should deal 6 damage to slime")

    def test_play_defend_gains_block(self):
        defend = self._get_card("Defend")
        self.combat.play_card(defend)
        self.assertEqual(self.player.block, 5, "Defend should give player 5 block")

    def test_play_card_consumes_energy(self):
        strike = self._get_card("Strike")
        self.combat.play_card(strike)
        self.assertEqual(self.player.energy, 2, "Playing a cost-1 card should reduce energy by 1")

    def test_play_card_discards_from_hand(self):
        strike = self._get_card("Strike")
        hand_size = len(self.player.deck.hand)
        self.combat.play_card(strike)
        self.assertEqual(len(self.player.deck.hand), hand_size - 1, "Played card should be removed from hand")
        self.assertEqual(len(self.player.deck.discard_pile), 1, "Played card should appear in discard pile")

    def test_play_card_not_in_hand_raises(self):
        fake = Card(99, "Fake", "attack", 1, "Fake.", 6, 0, "common")
        with self.assertRaises(ValueError):
            self.combat.play_card(fake)

    def test_play_card_insufficient_energy_raises(self):
        self.player.energy = 0
        strike = self._get_card("Strike")
        with self.assertRaises(ValueError):
            self.combat.play_card(strike)

    # ── end_turn ───────────────────────────────────────────

    def test_end_turn_discards_hand(self):
        self.combat.end_turn()
        self.assertEqual(len(self.player.deck.hand), 5, "Player should draw a new hand of 5 after end turn")

    def test_end_turn_enemy_attacks_player(self):
        self.combat.end_turn()
        self.assertEqual(self.player.hp, 70, "Slime should deal 5 damage to player on end turn")

    def test_end_turn_resets_player_block(self):
        defend = self._get_card("Defend")
        self.combat.play_card(defend)
        self.combat.end_turn()
        self.assertEqual(self.player.block, 0, "Player block should reset at start of new turn")

    def test_end_turn_block_absorbs_enemy_damage(self):
        defend = self._get_card("Defend")
        self.combat.play_card(defend)   # gain 5 block
        self.combat.end_turn()          # slime attacks for 5
        self.assertEqual(self.player.hp, 75, "Block should fully absorb slime attack of 5")

    def test_dead_enemy_does_not_act(self):
        """Enemy at 0 hp should not attack the player on end turn."""
        self.slime.hp = 0
        hp_before = self.player.hp
        self.combat.end_turn()
        self.assertEqual(self.player.hp, hp_before, "Dead enemy should not deal damage")

    # ── is_over / player_won ───────────────────────────────

    def test_is_over_false_at_start(self):
        self.assertFalse(self.combat.is_over)

    def test_is_over_true_when_enemy_dead(self):
        self.slime.hp = 0
        self.assertTrue(self.combat.is_over)

    def test_is_over_true_when_player_dead(self):
        self.player.hp = 0
        self.assertTrue(self.combat.is_over)

    def test_player_won_true_when_enemy_dead(self):
        self.slime.hp = 0
        self.assertTrue(self.combat.player_won)

    def test_player_won_false_when_player_dead(self):
        self.player.hp = 0
        self.assertFalse(self.combat.player_won)

    def test_hp_never_goes_below_zero(self):
        """Overkill damage should clamp hp to 0, not go negative."""
        self.slime.take_damage(1000)
        self.assertEqual(self.slime.hp, 0, "HP should be clamped to 0 on overkill damage")
        self.player.take_damage(1000)
        self.assertEqual(self.player.hp, 0, "HP should be clamped to 0 on overkill damage")


if __name__ == "__main__":
    unittest.main(verbosity=2)