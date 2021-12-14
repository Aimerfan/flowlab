from django import forms
from .models import Lab


class LabForm(forms.ModelForm):
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
            # 'template': forms.Select(),
            'deadline': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
            }),
        }

    template = forms.ChoiceField(
        initial='none',
        choices=[('none', '無')],
        # TODO: 暫時設定為非必填, 否則無法通過表單驗證
        required=False,
    )
