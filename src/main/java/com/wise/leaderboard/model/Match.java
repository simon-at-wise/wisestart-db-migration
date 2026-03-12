package com.wise.leaderboard.model;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

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

    @Column(length = 20)
    private String difficulty;

    @Column(name = "time_started")
    private LocalDateTime timeStarted;

    @Column(name = "time_ended")
    private LocalDateTime timeEnded;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(columnDefinition = "longtext")
    private Map<String, Object> settings;

    @Column(name = "max_level")
    private Integer maxLevel;

    @Column(name = "experience_gained")
    private Long experienceGained;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(columnDefinition = "longtext")
    private List<String> powerups;

    @Column(name = "feedback_score")
    private Integer feedbackScore;

    @PrePersist
    protected void onCreate() {
        if (playedAt == null) {
            playedAt = LocalDateTime.now();
        }
    }
}
