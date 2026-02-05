-- BROKEN: Missing foreign key constraint on player_id
-- This will allow orphaned achievement records

CREATE TABLE achievements (
    achievement_id BIGSERIAL PRIMARY KEY,
    player_id BIGINT NOT NULL,
    achievement_type VARCHAR(50) NOT NULL,
    achieved_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

CREATE INDEX idx_achievements_player ON achievements(player_id);
