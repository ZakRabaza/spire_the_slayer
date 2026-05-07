import psycopg2
import psycopg2.extras
import sys
import os

sys.path.append(os.path.join(os.path.dirname(str(__file__)), '..'))
from game.models import Card, Enemy

DB_CONFIG = {
    "dbname":   "spire_the_slayer",
    "user":     "postgres",
    "password": "root",
    "host":     "172.17.58.171",
    "port":     5432,
}

def get_conn():
    """
        Return a new connection to the database.
        The caller is responsible for closing it.
    """
    return psycopg2.connect(**DB_CONFIG)


# ── Cards ──────────────────────────────────────────────


def get_reward_cards(n: int = 3) -> list[Card]:
    """
        Return n random playable cards to offer as post-combat rewards.
        Only cards with playable = true are eligible.

        Args:
            n: Number of cards to offer, default 3.
    """
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, name, card_type, cost, description, damage, block, rarity, effects
                FROM cards
                WHERE playable = true
                ORDER BY RANDOM()
                LIMIT %s
            """, (n,))
            rows = cur.fetchall()
        return [Card.from_db_row(row) for row in rows]
    finally:
        conn.close()


def get_enemy_for_floor(floor: int) -> Enemy:
    """
        Return a random enemy eligible for the given floor number.
        An enemy is eligible if floor_min <= floor <= floor_max.

        Args:
            floor: The current floor number.
    """
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, name, max_hp, actions
                FROM enemies
                WHERE floor_min <= %s AND floor_max >= %s
                ORDER BY RANDOM()
                LIMIT 1
            """, (floor, floor))
            row = cur.fetchone()
        if row is None:
            raise ValueError(f"No enemy found for floor {floor}")
        return Enemy.from_db_row(row)
    finally:
        conn.close()


# ── Runs ───────────────────────────────────────────────

def create_run(player_name: str = "Player") -> int:
    """
        Insert a new run into the runs table and return its id.
        Also inserts 5x Strike + 5x Defend into run_cards as starter cards.

        Args:
            player_name: The player's name, default 'Player'.

        Returns:
            The new run's id.
    """
    conn = get_conn()
    try:
        with conn:
            with conn.cursor() as cur:
                # Create the run
                cur.execute("""
                    INSERT INTO runs (player_name, current_hp, max_hp)
                    VALUES (%s, 75, 75)
                    RETURNING id
                """, (player_name,))
                run_id = cur.fetchone()[0]

                # Get starter card ids
                cur.execute("""
                    SELECT id FROM cards WHERE rarity = 'starter'
                """)
                starter_ids = [row[0] for row in cur.fetchall()]

                # Insert 5 copies of each starter card
                for card_id in starter_ids:
                    for _ in range(5):
                        cur.execute("""
                            INSERT INTO run_cards (run_id, card_id, source)
                            VALUES (%s, %s, 'starter')
                        """, (run_id, card_id))
        return run_id
    finally:
        conn.close()


def get_run(run_id: int) -> dict:
    """
        Return the current state of a run as a dict.

        Args:
            run_id: The run's id.
    """
    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT id, player_name, current_hp, max_hp, current_floor, gold, outcome
                FROM runs
                WHERE id = %s
            """, (run_id,))
            row = cur.fetchone()
            if row is None:
                raise ValueError(f"Run {run_id} not found")
            return dict(row)
    finally:
        conn.close()


def get_deck_for_run(run_id: int) -> list[Card]:
    """
        Return all cards in a run's deck as Card objects.
        Joins run_cards with cards to get full card details.

        Args:
            run_id: The run's id.
    """
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT c.id, c.name, c.card_type, c.cost, c.description, c.damage, c.block, c.rarity, c.effects
                FROM run_cards rc
                JOIN cards c ON c.id = rc.card_id
                WHERE rc.run_id = %s
            """, (run_id,))
            rows = cur.fetchall()
        return [Card.from_db_row(row) for row in rows]
    finally:
        conn.close()


def save_run_after_combat(run_id: int, current_hp: int,
                          current_floor: int, reward_card_id: int | None = None):
    """
        Atomically update run state after a combat ends.
        Updates hp and floor, optionally adds a reward card.
        All changes are committed together — if anything fails, the entire transaction rolls back.

        Args:
            run_id:         The run's id.
            current_hp:     Player's hp after combat.
            current_floor:  The new floor number.
            reward_card_id: Card id chosen as reward, or None if skipped.
    """
    conn = get_conn()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE runs
                    SET current_hp = %s, current_floor = %s
                    WHERE id = %s
                """, (current_hp, current_floor, run_id))

                if reward_card_id is not None:
                    cur.execute("""
                        INSERT INTO run_cards (run_id, card_id, source)
                        VALUES (%s, %s, 'reward')
                    """, (run_id, reward_card_id))
    finally:
        conn.close()


def end_run(run_id: int, outcome: str):
    """
        Mark a run as finished with the given outcome.

        Args:
            run_id:  The run's id.
            outcome: 'victory' or 'defeat'.
    """
    conn = get_conn()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE runs SET outcome = %s WHERE id = %s
                """, (outcome, run_id))
    finally:
        conn.close()


def get_ongoing_runs() -> list[dict]:
    """
        Return all ongoing runs ordered by most recent first.
        Used by main.py to let the player resume an existing run.
    """
    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                        SELECT id, player_name, current_hp, max_hp, current_floor
                        FROM runs
                        WHERE outcome = 'ongoing'
                        ORDER BY id DESC
                        """)
            rows = cur.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()