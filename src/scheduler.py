"""
Scheduling module for running the agent at specific times
Supports both scheduled and manual triggers
"""
import schedule
import time
from typing import Callable
import pytz
from datetime import datetime


class EmailScheduler:
    """Manages scheduling of email processing"""
    
    def __init__(self, timezone: str = "America/New_York"):
        self.timezone = pytz.timezone(timezone)
        self.jobs = []
        self.is_running = False
    
    def schedule_daily(self, time_str: str, job_func: Callable) -> schedule.Job:
        """
        Schedule a job to run at a specific time daily
        
        Args:
            time_str: Time in HH:MM format (24-hour)
            job_func: Function to call
        
        Returns:
            schedule.Job object
        """
        try:
            job = schedule.at(time_str).do(job_func)
            self.jobs.append(job)
            print(f"✓ Scheduled job at {time_str}")
            return job
        except Exception as e:
            print(f"Error scheduling job: {str(e)}")
            return None
    
    def schedule_multiple(self, times: list, job_func: Callable):
        """Schedule job at multiple times"""
        for time_str in times:
            self.schedule_daily(time_str, job_func)
    
    def run_manual(self, job_func: Callable) -> bool:
        """Run job immediately (manual trigger)"""
        try:
            print(f"▶ Running manual trigger at {datetime.now(self.timezone).strftime('%Y-%m-%d %H:%M:%S')}")
            job_func()
            return True
        except Exception as e:
            print(f"Error running manual trigger: {str(e)}")
            return False
    
    def start_scheduler(self, interval: int = 60):
        """
        Start the scheduler loop
        
        Args:
            interval: Check interval in seconds (default 60)
        """
        self.is_running = True
        print(f"✓ Scheduler started (checking every {interval}s)")
        
        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n✓ Scheduler stopped by user")
            self.stop_scheduler()
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        self.is_running = False
        schedule.clear()
        self.jobs = []
        print("✓ Scheduler stopped and cleared")
    
    def get_job_count(self) -> int:
        """Get number of scheduled jobs"""
        return len(self.jobs)
    
    def get_next_run(self) -> str:
        """Get time of next scheduled run"""
        if self.jobs:
            next_job = min(self.jobs, key=lambda x: x.next_run)
            return next_job.next_run.strftime('%Y-%m-%d %H:%M:%S') if next_job.next_run else "Unknown"
        return "No jobs scheduled"
    
    def clear_schedule(self):
        """Clear all scheduled jobs"""
        schedule.clear()
        self.jobs = []
        print("✓ All jobs cleared")
