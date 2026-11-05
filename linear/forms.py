from django import forms

from nonlinear.services.parser import MathInputError, finite

from .catalog import METHODS


class LinearSystemForm(forms.Form):
    size = forms.IntegerField(min_value=2, max_value=3)
    matrix = forms.JSONField()
    vector = forms.JSONField()
    tolerance = forms.FloatField(required=False, min_value=1e-12, max_value=0.1, initial=0.000001)
    max_iterations = forms.IntegerField(required=False, min_value=1, max_value=200, initial=100)

    def __init__(self, method, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in METHODS[method]['parameters']:
            self.fields[field].required = True

    def clean(self):
        cleaned = super().clean()
        n, matrix, vector = cleaned.get('size'), cleaned.get('matrix'), cleaned.get('vector')
        if n is None or matrix is None or vector is None:
            return cleaned
        if not (isinstance(matrix, list) and len(matrix) == n and all(isinstance(r, list) and len(r) == n for r in matrix)):
            raise forms.ValidationError(f'La matriz debe ser de {n}×{n}.')
        if not (isinstance(vector, list) and len(vector) == n):
            raise forms.ValidationError(f'El vector debe tener {n} componentes.')
        try:
            cleaned['matrix'] = [[finite(v, f'A[{i + 1},{j + 1}]') for j, v in enumerate(row)]
                                 for i, row in enumerate(matrix)]
            cleaned['vector'] = [finite(v, f'b[{i + 1}]') for i, v in enumerate(vector)]
        except MathInputError as exc:
            raise forms.ValidationError(str(exc)) from None
        return cleaned
