"""Job agent representing production orders"""

from src.agents.base_agent import BaseAgent
from src.models.job import Job
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class JobAgent(BaseAgent):
    """Agent representing a production job"""
    def __init__(self, unique_id: str, model, job: Job):
        super().__init__(unique_id, model, "job")
        self.job = job
        self.assigned_plant: Optional[str] = None
        self.assigned_time: Optional[int] = None
        self.completion_time: Optional[int] = None
        self.status = "unassigned"

    def assign_to_plant(self, plant_id: str, start_time: int):
        """Assign job to a specific plant at given time"""
        self.assigned_plant = plant_id
        self.assigned_time = start_time
        self.status = "assigned"
        logger.info(f"Job {self.unique_id} assigned to {plant_id} at time {start_time}")

    def mark_completed(self, completion_time: int, tardiness: int):
        """Mark job as completed"""
        self.completion_time = completion_time
        self.status = "completed"
        self.update_metrics("tardiness", tardiness)
        logger.info(f"Job {self.unique_id} completed at {completion_time} (tardiness: {tardiness})")

    def step(self):
        """Job agent step"""
        super().step()
        # Jobs are passive agents - they don't take actions
        pass