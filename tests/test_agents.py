"""Tests for agent components"""

import pytest
from datetime import datetime, timedelta
from src.models.job import Job, JobOperation
from src.agents.plant_agent import PlantAgent, ProductionModel, MachineResource
import simpy


def test_machine_resource_creation():
    """Test machine resource creation"""
    env = simpy.Environment()
    machine = MachineResource(env, "M1", capacity=1)
    assert machine.machine_id == "M1"
    assert machine.total_runtime == 0


def test_job_creation():
    """Test job creation"""
    operations = [
        JobOperation(operation_id=0, machine_id="M1", duration=5),
        JobOperation(operation_id=1, machine_id="M2", duration=3),
    ]
    job = Job(
        job_id="Job_1",
        plant_id="Plant_0",
        operations=operations,
        arrival_time=datetime.now(),
        due_date=datetime.now() + timedelta(hours=2),
        priority=1
    )
    assert job.total_duration == 8
    assert job.num_operations == 2


def test_production_model_creation():
    """Test production model creation"""
    model = ProductionModel(num_plants=2)
    assert len(model.plants) == 2
    assert "Plant_0" in model.plants
    assert "Plant_1" in model.plants


def test_completed_jobs_counting():
    """Test counting of completed jobs"""
    model = ProductionModel(num_plants=1)
    assert model.count_completed_jobs() == 0


def test_simulation_actually_processes_jobs():
    """End-to-end regression test: submitted jobs must be processed and
    completed when the model is run for enough steps. This guards against
    the SimPy clock silently never advancing (model.step() must drive
    self.env forward, not just the Mesa schedule)."""
    model = ProductionModel(num_plants=1)
    plant = model.plants["Plant_0"]
    plant.add_machine("M1", capacity=1)
    plant.add_machine("M2", capacity=1)

    operations = [
        JobOperation(operation_id=0, machine_id="M1", duration=5),
        JobOperation(operation_id=1, machine_id="M2", duration=3),
    ]
    job = Job(
        job_id="Job_test",
        plant_id="Plant_0",
        operations=operations,
        arrival_time=datetime.now(),
        due_date=datetime.now() + timedelta(hours=2),
        priority=1,
    )
    plant.submit_job(job)
    model.run(steps=20)

    assert model.count_completed_jobs() == 1
    assert plant.completed_schedules[0].job_id == "Job_test"


def test_production_model_with_custom_plant_ids():
    """ProductionModel should support explicit plant IDs (e.g. to match
    external/real-world datasets) instead of only the auto-generated
    Plant_0, Plant_1, ... scheme."""
    model = ProductionModel(plant_ids=["Plant_001", "Plant_002"])
    assert set(model.plants.keys()) == {"Plant_001", "Plant_002"}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])