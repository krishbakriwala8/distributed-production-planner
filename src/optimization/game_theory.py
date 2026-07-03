"""Game theory based negotiation and distributed scheduling"""

import nashpy as nash
import numpy as np
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)


class NegotiationProtocol:
    """Game-theoretic negotiation for distributed scheduling"""
    def __init__(self, plants: List[str]):
        self.plants = plants
        self.payoff_matrices = {}

    def compute_nash_equilibrium(self, payoff_a: np.ndarray,
                                 payoff_b: np.ndarray) -> List[Tuple]:
        """
        Compute Nash equilibrium for two agents

        Args:
            payoff_a: Payoff matrix for player A (rows)
            payoff_b: Payoff matrix for player B (columns)

        Returns:
            List of Nash equilibrium mixed strategies
        """
        try:
            game = nash.Game(payoff_a, payoff_b)
            equilibria = list(game.support_enumeration())
            logger.info(f"Found {len(equilibria)} Nash equilibria")
            return equilibria
        except Exception as e:
            logger.error(f"Error computing Nash equilibrium: {e}")
            return []

    def create_scheduling_game(self, plant1_capacity: int,
                               plant2_capacity: int) -> np.ndarray:
        """
        Create payoff matrix for scheduling game
        Strategies: which plant to assign the job to
        Payoff: based on completion time and plant load
        """
        # Simple payoff: negative of expected completion time
        payoff = np.array([
            [-plant1_capacity, -plant2_capacity],  # Assign to plant1
            [-plant1_capacity, -plant2_capacity]   # Assign to plant2
        ])
        return payoff

    def find_best_response(self, my_payoffs: np.ndarray,
                          opponent_strategy: np.ndarray) -> int:
        """Find best response given opponent's mixed strategy"""
        expected_payoffs = my_payoffs @ opponent_strategy
        best_action = np.argmax(expected_payoffs)
        logger.debug(f"Best response: action {best_action} with payoff {expected_payoffs[best_action]}")
        return best_action

    def evaluate_cooperation_potential(self, plant1_jobs: int,
                                      plant2_jobs: int) -> float:
        """
        Evaluate if cooperation is beneficial
        Returns cooperation score (0-1)
        """
        total_jobs = plant1_jobs + plant2_jobs
        if total_jobs == 0:
            return 1.0
        # Cooperation is better when load is unbalanced
        load_difference = abs(plant1_jobs - plant2_jobs) / total_jobs
        return load_difference