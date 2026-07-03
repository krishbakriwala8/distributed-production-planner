"""Production plant model"""

from dataclasses import dataclass, field
from typing import Dict, Any, List
from datetime import datetime


@dataclass
class Plant:
    """Represents a production plant/factory"""
    plant_id: str
    plant_name: str
    location: str
    country: str = "Germany"
    max_capacity: int = 100  # jobs per day
    operating_days_per_week: int = 5
    work_shift_hours: int = 8
    timezone: str = "Europe/Berlin"
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if self.max_capacity < 1:
            raise ValueError("Max capacity must be at least 1")
        if not (1 <= self.operating_days_per_week <= 7):
            raise ValueError("Operating days must be between 1 and 7")