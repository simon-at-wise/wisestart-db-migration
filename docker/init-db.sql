-- Grant additional privileges to leaderboard_user for bulk operations
GRANT BINLOG ADMIN ON *.* TO 'leaderboard_user'@'%';
FLUSH PRIVILEGES;
