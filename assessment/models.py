import uuid

from django.conf import settings
from django.db import models


class Attempt(models.Model):
    """Un intento de evaluación. El plan (preguntas, semillas, orden de opciones) vive en el servidor."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    session_key = models.CharField(max_length=40, blank=True, db_index=True)
    student_name = models.CharField(max_length=80)
    scope = models.CharField(max_length=20)
    plan = models.JSONField(default=list)       # [{id, seed, order}]
    state = models.JSONField(default=dict)      # progreso de los problemas paso a paso
    current = models.PositiveSmallIntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    points = models.FloatField(null=True, blank=True)
    total = models.PositiveSmallIntegerField(default=0)
    passed = models.BooleanField(null=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f'{self.student_name} · {self.scope} · {self.started_at:%Y-%m-%d %H:%M}'

    @property
    def finished(self):
        return self.finished_at is not None


class Answer(models.Model):
    attempt = models.ForeignKey(Attempt, related_name='answers', on_delete=models.CASCADE)
    index = models.PositiveSmallIntegerField()
    question_id = models.CharField(max_length=20)
    kind = models.CharField(max_length=10)
    topic = models.CharField(max_length=30)
    response = models.JSONField(default=dict)   # selección, texto o resumen de pasos
    score = models.FloatField(default=0)        # 0..1 calculado por el sistema
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['attempt', 'index']
        constraints = [models.UniqueConstraint(fields=['attempt', 'index'], name='unique_answer_per_question')]

    @property
    def effective_score(self):
        return self.score
