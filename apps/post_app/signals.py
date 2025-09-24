import os

from django.db.models.signals import pre_delete
from django.dispatch import receiver

from apps.post_app.models import PostImage


@receiver(pre_delete, sender=PostImage)
def delete_image_file_on_delete(sender, instance, **kwargs):
    if instance.image:
        if instance.image.path and os.path.isfile(instance.image.path):
            os.remove(instance.image.path)
