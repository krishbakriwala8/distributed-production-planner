"""Simple end-to-end example"""

import sys
sys.path.insert(0, '..')

from datetime import datetime, timedelta
from src.models.job import Job, JobOperation
from src.agents.plant_agent import ProductionModel
from src.optimization.job_shop import JobShopScheduler
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    print("\n" + "=" * 60)
    print("Distributed Production Planning - Simple Example")
    print("=" * 60)

    # Create sample jobs
    jobs = []
    for i in range(5):
        operations = [
            JobOperation(operation_id=0, machine_id="M1", duration=5),
            JobOperation(operation_id=1, machine_id="M2", duration=3),
        ]
        job = Job(
            job_id=f"Job_{i}",
            plant_id="Plant_0",
            operations=operations,
            arrival_time=datetime.now(),
            due_date=datetime.now() + timedelta(hours=2),
            priority=1
        )
        jobs.append(job)

    # --- Option 1: OR-Tools Scheduling ---
    print("\n1️⃣ USING OR-TOOLS SOLVER:")
    print("-" * 60)
    scheduler = JobShopScheduler(max_time=1000)
    machines = {"M1": 1, "M2": 1}
    schedule = scheduler.schedule_jobs(jobs, machines)

    if schedule:
        print("✅ Schedule found!")
        for job_id, job_schedule in schedule.items():
            print(f"\n  {job_id}:")
            for op_id, details in job_schedule.items():
                print(f"    Op {op_id}: Start={details['start']}, "
                      f"Duration={details['duration']}, Machine={details['machine']}")
    else:
        print("❌ No feasible schedule found")

    # --- Option 2: Simulation-Based Scheduling ---
    print("\n2️⃣ USING MESA + SIMPY SIMULATION:")
    print("-" * 60)
    model = ProductionModel(num_plants=1)

    # Add machines
    for plant in model.plants.values():
        plant.add_machine("M1", capacity=1)
        plant.add_machine("M2", capacity=1)

    # Submit jobs
    for job in jobs:
        plant = model.plants["Plant_0"]
        plant.submit_job(job)

    # Run simulation
    model.run(steps=500)

    print(f"✅ Simulation completed!")
    print(f"  Total completed jobs: {model.count_completed_jobs()}")
    print(f"  Average tardiness: {model.avg_tardiness():.2f}")

    # Print schedules
    for plant_id, plant in model.plants.items():
        print(f"\n  {plant_id} completed schedules:")
        for schedule in plant.completed_schedules[:3]:  # Show first 3
            print(f"    {schedule.job_id}: Completion time = {schedule.completion_time}")

    print("\n" + "=" * 60)
    print("✨ Example completed successfully!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()