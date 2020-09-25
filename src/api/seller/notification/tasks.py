from celery.task import task

from explorer.models import Query

from seller.user.tasks import send_notifications_user


@task(name='send_query_notifications')
def send_query_notification(sender_user, sql, notification):
    query = Query(sql=sql)
    user_ids = [x[0] for x in query.execute().data]

    send_notifications_user.delay(
        sender_user,
        user_ids,
        notification['notification_text'],
        notification['title'],
        notification['subtitle'], {
            'vendor_id': notification['vendor_id'],
            'icon_image': notification['icon_url'],
            'large_image': notification['image_url'],
            # Adding to context ensures the frontend sees this
            'title': notification['title'],
        }, {
            'icon': notification['icon'],
            'image': notification['image'],
        })
