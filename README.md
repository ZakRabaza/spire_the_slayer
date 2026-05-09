
## Spire the Slayer

A terminal-based deck-building roguelike inspired by Slay the Spire, built in Python with a PostgreSQL database.

---

### What it is

You fight enemies floor by floor, managing a hand of cards each turn. After each fight you choose a new card to add to your deck. The game ends when you clear all 10 floors or die trying. Progress is saved to the database after every fight, you can quit and resume at any time.

---

### How to run it

#### Prerequisites

- Python 3.11+
- PostgreSQL 16
- WSL (if running on Windows, see [WSL setup](#wsl-setup))

#### First time setup

bash

```bash
# 1. Clone the repository
git clone https://github.com/ZakRabaza/spire_the_slayer.git
cd spire_the_slayer

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate          # Linux/WSL
venv\Scripts\activate             # Windows

# 3. Install dependencies
pip install psycopg2-binary

# 4. Start PostgreSQL
sudo service postgresql start

# 5. Set the postgres password
sudo -u postgres psql
ALTER USER postgres PASSWORD 'root';
\q

# 6. Create and seed the database
cd db
python3 setup.py
cd ..

# 7. Run the game
python3 main.py
```

#### Every subsequent session

bash

```bash
source venv/bin/activate
sudo service postgresql start
python3 main.py
```

---

### How to play
   
```
Enter your name: Hero
Run created — good luck, Hero!

Welcome, Hero!
Starting on floor 1.

════════════════════════════════════════
               Floor 1                
════════════════════════════════════════
An enemy appears: Slime (hp=25)


────────────────────────────────────────
Hero HP: 75/75 Block: 0 Energy: 3 Strength: 0 

  ┌────────────────────────────────────────┐
  │                  Slime                 │
  │ HP: 25/25                              │
  │ Intent: slimes you                     │
  │ Damage: 5                              │
  └────────────────────────────────────────┘
────────────────────────────────────────

Your hand:
  ┌───────────────────[1]┐  ┌───────────────────[2]┐
  │ Strike               │  │ Defend               │
  │ Cost: 1              │  │ Cost: 1              │
  │ Deal 6 damage.       │  │ Gain 5 block.        │
  │ Damage: 6            │  │                      │
  │                      │  │ Block:  5            │
  └──────────────────────┘  └──────────────────────┘


  0. End turn
  d. View draw pile 5 cards
  x. View discard pile 0 cards

Your choice: 
```


- Enter a card number to play it
- Enter `0` to end your turn
- Enter `d` to view your draw pile
- Enter `x` to view your discard pile
- After each fight pick a card reward or skip

---

### Project structure

```
spire_the_slayer/
├── main.py                  — entry point, run selection
├── game/
│   ├── colors.py            — ANSI color helpers
│   ├── combat.py            — CombatEngine
│	├── display.py           — all terminal display functions
│	├── game_loop.py         — floor progression, combat loop, rewards
│	└── models.py            — Card, Deck, Player, Enemy
├── db/
│   ├── database.py          — repository, all SQL queries
│	│── reset.py             — drops and rebuilds (development only)
│   ├── schema.sql           — table definitions, constraints, indexes
│   ├── seed.sql             — static card and enemy data
│   └── setup.py             — creates and seeds the database
└── tests/
	├──	test_combat.py       — 18 unit tests for CombatEngine
    └── test_models.py       — 24 unit tests for models
```

---

### Running the tests

bash

```bash
python3 -m unittest tests.test_models tests.test_combat -v
```

42 tests, all passing.

---

### Database schema

Four tables with real relational structure:

```
cards        — static card catalog (14 cards)
enemies      — static enemy catalog (5 enemies)
runs         — one row per playthrough
run_cards    — junction table: cards in a run's deck
```

`run_cards` is a proper many-to-many junction table — not an array column — which allows direct joins and per-card queries.

Enemy actions and card effects are stored as JSONB, consistent with the data-driven design: adding a new effect type requires no schema change.

---

### Design decisions

#### Repository pattern

All SQL lives in `db/database.py`. No other file touches the database directly. Swapping PostgreSQL for another backend would only require changing this one file.

#### Factory pattern

`Card.from_db_row()` and `Enemy.from_db_row()` centralize object construction from database rows. If a field is added to a table, only the factory method needs updating — not every place that builds the object.

#### Strategy pattern — data-driven variant

`CombatEngine` never checks what a card does. It calls `card.apply(player, enemy)` and the card handles itself. Simple effects (draw, strength, hp loss) are stored as JSONB and executed by a dispatcher. Complex effects that depend on runtime state would use subclasses registered in `CARD_REGISTRY`, but none of the current cards require it.

#### Transactions

Post-combat state is saved atomically, HP update, floor advance, and reward card insert all commit together or all roll back. A player can never advance a floor without their HP being saved.

#### JSONB for variable-length data

Enemy `actions` and card `effects` are stored as JSONB rather than separate tables. Both are ordered, read-only catalog data that is never filtered or joined individually, JSONB avoids unnecessary table complexity with no query cost.

---

### Cards

|Name|Type|Cost|Effect|
|---|---|---|---|
|Strike|attack|1|Deal 6 damage|
|Defend|skill|1|Gain 5 block|
|Bash|attack|2|Deal 8 damage|
|Twin Strike|attack|1|Deal 5 damage|
|Iron Wave|attack|1|Deal 5 damage, gain 5 block|
|Shrug It Off|skill|1|Gain 8 block|
|Bludgeon|attack|3|Deal 32 damage|
|Hemokinesis|attack|1|Lose 2 HP, deal 15 damage|
|Battle Trance|skill|0|Draw 3 cards|
|Taunt|skill|1|Gain 7 block|
|Inflame|power|1|Gain 2 strength|
|Impervious|skill|2|Gain 30 block|

Starter cards (Strike, Defend) are not offered as rewards. Cards with unimplemented effects (`Demon Form`, `Pyre`) are marked `playable = false` and never appear as rewards.

---

### Enemies

|Name|HP|Floors|Pattern|
|---|---|---|---|
|Slime|25|1–3|attack, attack|
|Cultist|50|1–5|attack, buff, attack|
|Jaw Worm|40|2–6|attack, defend, attack|
|Gremlin Nob|82|4–8|buff, attack, attack|
|Lagavulin|112|6–10|defend, attack, attack|

---

### Known limitations and future improvements

- **No card upgrades**: upgrading a card would return a new `Card` object rather than mutating the existing one, preserving immutability
- **No status effects**: vulnerable, weak, poison would extend the `_apply_effect()` dispatcher with no structural changes
- **No map or branching paths**: floors are strictly linear
- `Demon Form` and `Pyre`: per-turn effects require a hook in `start_turn()`, not yet implemented
- `Twin Strike`: needs to strike twice instead of once 
- **Gold is tracked but unused**: shop system would be the natural next step
- **Single character class**: multiple classes would use the Strategy pattern for different starting decks and card pools

---

### WSL setup

If running on Windows with WSL, GUI tools (PgAdmin, PyCharm database panel) need the WSL IP to connect — not `localhost`.

bash

```bash
# get your WSL IP — changes on every restart
hostname -I
```

PostgreSQL must also be configured to accept TCP connections:

bash

```bash
# /etc/postgresql/16/main/postgresql.conf
listen_addresses = '*'

# /etc/postgresql/16/main/pg_hba.conf  — add this line
hostssl all all 0.0.0.0/0 md5
```

bash

```bash
sudo service postgresql restart
```

Use the WSL IP in PyCharm/PgAdmin instead of `localhost`. See the full WSL connection note in the project documentation for details.

---

### Dependencies

| Package         | Version | Purpose           |
| --------------- | ------- | ----------------- |
| psycopg2-binary | 2.9.12  | PostgreSQL driver |

No other external dependencies, the game engine, display, and combat logic use only the Python standard library.

---

### Screens:

<img width="412" height="242" alt="spire_the_slayer_start_screen" src="https://github.com/user-attachments/assets/af402c86-5a6b-4341-a4db-44f85ded4585" />

---

<img width="1330" height="870" alt="spire_the_slayer_start_game" src="https://github.com/user-attachments/assets/ee4e3dc9-0dd4-48cc-8a49-b3747ed1e53f" />



