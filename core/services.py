"""Reglas de negocio de cuentas y progreso, independientes de las vistas."""
from linear.catalog import TOPIC_SLUGS as LINEAR_SLUGS, TOPICS as LINEAR_TOPICS
from nonlinear.catalog import TOPICS

from .models import UserProgress

SESSION_TOPICS_KEY = 'completed_topics'
VALID_TOPICS = {slug for slug, *_ in TOPICS} | {slug for slug, *_ in LINEAR_TOPICS}


def adopt_session_progress(request, user):
    """Traslada a la cuenta los temas completados como invitado y limpia la sesión.

    Se ejecuta al registrarse y al iniciar sesión (señal `user_logged_in`), de modo
    que el trabajo de invitado nunca se pierde. Devuelve la cantidad de temas nuevos.
    """
    topics = [topic for topic in request.session.get(SESSION_TOPICS_KEY, []) if topic in VALID_TOPICS]
    created = 0
    for topic in topics:
        progress, was_created = UserProgress.objects.get_or_create(
            user=user,
            module='linear' if topic in LINEAR_SLUGS else 'nonlinear',
            topic=topic,
            defaults={'completed': True, 'progress_percentage': 100},
        )
        if not was_created and (not progress.completed or progress.progress_percentage != 100):
            progress.completed = True
            progress.progress_percentage = 100
            progress.save(update_fields=['completed', 'progress_percentage', 'updated_at'])
        created += was_created
    if topics:
        request.session.pop(SESSION_TOPICS_KEY, None)
    return created
