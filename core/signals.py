from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from .services import adopt_session_progress


@receiver(user_logged_in)
def merge_guest_progress(sender, request, user, **kwargs):
    if request is not None and hasattr(request, 'session'):
        adopt_session_progress(request, user)
