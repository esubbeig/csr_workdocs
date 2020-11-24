from .models import *

def notifications_processor(request):
    
    try:
        notifications_count = Notifications.objects.filter(receiverId=request.user.id, read=False).count()
    except Notifications.DoesNotExist:
        notifications_count = None

    return {'notifications_count' : notifications_count}
