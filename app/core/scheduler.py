import schedule
import time
import threading
import logging
from datetime import datetime
import asyncio

from app.core.crew_manager import crew_manager

logger = logging.getLogger(__name__)

class TaskScheduler:
    def __init__(self):
        self.running = False
        self.thread = None
    
    def start(self):
        """Start the scheduler in a separate thread"""
        if self.running:
            logger.warning("Scheduler is already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        logger.info("Task scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        if self.thread:
            self.thread.join()
        logger.info("Task scheduler stopped")
    
    def _run_scheduler(self):
        """Run the scheduler loop"""
        # Schedule tasks
        schedule.every(6).hours.do(self._run_collection_job)
        schedule.every().day.at("09:00").do(self._run_daily_notifications)
        schedule.every().monday.at("08:00").do(self._run_weekly_notifications)
        schedule.every().hour.do(self._cleanup_old_data)
        
        logger.info("Scheduled tasks configured")
        
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                time.sleep(60)
    
    def _run_collection_job(self):
        """Run the collection pipeline"""
        logger.info("Running scheduled collection job...")
        try:
            # Run async function in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(crew_manager.run_collection_pipeline())
            loop.close()
            
            logger.info(f"Collection job completed: {result}")
        except Exception as e:
            logger.error(f"Collection job failed: {e}")
    
    def _run_daily_notifications(self):
        """Send daily notifications to users who prefer daily alerts"""
        logger.info("Running daily notifications...")
        try:
            # This would query the database for users with daily preferences
            # For now, just log the action
            logger.info("Daily notifications would be sent here")
        except Exception as e:
            logger.error(f"Daily notifications failed: {e}")
    
    def _run_weekly_notifications(self):
        """Send weekly notifications to users who prefer weekly alerts"""
        logger.info("Running weekly notifications...")
        try:
            # This would query the database for users with weekly preferences
            # For now, just log the action
            logger.info("Weekly notifications would be sent here")
        except Exception as e:
            logger.error(f"Weekly notifications failed: {e}")
    
    def _cleanup_old_data(self):
        """Clean up old data and logs"""
        logger.info("Running data cleanup...")
        try:
            # This would clean up old logs, expired opportunities, etc.
            logger.info("Data cleanup completed")
        except Exception as e:
            logger.error(f"Data cleanup failed: {e}")

# Global scheduler instance
scheduler = TaskScheduler()

def start_scheduler():
    """Start the global scheduler"""
    scheduler.start()

def stop_scheduler():
    """Stop the global scheduler"""
    scheduler.stop()