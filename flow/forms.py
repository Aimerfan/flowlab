from django import forms

from .dicts import REPO_TEMPLATES_SRC


class BaseRepoForm(forms.Form):

    REPO_VISIBILITY = [
        ('public', {'name': '公開 Public',
                    'info': '任何人都可以訪問該專案，無須身份驗證。'}),
        ('internal', {'name': '內部 Internal',
                      'info': '除了外部用戶外，任何已登入的使用者皆能訪問該專案。'}),
        ('private', {'name': '私人 Private',
                     'info': '專案的訪問權限必須明確授予每個使用者。若專案屬於某個群組，則該群組的所有成員皆具有訪問權限。'}),
    ]

    name = forms.CharField(
        max_length=50,
        strip=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    description = forms.CharField(
        required=False,
        max_length=256,
        strip=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '3'}),
    )
    visibility = forms.ChoiceField(
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        choices=REPO_VISIBILITY, initial=REPO_VISIBILITY[0],
    )


class BlankRepoForm(BaseRepoForm):
    add_file = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        choices=[
            ('jenkins', '使用 Jenkins File 初始化儲存庫'),
            ('readme',  '使用 README 初始化儲存庫'),
        ],
    )


class TemplateRepoForm(BaseRepoForm):
    template = forms.ChoiceField(
        initial='',
        choices=[('', '(選擇一個模板)')] + REPO_TEMPLATES_SRC['local']['templates'],
    )


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
