package com.wise.leaderboard.repository;

import com.wise.leaderboard.model.Match;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface MatchRepository extends JpaRepository<Match, Long> {

    List<Match> findByPlayerIdOrderByPlayedAtDesc(Long playerId, Pageable pageable);

    @Query("SELECT m FROM Match m ORDER BY m.score DESC, m.playedAt DESC")
    List<Match> findTopScores(Pageable pageable);

    @Query("SELECT m FROM Match m WHERE m.timeStarted >= :from AND m.timeStarted <= :to ORDER BY m.timeStarted DESC")
    List<Match> findByTimeStartedBetween(LocalDateTime from, LocalDateTime to);

    @Query("SELECT m FROM Match m WHERE m.timeEnded >= :from AND m.timeEnded <= :to ORDER BY m.timeEnded DESC")
    List<Match> findByTimeEndedBetween(LocalDateTime from, LocalDateTime to);
}
