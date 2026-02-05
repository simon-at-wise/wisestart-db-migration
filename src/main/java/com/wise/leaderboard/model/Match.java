package com.wise.leaderboard.model;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Table(name = "matches")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Match {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotNull
    @Column(name = "player_id", nullable = false)
    private Long playerId;

    @NotNull
    @Column(nullable = false)
    private Integer score;

    @Column(name = "played_at", nullable = false)
    private LocalDateTime playedAt;

    @PrePersist
    protected void onCreate() {
        playedAt = LocalDateTime.now();
    }
}
