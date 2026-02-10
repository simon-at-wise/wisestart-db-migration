package com.wise.leaderboard.dto;

import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import lombok.Data;

@Data
public class CreateMatchRequest {

    @NotNull(message = "Player ID is required")
    private Long playerId;

    @NotNull(message = "Score is required")
    @Positive(message = "Score must be positive")
    private Integer score;
}
