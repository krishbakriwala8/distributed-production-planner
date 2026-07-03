# 🏭 Distributed Production Planning with Multi-Agent Scheduling

A comprehensive Python-based multi-agent system for distributed production planning and scheduling across multiple manufacturing plants. Built with **Mesa**, **SimPy**, **Google OR-Tools**, and **Game Theory** principles.

## 📋 Overview

This project demonstrates a realistic industrial scheduling system designed for **German automotive companies** (BMW, Mercedes-Benz, Audi, Volkswagen, Siemens) implementing **Industry 4.0** and **Production Level 4** standards.

### Key Features

- **Multi-Agent System**: Plant, Job, and Machine agents using Mesa framework
- **Distributed Scheduling**: Coordinate production across multiple plants
- **Optimization Engine**: Google OR-Tools for constraint-based job shop scheduling
- **Game Theory**: Nash equilibrium-based negotiation between plants
- **Real-time Simulation**: SimPy discrete event simulation
- **Interactive Dashboard**: Streamlit-based visualization
- **REST API**: FastAPI for external integration
- **Production Ready**: Docker, PostgreSQL, Redis support

## 🏗️ Project Structure

```
distributed-production-planner/
├── README.md
├── requirements.txt
├── setup.py
├── docker-compose.yml
├── Dockerfile
├── .gitignore
│
├── src/
│   ├── __init__.py
│   ├── models/           # Data models (Job, Machine, Plant)
│   ├── agents/           # Mesa agents (Plant, Job, Machine)
│   ├── optimization/     # OR-Tools solver, game theory
│   ├── simulation/       # Main production model
│   ├── communication/    # Message protocols
│   ├── database/         # SQLAlchemy ORM
│   ├── visualization/    # Streamlit dashboard
│   ├── api/              # FastAPI REST endpoints
│   └── utils/            # Configuration, logging
│
├── tests/                # Unit tests
├── examples/             # Working examples
└── notebooks/            # Jupyter analysis notebooks
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip or poetry

### Installation

```bash
# Clone repository
git clone https://github.com/krishbakriwala8/distributed-production-planner.git
cd distributed-production-planner

# Install dependencies
pip install -r requirements.txt

# Or with poetry
poetry install
```

### Run Simple Example

```bash
python examples/simple_example.py
```

**Output:**
```
============================================================
Distributed Production Planning - Simple Example
============================================================

1️⃣ USING OR-TOOLS SOLVER:
------------------------------------------------------------
✅ Schedule found!

  Job_0:
    Op 0: Start=0, Duration=5, Machine=M1
    Op 1: Start=5, Duration=3, Machine=M2

2️⃣ USING MESA + SIMPY SIMULATION:
------------------------------------------------------------
✅ Simulation completed!
  Total completed jobs: 5
  Average tardiness: 2.50
```

### Run API Server

```bash
python -m uvicorn src.api.main:app --reload
# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### Run Streamlit Dashboard

```bash
streamlit run src/visualization/dashboard.py
# Dashboard available at http://localhost:8501
```

### Run with Docker

```bash
docker-compose up
# API: http://localhost:8000
# Dashboard: http://localhost:8501
# Database: localhost:5432
```

## 📚 Core Components

### 1. **Multi-Agent System** (Mesa)
- **PlantAgent**: Manages machines and job processing
- **JobAgent**: Represents production jobs/orders
- **MachineAgent**: Simulates machine resources
- **SchedulerAgent**: Coordinates scheduling across plants

### 2. **Optimization Engine** (OR-Tools)
- Constraint programming solver for job shop scheduling
- Minimizes makespan (total production time)
- Handles precedence and capacity constraints
- Supports distributed multi-plant scheduling

### 3. **Game Theory** (nashpy, Gambit)
- Nash equilibrium computation for plant negotiation
- Best response dynamics for distributed decisions
- Resource allocation based on game-theoretic principles

### 4. **Simulation** (SimPy)
- Discrete event simulation for production processes
- Real-time resource contention modeling
- Accurate job routing and machine usage

### 5. **Visualization** (Streamlit, Plotly)
- Interactive dashboards
- Gantt charts for job schedules
- Real-time KPI monitoring
- Performance analytics

## 📖 Usage Examples

### Example 1: Basic Job Scheduling

```python
from src.models.job import Job, JobOperation
from src.optimization.job_shop import JobShopScheduler
from datetime import datetime, timedelta

# Create job with operations
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

# Solve with OR-Tools
scheduler = JobShopScheduler(max_time=1000)
schedule = scheduler.schedule_jobs([job], {"M1": 1, "M2": 1})
print(schedule)
```

### Example 2: Multi-Agent Simulation

```python
from src.agents.plant_agent import ProductionModel

# Create model with 2 plants
model = ProductionModel(num_plants=2)

# Add machines
for plant in model.plants.values():
    plant.add_machine("M1", capacity=1)
    plant.add_machine("M2", capacity=1)

# Run simulation for 100 steps
model.run(steps=100)

# Get results
print(f"Completed jobs: {model.count_completed_jobs()}")
print(f"Avg tardiness: {model.avg_tardiness()}")
```

### Example 3: Game-Theoretic Negotiation

```python
from src.optimization.game_theory import NegotiationProtocol
import numpy as np

protocol = NegotiationProtocol(plants=["Plant_0", "Plant_1"])

# Define payoff matrices
payoff_a = np.array([[-100, -50], [-50, -100]])
payoff_b = np.array([[-100, -50], [-50, -100]])

# Find Nash equilibrium
equilibria = protocol.compute_nash_equilibrium(payoff_a, payoff_b)
print(f"Nash equilibria: {equilibria}")
```

## 🔌 REST API Endpoints

### Schedule a Job
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
    "arrival_time": "2026-05-29T10:00:00",
    "due_date": "2026-05-29T12:00:00"
  }'
```

### Get System Status
```bash
curl http://localhost:8000/api/status
```

### Health Check
```bash
curl http://localhost:8000/api/health
```

## 📊 Key Performance Indicators (KPIs)

- **Makespan**: Total production time
- **Tardiness**: Jobs completing after due date
- **Machine Utilization**: Percentage of time machines are working
- **Average Flow Time**: Average time job spends in system
- **On-Time Percentage**: % of jobs completed before due date
- **Schedule Feasibility**: % of feasible solutions found

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_agents.py -v

# Run specific test
pytest tests/test_agents.py::test_production_model_creation -v
```

## 📦 Tech Stack

| Layer | Technology |
|-------|------------|
| **Agent Framework** | Mesa 1.10+ |
| **Simulation** | SimPy 4.1+ |
| **Optimization** | Google OR-Tools 9.7+ |
| **Game Theory** | nashpy 0.0.48+ |
| **API** | FastAPI 0.104+ |
| **Dashboard** | Streamlit 1.28+ |
| **Visualization** | Plotly 5.17+ |
| **Database** | PostgreSQL 13+, SQLAlchemy 2.0+ |
| **Cache** | Redis 5.0+ |
| **Communication** | Celery 5.3+, paho-mqtt 1.6+ |
| **Testing** | pytest 7.4+ |

## 🎓 For Master's Internship

This project is designed for **master's-level computer science or operations research interns** working with German manufacturing companies.

### Learning Outcomes
- ✅ Multi-agent system design and implementation
- ✅ Distributed optimization algorithms
- ✅ Game theory applications in scheduling
- ✅ Industrial simulation and modeling
- ✅ Production systems (Industry 4.0)
- ✅ Full-stack Python development
- ✅ API design and deployment
- ✅ Docker containerization

### Internship Timeline
- **Month 1**: Core system implementation (Mesa, SimPy)
- **Month 2**: Optimization engine (OR-Tools, game theory)
- **Month 3**: Production deployment (API, dashboard, Docker)

### Company Integration Points
- **Siemens**: Industrial AI & automation
- **BMW**: AI manufacturing optimization
- **Mercedes-Benz**: Smart factory production
- **Audi**: Digitalization & process optimization
- **Volkswagen**: Industry 4.0 integration
- **DFKI**: Research in innovative factory systems

## 📚 Resources & References

### Documentation
- [Mesa Documentation](https://mesa.readthedocs.io/)
- [SimPy Documentation](https://simpy.readthedocs.io/)
- [OR-Tools Scheduling](https://developers.google.com/optimization/scheduling)
- [nashpy Documentation](https://nashpy.readthedocs.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)

### Academic Papers
- Multi-agent job shop scheduling
- Game-theoretic distributed scheduling
- Industry 4.0 production systems
- Nash equilibrium computation

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

## 👤 Author

**Krish Bakriwala** - Master's Intern in Multi-Agent Systems

---

## 🏆 Project Highlights

✨ **Industry-Ready**: Designed for German manufacturing companies
🔬 **Research-Grade**: Based on peer-reviewed algorithms
🎯 **Educational**: Perfect for master's thesis or research project
🚀 **Production-Ready**: Docker, API, Dashboard included
📊 **Well-Documented**: Comprehensive examples and documentation

---

**Last Updated**: May 29, 2026

**Repository**: https://github.com/krishbakriwala8/distributed-production-planner