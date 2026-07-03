"""Streamlit interactive dashboard"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from src.agents.plant_agent import ProductionModel
from src.models.job import Job, JobOperation
import logging

logger = logging.getLogger(__name__)


def render_dashboard():
    st.set_page_config(layout="wide", page_title="Production Planner")
    st.title("🏭 Distributed Production Planning Dashboard")

    # Sidebar controls
    st.sidebar.header("⚙️ Simulation Control")
    num_plants = st.sidebar.slider("Number of Plants", 2, 5, 2)
    num_jobs = st.sidebar.slider("Number of Jobs", 5, 50, 10)
    num_steps = st.sidebar.slider("Simulation Steps", 10, 500, 100)

    if st.sidebar.button("▶️ Run Simulation"):
        with st.spinner("Running simulation..."):
            # Create model
            model = ProductionModel(num_plants)

            # Add machines
            for plant in model.plants.values():
                plant.add_machine("M1", capacity=1)
                plant.add_machine("M2", capacity=1)
                plant.add_machine("M3", capacity=1)

            # Create and submit jobs
            for i in range(num_jobs):
                operations = [
                    JobOperation(operation_id=0, machine_id="M1", duration=5),
                    JobOperation(operation_id=1, machine_id="M2", duration=3),
                    JobOperation(operation_id=2, machine_id="M3", duration=4),
                ]
                job = Job(
                    job_id=f"Job_{i}",
                    plant_id="Plant_0",
                    operations=operations,
                    arrival_time=datetime.now(),
                    due_date=datetime.now() + timedelta(hours=2),
                    priority=1
                )
                model.plants["Plant_0"].submit_job(job)

            # Run simulation
            model.run(num_steps)

            # Display metrics
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "✅ Total Completed Jobs",
                    model.count_completed_jobs()
                )

            with col2:
                st.metric(
                    "⏱️ Average Tardiness",
                    f"{model.avg_tardiness():.2f} units"
                )

            with col3:
                st.metric(
                    "🔧 Avg Utilization",
                    f"{model.avg_utilization():.1f}%"
                )

            # Display KPI charts
            st.subheader("📊 KPI Trends")
            df = model.datacollector.get_model_vars_dataframe()
            st.line_chart(df)

            # Plant details
            st.subheader("🏢 Plant Details")
            for plant_id, plant in model.plants.items():
                with st.expander(f"{plant_id} Details"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Jobs Completed**: {len(plant.completed_schedules)}")
                        st.write(f"**Total Tardiness**: {plant.total_tardiness}")
                    with col2:
                        st.write(f"**Utilization**: {plant.get_utilization():.1f}%")
                        if plant.completed_schedules:
                            avg_tard = plant.total_tardiness / len(plant.completed_schedules)
                            st.write(f"**Avg Tardiness**: {avg_tard:.2f}")


if __name__ == "__main__":
    render_dashboard()