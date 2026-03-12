-- Insert 10 initial players
INSERT INTO players (username, created_at) VALUES
('alice_gamer', '2024-01-15 10:00:00'),
('bob_pro', '2024-01-16 11:30:00'),
('charlie_plays', '2024-01-17 09:15:00'),
('diana_wins', '2024-01-18 14:20:00'),
('eve_master', '2024-01-19 16:45:00'),
('frank_ninja', '2024-01-20 08:00:00'),
('grace_legend', '2024-01-21 12:30:00'),
('hank_elite', '2024-01-22 15:00:00'),
('iris_champ', '2024-01-23 10:45:00'),
('jack_ace', '2024-01-24 13:15:00');

-- Insert 20 match records
INSERT INTO matches (player_id, score, played_at, difficulty, time_started, time_ended, settings, max_level, experience_gained, powerups, feedback_score) VALUES
(1, 1500, '2024-01-25 10:00:00', 'easy', '2024-01-25 09:45:00', '2024-01-25 10:00:00', '{"sound": true, "music": true, "hints": true}', 5, 150, '["shield", "time_freeze"]', 4),
(2, 2300, '2024-01-25 10:15:00', 'hard', '2024-01-25 09:55:00', '2024-01-25 10:15:00', '{"sound": true, "music": false, "hints": false}', 8, 460, '["double_points", "extra_life", "speed_boost"]', 5),
(3, 1800, '2024-01-25 10:30:00', 'medium', '2024-01-25 10:10:00', '2024-01-25 10:30:00', '{"sound": false, "music": true, "hints": true}', 6, 270, '["shield", "bomb"]', 3),
(4, 2100, '2024-01-25 10:45:00', 'medium', '2024-01-25 10:20:00', '2024-01-25 10:45:00', '{"sound": true, "music": true, "hints": false}', 7, 315, '["time_freeze", "extra_life"]', 5),
(5, 2500, '2024-01-25 11:00:00', 'hard', '2024-01-25 10:35:00', '2024-01-25 11:00:00', '{"sound": true, "music": true, "hints": false}', 9, 625, '["double_points", "shield", "speed_boost"]', 5),
(1, 1700, '2024-01-25 11:15:00', 'easy', '2024-01-25 11:00:00', '2024-01-25 11:15:00', '{"sound": true, "music": true, "hints": true}', 6, 170, '["shield", "time_freeze", "extra_life"]', 4),
(2, 2400, '2024-01-25 11:30:00', 'hard', '2024-01-25 11:05:00', '2024-01-25 11:30:00', '{"sound": true, "music": false, "hints": false}', 9, 600, '["double_points", "bomb", "speed_boost"]', 5),
(3, 1900, '2024-01-25 11:45:00', 'medium', '2024-01-25 11:25:00', '2024-01-25 11:45:00', '{"sound": false, "music": true, "hints": true}', 7, 285, '["shield", "extra_life"]', 4),
(4, 2200, '2024-01-25 12:00:00', 'hard', '2024-01-25 11:35:00', '2024-01-25 12:00:00', '{"sound": true, "music": true, "hints": false}', 8, 440, '["time_freeze", "double_points"]', 5),
(5, 2600, '2024-01-25 12:15:00', 'hard', '2024-01-25 11:50:00', '2024-01-25 12:15:00', '{"sound": true, "music": true, "hints": false}', 10, 780, '["double_points", "shield", "speed_boost", "extra_life"]', 5),
(6, 1600, '2024-01-25 12:30:00', 'easy', '2024-01-25 12:15:00', '2024-01-25 12:30:00', '{"sound": true, "music": false, "hints": true}', 5, 160, '["shield", "bomb"]', 3),
(7, 2000, '2024-01-25 12:45:00', 'medium', '2024-01-25 12:25:00', '2024-01-25 12:45:00', '{"sound": true, "music": true, "hints": true}', 7, 300, '["time_freeze", "extra_life", "shield"]', 4),
(8, 2300, '2024-01-25 13:00:00', 'hard', '2024-01-25 12:40:00', '2024-01-25 13:00:00', '{"sound": false, "music": true, "hints": false}', 8, 460, '["double_points", "speed_boost"]', 4),
(9, 1400, '2024-01-25 13:15:00', 'easy', '2024-01-25 13:00:00', '2024-01-25 13:15:00', '{"sound": true, "music": true, "hints": true}', 4, 140, '["shield"]', 3),
(10, 1950, '2024-01-25 13:30:00', 'medium', '2024-01-25 13:10:00', '2024-01-25 13:30:00', '{"sound": true, "music": false, "hints": false}', 7, 293, '["time_freeze", "bomb", "extra_life"]', 4),
(6, 1750, '2024-01-25 13:45:00', 'medium', '2024-01-25 13:25:00', '2024-01-25 13:45:00', '{"sound": true, "music": true, "hints": true}', 6, 263, '["shield", "extra_life"]', 4),
(7, 2100, '2024-01-25 14:00:00', 'hard', '2024-01-25 13:40:00', '2024-01-25 14:00:00', '{"sound": true, "music": true, "hints": false}', 8, 420, '["double_points", "time_freeze", "speed_boost"]', 5),
(8, 2450, '2024-01-25 14:15:00', 'hard', '2024-01-25 13:50:00', '2024-01-25 14:15:00', '{"sound": false, "music": true, "hints": false}', 9, 613, '["double_points", "shield", "extra_life"]', 5),
(9, 1550, '2024-01-25 14:30:00', 'easy', '2024-01-25 14:15:00', '2024-01-25 14:30:00', '{"sound": true, "music": true, "hints": true}', 5, 155, '["shield", "time_freeze"]', 4),
(10, 2050, '2024-01-25 14:45:00', 'medium', '2024-01-25 14:25:00', '2024-01-25 14:45:00', '{"sound": true, "music": false, "hints": false}', 7, 308, '["bomb", "extra_life", "speed_boost"]', 4);
