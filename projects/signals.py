# projects/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from .models import Project


@receiver(post_save, sender=Project)
def add_user_to_contributors_group(sender, instance, created, **kwargs):
    if created:
        user = instance.author
        group, created = Group.objects.get_or_create(name='Contributors')
        if not user.groups.filter(name='Contributors').exists():
            user.groups.add(group)
