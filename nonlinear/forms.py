from django import forms
from .catalog import METHODS


class CalculationForm(forms.Form):
    expression = forms.CharField(max_length=200)
    tolerance = forms.FloatField(min_value=1e-12, max_value=0.1, initial=0.0001)
    max_iterations = forms.IntegerField(min_value=1, max_value=200, initial=100)
    a = forms.FloatField(required=False, min_value=-1e12, max_value=1e12)
    b = forms.FloatField(required=False, min_value=-1e12, max_value=1e12)
    x0 = forms.FloatField(required=False, min_value=-1e12, max_value=1e12)
    x1 = forms.FloatField(required=False, min_value=-1e12, max_value=1e12)

    def __init__(self, method, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in METHODS[method]['parameters']:
            self.fields[field].required = True
