package com.wise.leaderboard.controller;

import com.wise.leaderboard.dto.CreateMatchRequest;
import com.wise.leaderboard.model.Match;
import com.wise.leaderboard.repository.MatchRepository;
import jakarta.validation.Valid;
import org.springframework.data.domain.PageRequest;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;

@RestController
@RequestMapping("/matches")
public class MatchController {

    private final MatchRepository matchRepository;

    public MatchController(MatchRepository matchRepository) {
        this.matchRepository = matchRepository;
    }

    @GetMapping
    public List<Match> getRecentMatches(@RequestParam(defaultValue = "20") int limit) {
        return matchRepository.findAll(PageRequest.of(0, limit)).getContent();
    }

    @GetMapping("/leaderboard")
    public List<Match> getLeaderboard(@RequestParam(defaultValue = "10") int limit) {
        return matchRepository.findTopScores(PageRequest.of(0, limit));
    }

    @GetMapping("/by-time-started")
    public List<Match> findByTimeStarted(
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime from,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime to) {
        return matchRepository.findByTimeStartedBetween(from, to);
    }

    @GetMapping("/by-time-ended")
    public List<Match> findByTimeEnded(
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime from,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime to) {
        return matchRepository.findByTimeEndedBetween(from, to);
    }

    @GetMapping("/top-scores")
    public List<Match> getTopScores(@RequestParam(defaultValue = "10") int limit) {
        return matchRepository.findTopScores(PageRequest.of(0, limit));
    }

    @PostMapping
    public ResponseEntity<Match> createMatch(@Valid @RequestBody CreateMatchRequest request) {
        Match match = new Match();
        match.setPlayerId(request.getPlayerId());
        match.setScore(request.getScore());
        match.setDifficulty(request.getDifficulty());
        match.setTimeStarted(request.getTimeStarted());
        match.setTimeEnded(request.getTimeEnded());
        match.setSettings(request.getSettings());
        match.setMaxLevel(request.getMaxLevel());
        match.setExperienceGained(request.getExperienceGained());
        match.setPowerups(request.getPowerups());
        match.setFeedbackScore(request.getFeedbackScore());

        Match saved = matchRepository.save(match);
        return ResponseEntity.status(HttpStatus.CREATED).body(saved);
    }
}
