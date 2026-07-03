"""API routes"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from src.optimization.job_shop import JobShopScheduler
from src.models.job import Job, JobOperation
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["production"])


class OperationRequest(BaseModel):
    operation_id: int
    machine_id: str
    duration: int
    setup_time: int = 0


class JobRequest(BaseModel):
    job_id: str
    plant_id: str
    operations: List[dict]
    arrival_time: str
    due_date: str
    priority: int = 1


class ScheduleResponse(BaseModel):
    status: str
    message: str
    schedule: Optional[dict] = None


@router.post("/schedule", response_model=ScheduleResponse)
async def schedule_job(job: JobRequest):
    """Schedule a new job"""
    try:
        # Convert request to Job object
        operations = [
            JobOperation(
                operation_id=i,
                machine_id=op['machine_id'],
                duration=op['duration']
            )
            for i, op in enumerate(job.operations)
        ]

        job_obj = Job(
            job_id=job.job_id,
            plant_id=job.plant_id,
            operations=operations,
            arrival_time=datetime.fromisoformat(job.arrival_time),
            due_date=datetime.fromisoformat(job.due_date),
            priority=job.priority
        )

        # Schedule
        scheduler = JobShopScheduler()
        schedule = scheduler.schedule_jobs([job_obj], {})

        if schedule:
            return ScheduleResponse(
                status="success",
                message="Job scheduled successfully",
                schedule=schedule
            )
        else:
            return ScheduleResponse(
                status="failed",
                message="No feasible schedule found"
            )
    except Exception as e:
        logger.error(f"Error scheduling job: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/status")
async def get_status():
    """Get system status"""
    return {
        "status": "running",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}