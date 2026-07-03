"""Example using real manufacturing data"""

import sys
sys.path.insert(0, '..')

import json
from datetime import datetime, timedelta
from pathlib import Path
from src.models.job import Job, JobOperation
from src.agents.plant_agent import ProductionModel
from src.optimization.job_shop import JobShopScheduler
from src.simulation.metrics import PerformanceMetrics
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_real_data():
    """Load real manufacturing data from JSON files"""
    data_dir = Path(__file__).parent.parent / 'data'
    
    with open(data_dir / 'plants_data.json', 'r') as f:
        plants_data = json.load(f)
    
    with open(data_dir / 'jobs_data.json', 'r') as f:
        jobs_data = json.load(f)
    
    with open(data_dir / 'machines_data.json', 'r') as f:
        machines_data = json.load(f)
    
    return plants_data, jobs_data, machines_data


def convert_to_job_objects(jobs_data):
    """Convert JSON job data to Job objects"""
    jobs = []
    for job_dict in jobs_data['jobs']:
        operations = [
            JobOperation(
                operation_id=op['op_id'],
                machine_id=op['machine_id'],
                duration=op['duration']
            )
            for op in job_dict['operations']
        ]
        
        job = Job(
            job_id=job_dict['job_id'],
            plant_id=job_dict['plant_id'],
            operations=operations,
            arrival_time=datetime.fromisoformat(job_dict['arrival_time']),
            due_date=datetime.fromisoformat(job_dict['due_date']),
            priority=job_dict['priority'],
            metadata={'vehicle_model': job_dict.get('vehicle_model', 'Unknown')}
        )
        jobs.append(job)
    
    return jobs


def main():
    print("\n" + "="*70)
    print("Real Manufacturing Data - Distributed Production Scheduling")
    print("="*70)
    
    # Load real data
    print("\n📊 Loading real manufacturing data...")
    plants_data, jobs_data, machines_data = load_real_data()
    
    # Display plant information
    print("\n🏢 PRODUCTION PLANTS:")
    print("-" * 70)
    for plant in plants_data['plants']:
        print(f"\n  {plant['plant_name']}")
        print(f"    Location: {plant['location']}")
        print(f"    Capacity: {plant['max_capacity']} jobs/day")
        print(f"    Machines: {len(plant['machines'])}")
        print(f"    Efficiency Rating: {plant['efficiency_rating']:.1%}")
        print(f"    Description: {plant['notes']}")
    
    # Display machine information
    print("\n🔧 PRODUCTION MACHINES:")
    print("-" * 70)
    machine_types = {}
    for machine in machines_data['machines']:
        mtype = machine['machine_type']
        if mtype not in machine_types:
            machine_types[mtype] = []
        machine_types[mtype].append(machine['machine_name'])
    
    for mtype, machines in machine_types.items():
        print(f"\n  {mtype} Stations: {len(machines)}")
        for m in machines:
            print(f"    - {m}")
    
    # Display job information
    print("\n📋 PRODUCTION JOBS:")
    print("-" * 70)
    jobs = convert_to_job_objects(jobs_data)
    print(f"Total Jobs: {len(jobs)}")
    print(f"Job Types: {len(set(j.metadata['vehicle_model'] for j in jobs))}")
    print(f"Average Operations per Job: {jobs_data['metadata']['avg_operations_per_job']}")
    print(f"\nSample Jobs:")
    for job in jobs[:5]:
        print(f"\n  {job.job_id}")
        print(f"    Model: {job.metadata['vehicle_model']}")
        print(f"    Plant: {job.plant_id}")
        print(f"    Arrival: {job.arrival_time.strftime('%Y-%m-%d %H:%M')}")
        print(f"    Due Date: {job.due_date.strftime('%Y-%m-%d %H:%M')}")
        print(f"    Priority: {job.priority}")
        print(f"    Total Duration: {job.total_duration} min")
        print(f"    Operations: {job.num_operations}")
    
    # --- Option 1: OR-Tools Scheduling with Real Data ---
    print("\n\n1️⃣ CONSTRAINT PROGRAMMING SCHEDULING (OR-Tools):")
    print("="*70)
    scheduler = JobShopScheduler(max_time=5000)
    schedule = scheduler.schedule_jobs(jobs, {})
    
    if schedule:
        print("\n✅ Schedule found!")
        print("\nTop 5 Jobs Schedule:")
        for i, (job_id, job_schedule) in enumerate(list(schedule.items())[:5]):
            job = next(j for j in jobs if j.job_id == job_id)
            print(f"\n  {job_id} ({job.metadata['vehicle_model']}):")
            total_time = 0
            for op_id, details in job_schedule.items():
                total_time = max(total_time, details['start'] + details['duration'])
                print(f"    Op {op_id}: {details['machine']} | "
                      f"Start: {details['start']:4d} | "
                      f"Duration: {details['duration']:3d} min")
            print(f"    Total Completion: {total_time} min")
    else:
        print("\n❌ No feasible schedule found")
    
    # --- Option 2: Multi-Agent Simulation with Real Data ---
    print("\n\n2️⃣ MULTI-AGENT SIMULATION (Mesa + SimPy):")
    print("="*70)
    
    # Create production model using the real plant IDs from plants_data.json
    # (rather than the model's default "Plant_0"/"Plant_1"/... scheme), so
    # machines and jobs keyed by real plant IDs (e.g. "Plant_001") line up.
    real_plant_ids = [p['plant_id'] for p in plants_data['plants']]
    model = ProductionModel(plant_ids=real_plant_ids)
    
    # Add machines from real data
    print("\n🏗️ Setting up production facilities...")
    for machine in machines_data['machines']:
        plant_id = machine['plant_id']
        if plant_id in model.plants:
            plant = model.plants[plant_id]
            plant.add_machine(machine['machine_id'], capacity=1)
            print(f"  Added {machine['machine_id']} to {plant_id}")
    
    # Submit jobs
    print("\n📥 Submitting jobs to production plants...")
    jobs_by_plant = {}
    for job in jobs:
        plant_id = job.plant_id
        if plant_id in model.plants:
            jobs_by_plant[plant_id] = jobs_by_plant.get(plant_id, 0) + 1
            plant = model.plants[plant_id]
            plant.submit_job(job)
    
    for plant_id, count in jobs_by_plant.items():
        print(f"  {plant_id}: {count} jobs submitted")
    
    # Run simulation
    print("\n▶️ Running simulation (500 time steps)...")
    model.run(steps=500)
    
    # Display results
    print("\n📊 SIMULATION RESULTS:")
    print("-" * 70)
    print(f"Total Jobs Completed: {model.count_completed_jobs()}")
    print(f"Average Tardiness: {model.avg_tardiness():.2f} minutes")
    print(f"Average Utilization: {model.avg_utilization():.1f}%")
    
    print("\nPer-Plant Statistics:")
    for plant_id, plant in model.plants.items():
        if plant.completed_schedules:
            print(f"\n  {plant_id}:")
            print(f"    Jobs Completed: {len(plant.completed_schedules)}")
            print(f"    Total Tardiness: {plant.total_tardiness} min")
            avg_tard = plant.total_tardiness / len(plant.completed_schedules)
            print(f"    Average Tardiness: {avg_tard:.2f} min")
            print(f"    Utilization: {plant.get_utilization():.1f}%")
    
    # Performance metrics
    print("\n📈 PERFORMANCE METRICS:")
    print("-" * 70)
    all_schedules = []
    for plant in model.plants.values():
        all_schedules.extend(plant.completed_schedules)
    
    if all_schedules:
        report = PerformanceMetrics.generate_report(all_schedules)
        print(f"Makespan: {report['makespan']} minutes")
        print(f"Average Tardiness: {report['avg_tardiness']:.2f} minutes")
        print(f"Tardiness Std Dev: {report['tardiness_std']:.2f} minutes")
        print(f"On-Time Delivery: {report['on_time_percentage']:.1f}%")
        print(f"Average Flow Time: {report['avg_flow_time']:.2f} minutes")
        print(f"\nMachine Utilization:")
        for machine, time in report['machine_utilization'].items():
            print(f"  {machine}: {time} minutes")
    
    print("\n" + "="*70)
    print("✨ Real Data Example Completed Successfully!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()