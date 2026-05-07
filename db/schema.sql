-- Cards catalog (static data)
CREATE TABLE IF NOT EXISTS cards (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL UNIQUE,
    card_type   VARCHAR(20)  NOT NULL CHECK (card_type IN ('attack', 'skill', 'power')),
    cost        INTEGER      NOT NULL CHECK (cost >= 0),
    description TEXT         NOT NULL,
    damage      INTEGER      NOT NULL DEFAULT 0,
    block       INTEGER      NOT NULL DEFAULT 0,
    rarity      VARCHAR(20)  NOT NULL DEFAULT 'common'
                             CHECK (rarity IN ('starter', 'common', 'uncommon', 'rare')),
    playable    BOOLEAN      NOT NULL DEFAULT false,
    effects     JSONB        NOT NULL DEFAULT '[]'
);

-- Enemies catalog (static data)
CREATE TABLE IF NOT EXISTS enemies (
    id        SERIAL  PRIMARY KEY,
    name      VARCHAR(100) NOT NULL,
    max_hp    INTEGER      NOT NULL,
    floor_min INTEGER      NOT NULL,
    floor_max INTEGER      NOT NULL,
    actions   JSONB        NOT NULL
);

-- One row per playthrough
CREATE TABLE IF NOT EXISTS runs (
    id            SERIAL PRIMARY KEY,
    player_name   VARCHAR(100) NOT NULL DEFAULT 'Player',
    current_hp    INTEGER      NOT NULL,
    max_hp        INTEGER      NOT NULL DEFAULT 75,
    current_floor INTEGER      NOT NULL DEFAULT 1,
    gold          INTEGER      NOT NULL DEFAULT 100,
    outcome       VARCHAR(20)  DEFAULT 'ongoing'
                               CHECK (outcome IN ('ongoing', 'victory', 'defeat')),
    started_at    TIMESTAMP    DEFAULT NOW()
);

-- Junction table: cards in a run's deck
CREATE TABLE IF NOT EXISTS run_cards (
    id      SERIAL  PRIMARY KEY,
    run_id  INTEGER NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    card_id INTEGER NOT NULL REFERENCES cards(id),
    source  VARCHAR(20) NOT NULL DEFAULT 'starter'
                        CHECK (source IN ('starter', 'reward'))
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_run_cards_run_id  ON run_cards(run_id);
CREATE INDEX IF NOT EXISTS idx_run_cards_card_id ON run_cards(card_id);