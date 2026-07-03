# 🏭 Distributed Production Planning with Multi-Agent Scheduling

A Python-based multi-agent system for distributed production planning and scheduling across multiple manufacturing plants — built with **Mesa**, **SimPy**, **Google OR-Tools**, and **Game Theory**.

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

## 📋 Overview

This project models a realistic distributed industrial scheduling problem in the style of German automotive manufacturing (BMW, Mercedes-Benz, Volkswagen), combining three complementary approaches to production scheduling:

- **Constraint programming** (Google OR-Tools CP-SAT) for exact, makespan-optimal job-shop scheduling
- **Discrete-event multi-agent simulation** (Mesa + SimPy) for modeling real-time resource contention across plants
- **Game theory** (Nash equilibrium via `nashpy`) for modeling negotiation and load-balancing between competing plants

It's tested against both synthetic jobs and a realistic dataset modeled on real automotive production data (welding → painting → assembly → testing → shipping) across three plants.

### Key Features

- **Multi-Agent System**: Plant and Job agents built on Mesa
- **Distributed Scheduling**: Coordinate production across multiple plants with independently-keyed IDs (supports real-world plant identifiers, not just auto-generated ones)
- **Optimization Engine**: OR-Tools CP-SAT solver for constraint-based job-shop scheduling, minimizing makespan
- **Game Theory**: Nash equilibrium computation for plant-to-plant negotiation
- **Real-Time Simulation**: SimPy discrete-event simulation, properly synchronized with the Mesa agent step loop
- **Interactive Dashboard**: Streamlit-based visualization with live KPIs
- **REST API**: FastAPI endpoints for external integration
- **Containerized**: Docker + docker-compose with PostgreSQL and Redis

## 🏗️ Project Structure

```
distributed-production-planner/
├── README.md
├── requirements.txt
├── setup.py
├── docker-compose.yml
├── Dockerfile
│
├── src/
│   ├── models/           # Data models (Job, Machine, Plant, Schedule)
│   ├── agents/           # Mesa agents (Plant, Job) + SimPy-driven ProductionModel
│   ├── optimization/     # OR-Tools CP-SAT solver, game-theoretic negotiation
│   ├── simulation/       # Simulation runner + performance metrics
│   ├── visualization/    # Streamlit dashboard
│   ├── api/              # FastAPI REST endpoints
│   └── utils/            # Configuration, logging
│
├── data/                 # Realistic sample dataset (3 plants, 20+ jobs, 15+ machines)
├── tests/                # pytest unit + end-to-end regression tests
├── examples/             # Runnable end-to-end examples
└── notebooks/            # Jupyter analysis notebook
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip

### Installation

```bash
git clone https://github.com/krishbakriwala8/distributed-production-planner.git
cd distributed-production-planner
pip install -r requirements.txt
```

### Run the Examples

```bash
# Synthetic 5-job example: OR-Tools solver + Mesa/SimPy simulation side by side
python examples/simple_example.py

# Realistic dataset: 3 plants, 20 jobs, 15 machines, full KPI report
python examples/real_data_example.py
```

**Expected output (`simple_example.py`):**
```
1️⃣ USING OR-TOOLS SOLVER:
✅ Schedule found!
  Job_0:
    Op 0: Start=15, Duration=5, Machine=M1
    Op 1: Start=20, Duration=3, Machine=M2

2️⃣ USING MESA + SIMPY SIMULATION:
✅ Simulation completed!
  Total completed jobs: 5
  Average tardiness: 0.00
```

### Run the API Server

```bash
python -m uvicorn src.api.main:app --reload
# API:  http://localhost:8000
# Docs: http://localhost:8000/docs
```

### Run the Dashboard

```bash
streamlit run src/visualization/dashboard.py
# http://localhost:8501
```

### Run with Docker

```bash
docker-compose up
# API:      http://localhost:8000
# Dashboard: http://localhost:8501
# Database: localhost:5432
```

## 📚 Core Components

### 1. Multi-Agent System (Mesa + SimPy)
`PlantAgent` manages a set of machines (SimPy `Resource`s) and processes submitted `Job`s through their operation sequence, respecting machine capacity via `AddNoOverlap`-style resource contention. `ProductionModel` coordinates multiple plants and drives both the Mesa scheduler and the SimPy clock forward together each step — this synchronization is what makes jobs actually complete during a simulated run.

### 2. Optimization Engine (OR-Tools)
`JobShopScheduler` builds a CP-SAT model with interval variables per operation, precedence constraints between a job's operations, and no-overlap constraints per machine, then minimizes makespan.

### 3. Game Theory (nashpy)
`NegotiationProtocol` computes Nash equilibria over payoff matrices representing plant-to-plant load assignment decisions, and includes best-response and cooperation-potential heuristics for distributed negotiation.

### 4. Simulation (SimPy)
Jobs are processed as SimPy generator processes with machine resource requests and timeouts, giving realistic queueing behavior when multiple jobs compete for the same machine.

### 5. Visualization (Streamlit + Plotly)
Interactive dashboard for running simulations with configurable plant/job/step counts and viewing live KPI trends and per-plant breakdowns.

## 📖 Usage Examples

### Example 1: Basic Job Scheduling (OR-Tools)

```python
from src.models.job import Job, JobOperation
from src.optimization.job_shop import JobShopScheduler
from datetime import datetime, timedelta

operations = [
    JobOperation(operation_id=0, machine_id="M1", duration=5),
    JobOperation(operation_id=1, machine_id="M2", duration=3),
]

job = Job(
    job_id="Job_001",
    plant_id="Plant_0",
    operations=operations,
    arrival_time=datetime.now(),
    due_date=datetime.now() + timedelta(hours=2),
    priority=1
)

scheduler = JobShopScheduler(max_time=1000)
schedule = scheduler.schedule_jobs([job], {"M1": 1, "M2": 1})
print(schedule)
```

### Example 2: Multi-Agent Simulation

```python
from src.agents.plant_agent import ProductionModel

# Auto-generated plant IDs (Plant_0, Plant_1, ...)
model = ProductionModel(num_plants=2)

# Or use real-world plant IDs to line up with an external dataset:
# model = ProductionModel(plant_ids=["Plant_001", "Plant_002"])

for plant in model.plants.values():
    plant.add_machine("M1", capacity=1)
    plant.add_machine("M2", capacity=1)

model.run(steps=100)

print(f"Completed jobs: {model.count_completed_jobs()}")
print(f"Avg tardiness: {model.avg_tardiness()}")
```

### Example 3: Game-Theoretic Negotiation

```python
from src.optimization.game_theory import NegotiationProtocol
import numpy as np

protocol = NegotiationProtocol(plants=["Plant_0", "Plant_1"])

payoff_a = np.array([[-100, -50], [-50, -100]])
payoff_b = np.array([[-100, -50], [-50, -100]])

equilibria = protocol.compute_nash_equilibrium(payoff_a, payoff_b)
print(f"Nash equilibria: {equilibria}")
```

## 🔌 REST API Endpoints

**Schedule a job**
```bash
curl -X POST http://localhost:8000/api/schedule \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "Job_001",
    "plant_id": "Plant_0",
    "operations": [
      {"machine_id": "M1", "duration": 5},
      {"machine_id": "M2", "duration": 3}
    ],
    "arrival_time": "2026-07-03T10:00:00",
    "due_date": "2026-07-03T12:00:00"
  }'
```

**System status**
```bash
curl http://localhost:8000/api/status
```

**Health check**
```bash
curl http://localhost:8000/api/health
```

## 📊 Key Performance Indicators

- **Makespan** — total production time
- **Tardiness** — how late jobs complete relative to their due date
- **Machine Utilization** — % of time each machine is busy
- **Average Flow Time** — average time a job spends in the system
- **On-Time Percentage** — % of jobs completed by their due date

## 🧪 Testing

```bash
pytest                          # run all tests
pytest --cov=src                # with coverage
pytest tests/test_agents.py -v  # single file, verbose
```

10 tests currently pass, including two end-to-end regression tests that run a full simulation loop and assert jobs actually complete — added specifically to catch a class of bug (a simulation clock silently never advancing) that a purely unit-level test suite had previously missed.

## 📦 Tech Stack

| Layer | Technology |
|-------|------------|
| **Agent Framework** | Mesa 2.4+ |
| **Simulation** | SimPy 4.1+ |
| **Optimization** | Google OR-Tools 9.7+ |
| **Game Theory** | nashpy 0.0.43+ |
| **API** | FastAPI 0.104+ |
| **Dashboard** | Streamlit 1.28+ |
| **Visualization** | Plotly 5.17+ |
| **Database** | PostgreSQL 13+, SQLAlchemy 2.0+ |
| **Cache** | Redis 5.0+ |
| **Testing** | pytest 7.4+ |

## 🛠️ Engineering Notes

This project went through a debugging pass after the initial build surfaced several issues worth documenting, since they're the kind of thing that comes up in a technical interview:

- **Dependency pins that didn't exist on PyPI** (`mesa==1.10.1`, `nashpy==0.0.48`) and an unused, unpublished dependency (`gambit-core`) were blocking `pip install -r requirements.txt` entirely.
- **The SimPy clock was never advanced** inside the Mesa step loop, so submitted jobs were created as SimPy processes but never actually executed — simulations silently reported zero completed jobs. Fixed by advancing `env.run(until=...)` alongside the Mesa scheduler each step, with a regression test added to catch any recurrence.
- **Plant ID mismatches**: the real-data example used IDs like `Plant_001` while the model only generated `Plant_0`, `Plant_1`, ... — jobs and machines silently failed to attach to any plant. `ProductionModel` now accepts explicit `plant_ids` to support real-world identifiers.
- **Tardiness was computed by comparing simulation-relative time against a wall-clock Unix timestamp**, which always evaluated to zero. Fixed to compare against the due date's offset from job arrival, in simulation time units.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

MIT License — see `LICENSE` for details.

## 👤 Author

**Krish Bakriwala**
M.Sc. Artificial Intelligence, Brandenburg University of Technology (BTU Cottbus-Senftenberg)

- GitHub: [github.com/krishbakriwala8](https://github.com/krishbakriwala8)
- LinkedIn: [linkedin.com/in/krish-akshay-bakriwala-3885a61b8](https://linkedin.com/in/krish-akshay-bakriwala-3885a61b8)
