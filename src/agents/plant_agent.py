"""Production plant agent using Mesa and SimPy"""

from mesa import Agent, Model
from mesa.time import SimultaneousActivation
from mesa.datacollection import DataCollector
import simpy
from typing import Dict, List, Optional
from datetime import datetime
import logging

from src.models.job import Job, Schedule
from src.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class MachineResource:
    """Wrapper for SimPy machine resource"""
    def __init__(self, env, machine_id: str, capacity: int = 1):
        self.machine = simpy.Resource(env, capacity=capacity)
        self.machine_id = machine_id
        self.env = env
        self.jobs_processed = []
        self.total_runtime = 0


class PlantAgent(BaseAgent):
    """Production plant agent managing machines and job scheduling"""
    def __init__(self, unique_id, model, env, plant_name: str):
        super().__init__(unique_id, model, "plant")
        self.env = env
        self.plant_name = plant_name
        self.machines: Dict[str, MachineResource] = {}
        self.job_queue: List[Job] = []
        self.active_jobs = []
        self.completed_schedules: List[Schedule] = []
        self.total_jobs_processed = 0
        self.total_tardiness = 0

    def add_machine(self, machine_id: str, capacity: int = 1):
        """Add a machine to this plant"""
        self.machines[machine_id] = MachineResource(self.env, machine_id, capacity)
        logger.debug(f"Plant {self.plant_name}: Added machine {machine_id}")

    def submit_job(self, job: Job):
        """Receive a job for scheduling"""
        self.job_queue.append(job)
        self.active_jobs.append(job)
        self.env.process(self.process_job(job))
        logger.info(f"Plant {self.plant_name}: Received job {job.job_id}")

    def process_job(self, job: Job):
        """SimPy process to execute job through all operations"""
        job_start = self.env.now
        current_time = job_start
        machine_schedule = {}

        try:
            for op in job.operations:
                if op.machine_id not in self.machines:
                    logger.warning(f"Machine {op.machine_id} not found in plant {self.plant_name}")
                    continue

                machine = self.machines[op.machine_id]

                # Request machine resource
                with machine.machine.request() as req:
                    yield req
                    op_start = self.env.now
                    yield self.env.timeout(op.duration)
                    op_end = self.env.now
                    machine_schedule[op.operation_id] = {
                        'start': op_start,
                        'end': op_end,
                        'duration': op.duration,
                        'machine': op.machine_id
                    }
                    machine.total_runtime += op.duration

            job_end = self.env.now
            due_date_sim_time = (job.due_date - job.arrival_time).total_seconds()
            tardiness = max(0, int(job_end - due_date_sim_time))

            schedule = Schedule(
                job_id=job.job_id,
                plant_id=self.plant_name,
                start_time=int(job_start),
                end_time=int(job_end),
                machine_assignments=machine_schedule,
                tardiness=tardiness,
                completion_time=int(job_end - job_start),
                status="completed"
            )

            self.completed_schedules.append(schedule)
            self.total_jobs_processed += 1
            self.total_tardiness += tardiness

            if job in self.active_jobs:
                self.active_jobs.remove(job)

            logger.info(f"Plant {self.plant_name}: Completed job {job.job_id} "
                       f"(tardiness: {tardiness})")

        except Exception as e:
            logger.error(f"Error processing job {job.job_id}: {e}")

    def get_utilization(self) -> float:
        """Get machine utilization percentage"""
        if not self.machines:
            return 0.0
        total_possible_time = sum(m.total_runtime * 100 / max(self.env.now, 1)
                                  for m in self.machines.values())
        return total_possible_time / len(self.machines)

    def step(self):
        """Mesa step for dynamic operations"""
        super().step()
        self.update_metrics("jobs_completed", self.total_jobs_processed)
        self.update_metrics("avg_tardiness", self.total_tardiness / max(1, self.total_jobs_processed))


class ProductionModel(Model):
    """Main simulation model coordinating multiple plants"""
    def __init__(self, num_plants: int = 2, random_seed: int = 42,
                 plant_ids: Optional[List[str]] = None):
        """
        Args:
            num_plants: Number of plants to auto-generate (ignored if
                plant_ids is provided).
            random_seed: Seed for reproducibility.
            plant_ids: Optional explicit list of plant IDs to use (e.g.
                real-world IDs like "Plant_001"). Lets callers line up
                plant identifiers with external datasets instead of being
                forced into the auto-generated "Plant_0", "Plant_1", ...
                scheme.
        """
        super().__init__()
        ids = plant_ids if plant_ids else [f"Plant_{i}" for i in range(num_plants)]
        self.num_plants = len(ids)
        self.env = simpy.Environment()
        self.schedule = SimultaneousActivation(self)
        self.plants: Dict[str, PlantAgent] = {}
        self.random.seed(random_seed) if random_seed else None

        # Create plants
        for i, plant_id in enumerate(ids):
            plant = PlantAgent(i, self, self.env, plant_id)
            self.plants[plant_id] = plant
            self.schedule.add(plant)

        # Data collection
        self.datacollector = DataCollector(
            model_reporters={
                "Completed_Jobs": self.count_completed_jobs,
                "Avg_Tardiness": self.avg_tardiness,
                "Utilization": self.avg_utilization
            }
        )

    def count_completed_jobs(self) -> int:
        """Count total completed jobs across all plants"""
        total = sum(len(p.completed_schedules) for p in self.plants.values())
        return total

    def avg_tardiness(self) -> float:
        """Calculate average tardiness across all completed jobs"""
        all_schedules = []
        for plant in self.plants.values():
            all_schedules.extend(plant.completed_schedules)
        if not all_schedules:
            return 0.0
        return sum(s.tardiness for s in all_schedules) / len(all_schedules)

    def avg_utilization(self) -> float:
        """Calculate average machine utilization"""
        if not self.plants:
            return 0.0
        utilizations = [p.get_utilization() for p in self.plants.values()]
        return sum(utilizations) / len(utilizations) if utilizations else 0.0

    def step(self):
        """Single step of simulation"""
        self.schedule.step()
        # Advance the underlying SimPy clock by one time unit so that job
        # processes (created via env.process in submit_job) actually run.
        # Without this, self.env.now never moves and every SimPy generator
        # stays parked on its first `yield` forever, so no job completes.
        self.env.run(until=self.env.now + 1)
        self.datacollector.collect(self)

    def run(self, steps: int = 100):
        """Run simulation for specified number of steps"""
        logger.info(f"Starting simulation for {steps} steps")
        for _ in range(steps):
            self.step()
        logger.info(f"Simulation completed. Total jobs: {self.count_completed_jobs()}")