from django.db.models.signals import post_save
from django.dispatch import receiver
from ..models import Customer
from config import settings


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_customer_profile_for_newly_created_user(sender , instance, created, **kwargs):
    if created:
        Customer.objects.create(user=instance)
