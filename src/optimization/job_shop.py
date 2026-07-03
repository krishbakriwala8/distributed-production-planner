"""OR-Tools based job shop scheduling solver"""

from ortools.sat.python import cp_model
from typing import List, Dict, Optional
from src.models.job import Job
import logging

logger = logging.getLogger(__name__)


class JobShopScheduler:
    """Job shop scheduler using Google OR-Tools"""
    def __init__(self, max_time: int = 10000):
        self.model = cp_model.CpModel()
        self.max_time = max_time
        self.intervals = {}
        self.starts = {}
        self.solver = cp_model.CpSolver()

    def schedule_jobs(self, jobs: List[Job], machines: Dict) -> Optional[Dict]:
        """
        Schedule jobs using constraint programming

        Args:
            jobs: List of Job objects
            machines: Dict of {machine_id: capacity}

        Returns:
            Dict with schedule for each job or None if no solution found
        """
        if not jobs:
            return {}

        logger.info(f"Scheduling {len(jobs)} jobs...")

        # Create variables
        for job in jobs:
            for op_idx, operation in enumerate(job.operations):
                machine_id = operation.machine_id

                start = self.model.NewIntVar(0, self.max_time,
                                            f'start_j{job.job_id}_op{op_idx}')
                end = self.model.NewIntVar(0, self.max_time,
                                          f'end_j{job.job_id}_op{op_idx}')

                # Add constraint: end = start + duration
                self.model.Add(end == start + operation.duration)

                # Store for later
                key = (job.job_id, op_idx)
                self.intervals[key] = self.model.NewIntervalVar(
                    start, operation.duration, end,
                    f'interval_j{job.job_id}_op{op_idx}'
                )
                self.starts[key] = start

        # Add precedence constraints
        for job in jobs:
            for op_idx in range(len(job.operations) - 1):
                key_curr = (job.job_id, op_idx)
                key_next = (job.job_id, op_idx + 1)
                self.model.Add(
                    self.starts[key_next] >= self.starts[key_curr] + job.operations[op_idx].duration
                )

        # Add no-overlap constraints
        machine_intervals = {}
        for job in jobs:
            for op_idx, operation in enumerate(job.operations):
                key = (job.job_id, op_idx)
                machine_id = operation.machine_id
                if machine_id not in machine_intervals:
                    machine_intervals[machine_id] = []
                machine_intervals[machine_id].append(self.intervals[key])

        for machine_intervals_list in machine_intervals.values():
            self.model.AddNoOverlap(machine_intervals_list)

        # Objective: minimize makespan
        makespan = self.model.NewIntVar(0, self.max_time, 'makespan')
        all_ends = []
        for job in jobs:
            job_end = self.model.NewIntVar(0, self.max_time, f'job_end_{job.job_id}')
            last_op_idx = len(job.operations) - 1
            key = (job.job_id, last_op_idx)
            self.model.Add(job_end == self.starts[key] + job.operations[last_op_idx].duration)
            all_ends.append(job_end)

        self.model.AddMaxEquality(makespan, all_ends)
        self.model.Minimize(makespan)

        # Solve
        status = self.solver.Solve(self.model)

        if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            schedule = {}
            for job in jobs:
                schedule[job.job_id] = {}
                for op_idx, operation in enumerate(job.operations):
                    key = (job.job_id, op_idx)
                    schedule[job.job_id][op_idx] = {
                        'start': self.solver.Value(self.starts[key]),
                        'duration': operation.duration,
                        'machine': operation.machine_id
                    }
            logger.info(f"Found schedule with makespan: {self.solver.Value(makespan)}")
            return schedule
        else:
            logger.warning("No feasible schedule found")
            return None