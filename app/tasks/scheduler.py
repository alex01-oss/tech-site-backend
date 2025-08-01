import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import cleanup_expired_tokens

logging.basicConfig(level=logging.INFO)

scheduler = BackgroundScheduler()


def job_cleanup_tokens():
    try:
        db: Session = SessionLocal()
        deleted_count = cleanup_expired_tokens(db)
        db.close()
    except Exception as e:
        logging.error(f"Error executing background token cleanup task: {e}")


def start_scheduler():
    scheduler.add_job(
        job_cleanup_tokens,
        IntervalTrigger(hours=1),
        id="cleanup_tokens",
        name="Cleanup expired tokens",
        replace_existing=True,
    )
    scheduler.start()
    logging.info("Task Scheduler started.")


def stop_scheduler():
    scheduler.shutdown(wait=False)
    logging.info("Task Scheduler stopped.")
