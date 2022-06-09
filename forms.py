from django import forms
class LoginForm(forms.Form):
        user = forms.CharField(label='LOGIN')
        password = forms.CharField(label='HASŁO', widget=forms.PasswordInput)
from django import forms
class RetrievePackageForm(forms.Form):
    package_id = forms.CharField(max_length="12",required=True)