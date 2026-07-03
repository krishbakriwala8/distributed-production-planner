"""Production simulation executor"""

from src.agents.plant_agent import ProductionModel
from src.models.job import Job, JobOperation
from datetime import datetime, timedelta
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


def run_simulation(num_plants: int = 2, num_jobs: int = 10,
                   num_steps: int = 100) -> Dict:
    """
    Run a complete production simulation

    Args:
        num_plants: Number of production plants
        num_jobs: Number of jobs to schedule
        num_steps: Number of simulation steps

    Returns:
        Results dictionary with KPIs and schedules
    """
    logger.info(f"Starting simulation: {num_plants} plants, {num_jobs} jobs, {num_steps} steps")

    # Create model
    model = ProductionModel(num_plants=num_plants)

    # Add machines to each plant
    for plant in model.plants.values():
        plant.add_machine("M1", capacity=1)
        plant.add_machine("M2", capacity=1)
        plant.add_machine("M3", capacity=1)

    # Create and submit jobs
    for i in range(num_jobs):
        operations = [
            JobOperation(operation_id=0, machine_id="M1", duration=5),
            JobOperation(operation_id=1, machine_id="M2", duration=3),
            JobOperation(operation_id=2, machine_id="M3", duration=4),
        ]
        job = Job(
            job_id=f"Job_{i}",
            plant_id="Plant_0",
            operations=operations,
            arrival_time=datetime.now(),
            due_date=datetime.now() + timedelta(hours=2),
            priority=1 + (i % 3)
        )
        model.plants["Plant_0"].submit_job(job)

    # Run simulation
    model.run(steps=num_steps)

    # Collect results
    results = {
        "total_jobs_completed": model.count_completed_jobs(),
        "avg_tardiness": model.avg_tardiness(),
        "avg_utilization": model.avg_utilization(),
        "plant_schedules": {}
    }

    for plant_id, plant in model.plants.items():
        results["plant_schedules"][plant_id] = {
            "jobs_completed": len(plant.completed_schedules),
            "total_tardiness": plant.total_tardiness,
            "avg_tardiness": plant.total_tardiness / max(1, plant.total_jobs_processed),
            "utilization": plant.get_utilization()
        }

    logger.info(f"Simulation complete. Results: {results}")
    return results