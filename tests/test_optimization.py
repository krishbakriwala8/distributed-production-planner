"""Tests for optimization components"""

import pytest
import numpy as np
from src.optimization.job_shop import JobShopScheduler
from src.optimization.game_theory import NegotiationProtocol
from src.models.job import Job, JobOperation
from datetime import datetime, timedelta


def test_job_shop_scheduler_empty():
    """Test scheduler with no jobs"""
    scheduler = JobShopScheduler()
    result = scheduler.schedule_jobs([], {})
    assert result == {}


def test_job_shop_scheduler_single_job():
    """Test scheduler with single job"""
    scheduler = JobShopScheduler()
    operations = [
        JobOperation(operation_id=0, machine_id="M1", duration=5),
    ]
    job = Job(
        job_id="Job_1",
        plant_id="Plant_0",
        operations=operations,
        arrival_time=datetime.now(),
        due_date=datetime.now() + timedelta(hours=2),
    )
    result = scheduler.schedule_jobs([job], {"M1": 1})
    assert result is not None
    assert "Job_1" in result


def test_negotiation_protocol_creation():
    """Test negotiation protocol creation"""
    protocol = NegotiationProtocol(plants=["Plant_0", "Plant_1"])
    assert len(protocol.plants) == 2


def test_nash_equilibrium_computation():
    """Test Nash equilibrium computation"""
    protocol = NegotiationProtocol(plants=["Plant_0", "Plant_1"])
    payoff_a = np.array([[1, 0], [0, 1]])
    payoff_b = np.array([[1, 0], [0, 1]])
    equilibria = protocol.compute_nash_equilibrium(payoff_a, payoff_b)
    assert isinstance(equilibria, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])