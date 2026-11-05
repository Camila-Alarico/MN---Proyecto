from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class UserProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    module = models.CharField(max_length=40, default='nonlinear')
    topic = models.CharField(max_length=40)
    progress_percentage = models.PositiveSmallIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    completed = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'module', 'topic'], name='unique_user_topic'),
                       models.CheckConstraint(condition=models.Q(progress_percentage__lte=100), name='progress_max_100')]


class StudyNote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField(max_length=5000)
    updated_at = models.DateTimeField(auto_now=True)
