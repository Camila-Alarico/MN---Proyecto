"""Búsqueda global de contenidos: un solo algoritmo y un solo destino (`/buscar/`).

Antes cada origen tenía su propia lógica: la barra superior enviaba a la portada del módulo y un
script filtraba tarjetas en el navegador (distinguía tildes y solo buscaba en el título). Ahora la
consulta se resuelve en el servidor, sin distinguir mayúsculas ni tildes, sobre los temas del
módulo 1 y sobre el programa del curso.
"""
import unicodedata

from django.urls import reverse

from linear.catalog import TOPICS as LINEAR_TOPICS
from nonlinear.catalog import TOPICS

from .catalog import MODULES

MAX_QUERY_LENGTH = 80


def normalize(text):
    """Minúsculas y sin tildes: «Bisección» y «biseccion» son la misma búsqueda."""
    decomposed = unicodedata.normalize('NFKD', text.casefold())
    return ''.join(char for char in decomposed if not unicodedata.combining(char))


def _score(terms, title, description):
    """0 si algún término no aparece; si aparecen todos, el título pesa el doble que la descripción."""
    title, description = normalize(title), normalize(description)
    if not all(term in title or term in description for term in terms):
        return 0
    return sum(2 if term in title else 1 for term in terms)


def search_catalog(query):
    """Devuelve `{'topics': [...], 'modules': [...]}` ordenado por relevancia y luego por programa."""
    terms = normalize(query[:MAX_QUERY_LENGTH]).split()
    # Expresiones cortas habituales: «quiero Newton», «buscar bisección».
    fillers = {'quiero', 'buscar', 'busca', 'ver', 'aprender', 'sobre', 'el', 'la', 'de', 'tema'}
    terms = [term for term in terms if term not in fillers]
    found = {'topics': [], 'modules': []}
    if not terms:
        return found
    for slug, title, icon, description, difficulty in TOPICS:
        score = _score(terms, title, description)
        if score:
            found['topics'].append((score, {'title': title, 'description': description, 'icon': icon,
                                            'difficulty': difficulty,
                                            'url': reverse('nonlinear:page', args=[slug]), 'module': 1}))
    for slug, title, icon, description, difficulty in LINEAR_TOPICS:
        score = _score(terms, title, description)
        if score:
            found['topics'].append((score, {'title': title, 'description': description, 'icon': icon,
                                            'difficulty': difficulty,
                                            'url': reverse('linear:page', args=[slug]), 'module': 2}))
    for module in MODULES:
        score = _score(terms, module['title'], module['description'])
        if score:
            found['modules'].append((score, module))
    return {kind: [item for _, item in sorted(items, key=lambda pair: -pair[0])] for kind, items in found.items()}
