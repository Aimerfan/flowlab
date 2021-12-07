from django import forms


class LabForm(forms.Form):

    name = forms.CharField(
        max_length=50,
        strip=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        }),
    )
    description = forms.CharField(
        required=False,
        max_length=256,
        strip=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': '3'
        }),
    )
    branch = forms.CharField(
        max_length=50,
        strip=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        }),
    )
    template = forms.ChoiceField(
        initial='none',
        choices=[('none', '無')],
    )
    dateline = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        }),
    )
