"""Performance metrics calculation"""

from typing import List, Dict, Any
from src.models.job import Schedule
import statistics


class PerformanceMetrics:
    """Calculate KPIs for production schedules"""

    @staticmethod
    def calculate_makespan(schedules: List[Schedule]) -> int:
        """Calculate makespan (total production time)"""
        if not schedules:
            return 0
        return max(s.end_time for s in schedules)

    @staticmethod
    def calculate_avg_tardiness(schedules: List[Schedule]) -> float:
        """Calculate average job tardiness"""
        if not schedules:
            return 0.0
        return statistics.mean(s.tardiness for s in schedules)

    @staticmethod
    def calculate_tardiness_std(schedules: List[Schedule]) -> float:
        """Calculate tardiness standard deviation"""
        if len(schedules) < 2:
            return 0.0
        return statistics.stdev(s.tardiness for s in schedules)

    @staticmethod
    def calculate_on_time_percentage(schedules: List[Schedule]) -> float:
        """Calculate percentage of jobs completed on time"""
        if not schedules:
            return 0.0
        on_time = sum(1 for s in schedules if s.is_on_time)
        return (on_time / len(schedules)) * 100

    @staticmethod
    def calculate_avg_flow_time(schedules: List[Schedule]) -> float:
        """Calculate average flow time"""
        if not schedules:
            return 0.0
        return statistics.mean(s.completion_time for s in schedules)

    @staticmethod
    def calculate_machine_utilization(schedules: List[Schedule]) -> Dict[str, float]:
        """Calculate utilization per machine"""
        machine_times = {}
        for schedule in schedules:
            for op_id, assignment in schedule.machine_assignments.items():
                machine = assignment.get('machine', 'unknown')
                duration = assignment.get('duration', 0)
                if machine not in machine_times:
                    machine_times[machine] = 0
                machine_times[machine] += duration
        return machine_times

    @staticmethod
    def generate_report(schedules: List[Schedule]) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        return {
            "total_jobs": len(schedules),
            "makespan": PerformanceMetrics.calculate_makespan(schedules),
            "avg_tardiness": PerformanceMetrics.calculate_avg_tardiness(schedules),
            "tardiness_std": PerformanceMetrics.calculate_tardiness_std(schedules),
            "on_time_percentage": PerformanceMetrics.calculate_on_time_percentage(schedules),
            "avg_flow_time": PerformanceMetrics.calculate_avg_flow_time(schedules),
            "machine_utilization": PerformanceMetrics.calculate_machine_utilization(schedules)
        }