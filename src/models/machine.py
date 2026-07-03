"""Machine resource model"""

from dataclasses import dataclass, field
from typing import Dict, Any, List
from datetime import datetime


@dataclass
class Machine:
    """Represents a production machine/resource"""
    machine_id: str
    plant_id: str
    machine_type: str
    capacity: int = 1
    operating_hours_per_day: int = 8
    setup_time: int = 0  # minutes
    cost_per_hour: float = 100.0
    efficiency: float = 1.0  # 0.0 to 1.0
    skills: List[str] = field(default_factory=list)
    available: bool = True
    maintenance_schedule: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if self.capacity < 1:
            raise ValueError("Capacity must be at least 1")
        if not (0.0 < self.efficiency <= 1.0):
            raise ValueError("Efficiency must be between 0 and 1")

    @property
    def is_available(self) -> bool:
        """Check if machine is available for operations"""
        return self.available

    def get_effective_duration(self, duration: int) -> int:
        """Calculate effective duration considering efficiency"""
        return int(duration / self.efficiency)