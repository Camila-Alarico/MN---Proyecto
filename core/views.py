import json

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from urllib.parse import urlencode
from django.views.decorators.http import require_POST

from linear.catalog import HISTORY_PREFIX, HISTORY_TITLES, METHODS as LINEAR_METHODS
from nonlinear.catalog import DEFAULT_METHOD, METHODS, TOPICS
from nonlinear.models import CalculationHistory

from .catalog import MODULES
from .forms import RegisterForm
from .models import StudyNote, UserProgress
from .search import MAX_QUERY_LENGTH, search_catalog
from .services import adopt_session_progress


def health(request):
    return JsonResponse({'status': 'ok'})


def home(request):
    return render(request, 'core/home.html', {'modules': MODULES})


def theory(request):
    """Teoría general del curso: módulos y sus temas. Destino único del botón «Teoría» de la barra lateral."""
    return render(request, 'core/theory.html')


def search(request):
    """Único destino de todas las búsquedas del portal (ver core/urls.py)."""
    query = request.GET.get('q', '').strip()[:MAX_QUERY_LENGTH]
    results = search_catalog(query)
    return render(request, 'core/search.html', {
        'query': query, 'results': results, 'total': len(results['topics']) + len(results['modules']),
    })


def register(request):
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)  # la señal user_logged_in adopta el progreso de invitado
        adopt_session_progress(request, user)
        messages.success(request, 'Cuenta creada. Tu progreso de invitado se conservó.')
        return redirect('home')
    return render(request, 'registration/register.html', {'form': form})


def resources(request):
    return render(request, 'core/resources.html')


def _back(request, fallback='progress'):
    """Vuelve a la página desde la que se envió el formulario (favoritos o progreso)."""
    target = request.POST.get('next') or request.META.get('HTTP_REFERER', '')
    if target and url_has_allowed_host_and_scheme(target, allowed_hosts={request.get_host()}):
        return redirect(target)
    return redirect(fallback)


def _simulator_url(item):
    """Enlace canónico al simulador con los parámetros del cálculo guardado."""
    if item.method.startswith(HISTORY_PREFIX):  # sistemas lineales (módulo 2)
        key = item.method[len(HISTORY_PREFIX):]
        slug = LINEAR_METHODS[key]['slug'] if key in LINEAR_METHODS else 'comparacion-metodos'
        query = {'matrix': json.dumps(item.parameters.get('matrix')), 'vector': json.dumps(item.parameters.get('vector'))}
        return f"{reverse('linear:page', args=[slug])}?{urlencode(query)}"
    method = METHODS.get(item.method) or METHODS[DEFAULT_METHOD]
    query = {'expression': item.function_expression,
             **{key: value for key, value in item.parameters.items() if key != 'expression'}}
    return f"{reverse('nonlinear:page', args=[method['slug']])}?{urlencode(query)}"


def _history_context(request, queryset):
    method_titles = {key: method['title'] for key, method in METHODS.items()} | HISTORY_TITLES
    return [
        {
            'item': item,
            'url': _simulator_url(item),
            'method_title': method_titles.get(item.method, item.method),
            'root': item.result.get('root'),
            'status': item.result.get('status', ''),
            'iterations': item.result.get('iterations_count'),
        }
        for item in queryset
    ]


def progress(request):
    """Progreso: temas completados e historial de cálculos."""
    context = {'favorites': False}
    if request.user.is_authenticated:
        completed = set(
            UserProgress.objects.filter(user=request.user, module='nonlinear', completed=True).values_list(
                'topic', flat=True
            )
        )
        context['history'] = _history_context(request, CalculationHistory.objects.filter(user=request.user)[:30])
    else:
        completed = set(request.session.get('completed_topics', []))
        context['history'] = []
    completed &= {topic[0] for topic in TOPICS}
    context['topics'] = [
        {'slug': slug, 'title': title, 'icon': icon, 'completed': slug in completed}
        for slug, title, icon, _description, _difficulty in TOPICS
    ]
    return render(request, 'core/progress.html', context)


@login_required
def favorites(request):
    queryset = CalculationHistory.objects.filter(user=request.user, favorite=True)[:50]
    return render(
        request,
        'core/progress.html',
        {'history': _history_context(request, queryset), 'favorites': True, 'topics': []},
    )


@login_required
@require_POST
def toggle_favorite(request, pk):
    item = get_object_or_404(CalculationHistory, pk=pk, user=request.user)
    item.favorite = not item.favorite
    item.save(update_fields=['favorite'])
    return _back(request)


@login_required
@require_POST
def delete_history(request, pk):
    get_object_or_404(CalculationHistory, pk=pk, user=request.user).delete()
    messages.success(request, 'Cálculo eliminado del historial.')
    return _back(request)


@login_required
def notes(request):
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        if text and len(text) <= 5000:
            StudyNote.objects.create(user=request.user, text=text)
            messages.success(request, 'Apunte guardado.')
            return redirect('notes')
        messages.error(request, 'El apunte debe tener entre 1 y 5000 caracteres.')
    return render(
        request, 'core/notes.html', {'notes': StudyNote.objects.filter(user=request.user).order_by('-updated_at')}
    )


@login_required
@require_POST
def delete_note(request, pk):
    get_object_or_404(StudyNote, pk=pk, user=request.user).delete()
    messages.success(request, 'Apunte eliminado.')
    return redirect('notes')
