from django.urls import reverse

from linear.catalog import (FAMILIES as LINEAR_FAMILIES, ROUTE as LINEAR_ROUTE, TOPIC_SLUGS as LINEAR_SLUGS,
                            TOPICS as LINEAR_TOPICS)
from nonlinear.catalog import FAMILIES, METHODS, ROUTE, TOOL_SLUGS, TOPIC_SLUGS, TOPICS

from .catalog import AVAILABLE_MODULES, MODULES
from .models import UserProgress


def _route(route, completed, families):
    """Pasos de una ruta con su estado. Un paso con familia se completa al terminar cualquiera de sus métodos."""
    return [
        {**step, 'family': families.get(step.get('family')),
         'completed': any(slug in completed for slug in step['slugs'])}
        for step in route
    ]


def navigation(request):
    if request.user.is_authenticated:
        completed = set(
            UserProgress.objects.filter(user=request.user, module='nonlinear', completed=True).values_list(
                'topic', flat=True
            )
        )
    else:
        completed = set(request.session.get('completed_topics', []))
    if request.user.is_authenticated:
        linear_done = set(
            UserProgress.objects.filter(user=request.user, module='linear', completed=True).values_list(
                'topic', flat=True
            )
        )
    else:
        linear_done = completed & LINEAR_SLUGS
    linear_done &= LINEAR_SLUGS
    # Temas retirados del catálogo (p. ej. «practica») no deben inflar el avance.
    completed &= TOPIC_SLUGS

    topics = [
        {
            'slug': slug,
            'title': title,
            'icon': icon,
            'description': description,
            'difficulty': difficulty,
            'completed': slug in completed,
        }
        for slug, title, icon, description, difficulty in TOPICS
    ]
    linear_topics = [
        {'slug': slug, 'title': title, 'icon': icon, 'description': description, 'difficulty': difficulty,
         'completed': slug in linear_done}
        for slug, title, icon, description, difficulty in LINEAR_TOPICS
    ]

    # Rutas por módulo: lo que ve el estudiante en la barra lateral y en la portada de cada módulo.
    route_topics = _route(ROUTE, completed, FAMILIES)
    linear_route = _route(LINEAR_ROUTE, linear_done, LINEAR_FAMILIES)
    route_completed_count = sum(1 for step in route_topics if step['completed'])
    linear_completed_count = sum(1 for step in linear_route if step['completed'])

    path = request.path
    section = ('practice' if '/practica/' in path else 'assessment' if '/autoevaluacion/' in path or path.startswith('/evaluacion/')
               else 'resources' if path == '/recursos/' else 'theory' if path.startswith(('/ecuaciones-no-lineales/', '/sistemas-lineales/', '/teoria/')) else 'home')
    errors_focus = (path in ('/', '/ecuaciones-no-lineales/errores/', '/ecuaciones-no-lineales/teoria/', '/ecuaciones-no-lineales/practica/', '/ecuaciones-no-lineales/autoevaluacion/')
                    and request.GET.get('vista') != 'modulo'
                    and request.GET.get('tema', 'errores') == 'errores')
    return {
        'errors_focus': errors_focus,
        'learning_section': section,
        'is_linear_module': path.startswith('/sistemas-lineales/') or (path == '/evaluacion/' and request.GET.get('alcance') == 'modulo-2'),
        'show_topic_strip': not errors_focus and path.startswith('/ecuaciones-no-lineales/') and getattr(request.resolver_match, 'url_name', None) == 'page',
        'linear_topics': linear_topics,
        'linear_route': linear_route,
        'linear_completed_count': linear_completed_count,
        'learning_topics': topics,
        'route_topics': route_topics,
        'tool_topics': [topic for topic in topics if topic['slug'] in TOOL_SLUGS],
        'completed_count': len(completed),
        'route_completed_count': route_completed_count,
        'module_progress': round(route_completed_count / len(ROUTE) * 100),
        'course_modules': MODULES,
        'available_modules': AVAILABLE_MODULES,
        # URL canónica de cada simulador; JS y plantillas la usan en vez de rutas escritas a mano.
        'simulator_urls': {key: reverse('nonlinear:page', args=[method['slug']]) for key, method in METHODS.items()},
    }
