import unittest
from game.models import Card, Deck, Player, Enemy


class TestCard(unittest.TestCase):

    def setUp(self):
        self.strike = Card(1, "Strike", "attack", 1, "Deal 6 damage.", 6, 0, "starter")
        self.defend = Card(2, "Defend", "skill",  1, "Gain 5 block.",  0, 5, "starter")

    def test_repr(self):
        self.assertEqual(repr(self.strike), "Card('Strike', cost=1, dmg=6, block=0)")

    def test_equality_same_id(self):
        same = Card(1, "Strike", "attack", 1, "Deal 6 damage.", 6, 0, "starter")
        self.assertEqual(self.strike, same)

    def test_equality_different_id(self):
        self.assertNotEqual(self.strike, self.defend)


class TestDeck(unittest.TestCase):

    def setUp(self):
        strike = Card(1, "Strike", "attack", 1, "Deal 6 damage.", 6, 0, "starter")
        defend = Card(2, "Defend", "skill",  1, "Gain 5 block.",  0, 5, "starter")
        self.cards = [strike] * 5 + [defend] * 5
        self.deck = Deck(self.cards)

    def test_initial_state(self):
        self.assertEqual(len(self.deck.draw_pile), 10)
        self.assertEqual(len(self.deck.hand), 0)
        self.assertEqual(len(self.deck.discard_pile), 0)

    def test_draw(self):
        self.deck.draw(5)
        self.assertEqual(len(self.deck.hand), 5)
        self.assertEqual(len(self.deck.draw_pile), 5)

    def test_discard(self):
        self.deck.draw(5)
        hand_size_before = len(self.deck.hand)
        card = self.deck.hand[0]
        self.deck.discard(card)
        self.assertEqual(len(self.deck.hand), hand_size_before - 1)  # one less in hand
        self.assertEqual(len(self.deck.discard_pile), 1)

    def test_discard_hand(self):
        self.deck.draw(5)
        self.deck.discard_hand()
        self.assertEqual(len(self.deck.hand), 0)
        self.assertEqual(len(self.deck.discard_pile), 5)

    def test_recycle_discard(self):
        """Drawing more cards than draw pile triggers a reshuffle."""
        self.deck.draw(10)          # empty the draw pile into hand
        self.deck.discard_hand()    # move all to discard
        self.deck.draw(5)           # should trigger recycle
        self.assertEqual(len(self.deck.hand), 5)
        self.assertEqual(len(self.deck.draw_pile), 5)
        self.assertEqual(len(self.deck.discard_pile), 0)

    def test_draw_empty_deck(self):
        """Drawing from a completely empty deck does not crash."""
        self.deck.draw(10)
        # don't discard, hand is full, draw and discard are both empty
        self.deck.draw(5)  # should silently do nothing
        self.assertEqual(len(self.deck.hand), 10)  # still just the original 10


class TestPlayer(unittest.TestCase):

    def setUp(self):
        strike = Card(1, "Strike", "attack", 1, "Deal 6 damage.", 6, 0, "starter")
        defend = Card(2, "Defend", "skill",  1, "Gain 5 block.",  0, 5, "starter")
        deck = Deck([strike] * 5 + [defend] * 5)
        self.player = Player("Hero", hp=75, max_hp=75, deck=deck)

    def test_initial_state(self):
        self.assertEqual(self.player.hp, 75)
        self.assertEqual(self.player.block, 0)
        self.assertEqual(self.player.energy, 3)
        self.assertTrue(self.player.is_alive)

    def test_take_damage(self):
        self.player.take_damage(10)
        self.assertEqual(self.player.hp, 65)

    def test_block_absorbs_damage(self):
        self.player.gain_block(5)
        self.player.take_damage(3)
        self.assertEqual(self.player.hp, 75)   # no hp lost
        self.assertEqual(self.player.block, 2) # 2 block remaining

    def test_block_partially_absorbs(self):
        self.player.gain_block(5)
        self.player.take_damage(8)
        self.assertEqual(self.player.hp, 72)   # 3 bleed through
        self.assertEqual(self.player.block, 0)

    def test_block_resets_on_start_turn(self):
        self.player.gain_block(10)
        self.player.start_turn()
        self.assertEqual(self.player.block, 0)

    def test_energy_resets_on_start_turn(self):
        self.player.energy = 0
        self.player.start_turn()
        self.assertEqual(self.player.energy, 3)

    def test_start_turn_draws_five(self):
        self.player.start_turn()
        self.assertEqual(len(self.player.deck.hand), 5)

    def test_is_alive_false_at_zero_hp(self):
        self.player.take_damage(75)
        self.assertFalse(self.player.is_alive)


class TestEnemy(unittest.TestCase):

    def setUp(self):
        strike = Card(1, "Strike", "attack", 1, "Deal 6 damage.", 6, 0, "starter")
        defend = Card(2, "Defend", "skill",  1, "Gain 5 block.",  0, 5, "starter")
        deck = Deck([strike] * 5 + [defend] * 5)
        self.player = Player("Hero", hp=75, max_hp=75, deck=deck)
        self.cultist = Enemy(
            id=2,
            name="Cultist",
            max_hp=50,
            actions=[
                {"type": "attack", "value": 6, "desc": "slashes"},
                {"type": "buff",   "value": 2, "desc": "chants"},
                {"type": "attack", "value": 6, "desc": "slashes"},
            ]
        )

    def test_initial_intent(self):
        self.assertEqual(self.cultist.get_intent()["desc"], "slashes")

    def test_action_cycles(self):
        self.cultist.act(self.player)  # executes slashes (0), next=1
        self.assertEqual(self.cultist.get_intent()["desc"], "chants")
        self.cultist.act(self.player)  # executes chants (1), next=2
        self.assertEqual(self.cultist.get_intent()["desc"], "slashes")
        self.cultist.act(self.player)  # executes slashes (2), next=3
        self.assertEqual(self.cultist.get_intent()["desc"], "slashes")  # 3%3=0 → wraps to start

    def test_attack_deals_damage(self):
        self.cultist.act(self.player)   # slashes for 6
        self.assertEqual(self.player.hp, 69)

    def test_buff_increases_strength(self):
        self.cultist.act(self.player)   # slashes (index 0)
        self.cultist.act(self.player)   # chants  (index 1)
        self.assertEqual(self.cultist.strength, 2)

    def test_strength_adds_to_damage(self):
        self.cultist.act(self.player)   # slashes for 6
        self.cultist.act(self.player)   # chants, gains 2 strength
        self.cultist.act(self.player)   # slashes for 6 + 2 = 8
        self.assertEqual(self.player.hp, 61)

    def test_take_damage(self):
        self.cultist.take_damage(20)
        self.assertEqual(self.cultist.hp, 30)

    def test_is_alive_false_at_zero_hp(self):
        self.cultist.take_damage(50)
        self.assertFalse(self.cultist.is_alive)


if __name__ == "__main__":
    unittest.main(verbosity=2)