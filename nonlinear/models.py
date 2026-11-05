from django.conf import settings
from django.db import models


class CalculationHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    method = models.CharField(max_length=30)
    function_expression = models.CharField(max_length=200)
    parameters = models.JSONField(default=dict)
    result = models.JSONField(default=dict)
    favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
