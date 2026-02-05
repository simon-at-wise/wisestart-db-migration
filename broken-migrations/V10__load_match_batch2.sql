-- BROKEN: References non-existent player_id = 999
-- This will fail due to foreign key constraint violation

INSERT INTO matches (player_id, match_date, score, opponent, result) VALUES
(999, '2024-02-01', 2100, 'GhostPlayer', 'WIN'),
(1, '2024-02-01', 1950, 'Player2', 'LOSS'),
(2, '2024-02-02', 2050, 'Player3', 'WIN');
