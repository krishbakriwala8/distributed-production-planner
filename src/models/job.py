"""Job and operation data models"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any
import uuid


@dataclass
class JobOperation:
    """Represents a single operation in a job"""
    operation_id: int
    machine_id: str
    duration: int  # minutes
    setup_time: int = 0
    skill_required: str = ""

    def __post_init__(self):
        if self.duration <= 0:
            raise ValueError("Duration must be positive")


@dataclass
class Job:
    """Represents a production job/order"""
    job_id: str
    plant_id: str
    operations: List[JobOperation]
    arrival_time: datetime
    due_date: datetime
    priority: int = 1
    quantity: int = 1
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.due_date < self.arrival_time:
            raise ValueError("Due date must be after arrival time")
        if not self.operations:
            raise ValueError("Job must have at least one operation")
        if self.priority < 1:
            raise ValueError("Priority must be positive")

    @property
    def total_duration(self) -> int:
        """Total processing time needed"""
        return sum(op.duration for op in self.operations)

    @property
    def num_operations(self) -> int:
        """Number of operations in job"""
        return len(self.operations)


@dataclass
class Schedule:
    """Output schedule for a completed job"""
    job_id: str
    plant_id: str
    start_time: int
    end_time: int
    machine_assignments: Dict[int, Dict[str, Any]]
    tardiness: int = 0
    completion_time: int = 0
    status: str = "completed"
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def makespan(self) -> int:
        """Total time from start to end"""
        return self.end_time - self.start_time

    @property
    def is_on_time(self) -> bool:
        """Whether job completed before or on due date"""
        return self.tardiness <= 0