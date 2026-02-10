package com.wise.leaderboard.controller;

import com.wise.leaderboard.dto.CreatePlayerRequest;
import com.wise.leaderboard.model.Player;
import com.wise.leaderboard.repository.PlayerRepository;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/players")
public class PlayerController {

    private final PlayerRepository playerRepository;

    public PlayerController(PlayerRepository playerRepository) {
        this.playerRepository = playerRepository;
    }

    @GetMapping
    public List<Player> getAllPlayers() {
        return playerRepository.findAll();
    }

    @GetMapping("/{id}")
    public ResponseEntity<Player> getPlayerById(@PathVariable Long id) {
        return playerRepository.findById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping
    public ResponseEntity<Player> createPlayer(@Valid @RequestBody CreatePlayerRequest request) {
        Player player = new Player();
        player.setUsername(request.getUsername());
        // TODO: Exercise 1 - uncomment this
        //player.setEmail(request.getEmail());

        Player saved = playerRepository.save(player);
        return ResponseEntity.status(HttpStatus.CREATED).body(saved);
    }
}
