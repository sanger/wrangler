from apscheduler.schedulers.background import BackgroundScheduler  # type: ignore
from flask import Flask


def init_scheduler(app: Flask) -> BackgroundScheduler:
    """
    Initialise the scheduler and ensure it is shut down correctly when Flask is stopped.
    Args:
        app: The Flask app the scheduler is running in

    Returns: The initialised scheduler

    """
    scheduler = BackgroundScheduler()
    app.logger.info("Starting scheduler.")
    scheduler.start()
    app.teardown_appcontext(scheduler.shutdown)
    return scheduler
