from django import forms


class TestSelectForm(forms.Form):
    UNIT_TEST = 'unit_test'
    COVERAGE = 'coverage'
    SONARQUBE = 'sonarqube'

    selected_tests = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input',
            'role': 'switch',
        }),
        choices=[
            (UNIT_TEST, '單元測試'),
            (COVERAGE, '覆蓋率檢測'),
            (SONARQUBE, 'Sonar Qube 檢測'),
        ]
    )
