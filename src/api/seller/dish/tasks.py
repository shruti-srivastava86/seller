from celery.schedules import crontab
from celery.task import periodic_task

from seller.dish.models import Dish


@periodic_task(run_every=(crontab(minute=0, hour=0)), name="remove_temporary_price")
def task_remove_temporary_price():
    try:
        Dish.objects.filter(temporary_price__gt=0).update(temporary_price=0)
        print("Completed removing temporary price to dishes")
    except Exception as e:
        print("Failed to remove temporary price for dishes with error: {}".format(str(e)))
