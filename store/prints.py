# from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.triggers.combining import AndTrigger
# from apscheduler.triggers.interval import IntervalTrigger
# from apscheduler.triggers.cron import CronTrigger
# from datetime import time


# def start():
#     scheduler = BackgroundScheduler()

#     # Run pullAndPrint every 30 seconds, but only at 8:00-23:00 every day
#     trigger = CronTrigger(
#         second='*/10',  # Fire every 30 seconds
#         minute='*',     # Every minute
#         hour='8-23',    # Between 8 AM and 11 PM
#         timezone='America/New_York'
#     )
#     scheduler.add_job(pullAndPrint, trigger)
#     scheduler.start()

# def pullAndPrint():
#     print("Hello World")
    