-- Create players table
CREATE TABLE players (
    id BIGINT NOT NULL AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create matches table
CREATE TABLE matches (
    id BIGINT NOT NULL AUTO_INCREMENT,
    player_id BIGINT NOT NULL,
    score INT NOT NULL,
    played_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    difficulty VARCHAR(20),
    time_started TIMESTAMP,
    time_ended TIMESTAMP,
    settings LONGTEXT,
    max_level INT,
    experience_gained BIGINT,
    powerups LONGTEXT,
    feedback_score INT,
    PRIMARY KEY (id),
    KEY idx_player_id (player_id),
    CONSTRAINT fk_matches_player FOREIGN KEY (player_id) REFERENCES players(id),
    CONSTRAINT settings_json_check CHECK (JSON_VALID(settings) OR settings IS NULL),
    CONSTRAINT powerups_json_check CHECK (JSON_VALID(powerups) OR powerups IS NULL)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
