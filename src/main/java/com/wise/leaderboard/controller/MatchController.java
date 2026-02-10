package com.wise.leaderboard.controller;

import com.wise.leaderboard.dto.CreateMatchRequest;
import com.wise.leaderboard.model.Match;
import com.wise.leaderboard.repository.MatchRepository;
import jakarta.validation.Valid;
import org.springframework.data.domain.PageRequest;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

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

    @PostMapping
    public ResponseEntity<Match> createMatch(@Valid @RequestBody CreateMatchRequest request) {
        Match match = new Match();
        match.setPlayerId(request.getPlayerId());
        match.setScore(request.getScore());

        Match saved = matchRepository.save(match);
        return ResponseEntity.status(HttpStatus.CREATED).body(saved);
    }
}
