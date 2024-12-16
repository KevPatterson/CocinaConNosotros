from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_save, sender=User)
def assign_default_role(sender, instance, created, **kwargs):
    if created:  # Si el usuario acaba de ser creado
        user_group, _ = Group.objects.get_or_create(name='Usuario')  # Asegúrate de que el grupo existe
        instance.groups.add(user_group)  # Asigna el grupo al usuario
