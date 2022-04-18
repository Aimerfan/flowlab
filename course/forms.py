from django import forms
from django.contrib.admin.widgets import AdminSplitDateTime

from .models import Lab


class LabForm(forms.ModelForm):
    deadline = forms.SplitDateTimeField(
        widget=forms.SplitDateTimeWidget(attrs={
            'class': 'd-flex justify-content-start',
            # FIXME: 繳交期限無法'選填'
        }),
    )

    class Meta:
        model = Lab
        fields = ['name', 'description', 'branch', 'template', 'deadline']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'strip': True,
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'strip': True,
                'required': False,
            }),
            'branch': forms.TextInput(attrs={
                'class': 'form-control',
                'strip': True,
            }),
            'template': forms.Select(attrs={
                'required': False,
            }),
        }
