-- Starter cards
INSERT INTO cards (name, card_type, cost, description, damage, block, rarity, playable)
VALUES
    ('Strike', 'attack', 1, 'Deal 6 damage.', 6, 0, 'starter', false),
    ('Defend', 'skill',  1, 'Gain 5 block.',  0, 5, 'starter', false)
ON CONFLICT (name) DO NOTHING;

-- Common cards (playable = true, all damage/block only for now)
INSERT INTO cards (name, card_type, cost, description, damage, block, rarity, playable)
VALUES
    ('Bash',         'attack', 2, 'Deal 8 damage. Apply 2 Vulnerable.',        8,  0, 'common', true),
    ('Twin Strike',  'attack', 1, 'Deal 5 damage twice.',  5,  0, 'common', true),
    ('Iron Wave',    'attack', 1, 'Gain 5 block. Deal 5 damage.', 5, 5, 'common', true),
    ('Shrug It Off', 'skill',  1, 'Gain 8 block. Draw 1 card.',         0,  8, 'common', true)
ON CONFLICT (name) DO NOTHING;

-- Uncommon cards (playable = false until effects are implemented)
INSERT INTO cards (name, card_type, cost, description, damage, block, rarity, playable)
VALUES
    ('Bludgeon',      'attack', 3, 'Deal 32 damage.',       32, 0, 'uncommon', true),
    ('Hemokinesis',   'attack', 1, 'Lose 2 HP. Deal 15 damage.', 15, 0, 'uncommon', true),
    ('Battle Trance', 'skill',  0, 'Draw 3 cards.',          0,  0, 'uncommon', true),
    ('Taunt',         'skill',  1, 'Gain 7 block. Apply 1 Vulnerable.',          0,  7, 'uncommon', true),
    ('Inflame',       'power',  1, 'Gain 2 strength.',       0,  0, 'uncommon', true)
ON CONFLICT (name) DO NOTHING;

-- Rare cards
INSERT INTO cards (name, card_type, cost, description, damage, block, rarity, playable)
VALUES
    ('Demon Form', 'power', 3, 'At the start of your turn, gain 2 Strength.', 0,  0,  'rare', false),
    ('Pyre',       'power', 2, 'Gain 1 energy at the start of each turn.',   0,  0,  'rare', false),
    ('Impervious', 'skill', 2, 'Gain 30 block.',            0, 30,  'rare', true)
ON CONFLICT (name) DO NOTHING;

-- Enemies
INSERT INTO enemies (name, max_hp, floor_min, floor_max, actions)
VALUES
    ('Slime', 25, 1, 3,
     '[{"type":"attack","value":5,"desc":"slimes you"},
       {"type":"attack","value":5,"desc":"slimes you"}]'),

    ('Cultist', 50, 1, 5,
     '[{"type":"attack","value":6,"desc":"slashes"},
       {"type":"buff",  "value":2,"desc":"chants (gains 2 strength)"},
       {"type":"attack","value":6,"desc":"slashes"}]'),

    ('Jaw Worm', 40, 2, 6,
     '[{"type":"attack","value":11,"desc":"chomps"},
       {"type":"defend","value":5, "desc":"braces"},
       {"type":"attack","value":7, "desc":"thrashes"}]'),

    ('Gremlin Nob', 82, 4, 8,
     '[{"type":"buff",  "value":3, "desc":"bellows (gains 3 strength)"},
       {"type":"attack","value":14,"desc":"skull bashes"},
       {"type":"attack","value":14,"desc":"skull bashes"}]'),

    ('Lagavulin', 112, 6, 10,
     '[{"type":"defend","value":8, "desc":"sleeps"},
       {"type":"attack","value":18,"desc":"mauls"},
       {"type":"attack","value":18,"desc":"mauls"}]');