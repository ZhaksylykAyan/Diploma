import logging
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from chat.models import UserStatus
from django.db.models.signals import post_save
from django.conf import settings

logger = logging.getLogger(__name__)

@receiver(user_logged_in)
def log_login(sender, request, user, **kwargs):
    ip = get_client_ip(request)
    logger.info(f"Вход: {user.email} (IP: {ip})")

@receiver(user_logged_out)
def log_logout(sender, request, user, **kwargs):
    ip = get_client_ip(request)
    logger.info(f"Выход: {user.username} (IP: {ip})")

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_status(sender, instance, created, **kwargs):
    if created:
        UserStatus.objects.get_or_create(user=instance)