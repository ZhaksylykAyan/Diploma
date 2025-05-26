from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from chat.models import UserStatus

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_status(sender, instance, created, **kwargs):
    if created:
        UserStatus.objects.get_or_create(user=instance)
