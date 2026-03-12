package com.wise.leaderboard.dto;

import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import lombok.Data;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

@Data
public class CreateMatchRequest {

    @NotNull(message = "Player ID is required")
    private Long playerId;

    @NotNull(message = "Score is required")
    @Positive(message = "Score must be positive")
    private Integer score;

    private String difficulty;

    private LocalDateTime timeStarted;

    private LocalDateTime timeEnded;

    private Map<String, Object> settings;

    @Min(value = 1, message = "Max level must be at least 1")
    private Integer maxLevel;

    @Min(value = 0, message = "Experience gained cannot be negative")
    private Long experienceGained;

    private List<String> powerups;

    @Min(value = 1, message = "Feedback score must be between 1 and 5")
    @Max(value = 5, message = "Feedback score must be between 1 and 5")
    private Integer feedbackScore;
}
