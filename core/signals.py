from django.dispatch import receiver
from store.signals import order_created


@receiver(order_created)
def after_created_order(sender, **kwargs):
    print(f"new order created {kwargs['order'].id}")
