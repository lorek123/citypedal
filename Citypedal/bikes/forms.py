# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth import get_user_model


class RegisterForm(forms.Form):
    username = forms.RegexField(label="Nazwa użytkownika", regex=r'^\w+$',
                                min_length=2,
                                max_length=30)
    password1 = forms.CharField(label="Hasło", min_length=4,
                                widget=forms.PasswordInput(render_value=False),
                                help_text="At least 4 chars long")
    password2 = forms.CharField(label="Powtórz hasło", min_length=4,
                                widget=forms.PasswordInput(render_value=False))
    email1 = forms.EmailField(label="Adres email")
    email2 = forms.EmailField(label="Powtórz adres email")
    first_name = forms.CharField(label="Imię", min_length=2)
    last_name = forms.CharField(label="Nazwisko", min_length=2)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        try:
            get_user_model().objects.get(username__iexact=username)
            raise forms.ValidationError("Nazwa użytkownika jest zajęta")
        except get_user_model().DoesNotExist:
            pass
        return username

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 != password2:
            raise forms.ValidationError(
                "Podane hasła się nie zgadzają?")
        return password2

    def clean_email2(self):
        email1 = self.cleaned_data.get('email1')
        email2 = self.cleaned_data.get('email2')
        if email1 != email2:
            raise forms.ValidationError(
                "Podane adresy email się nie zgadzają?")
        return email2

    def save(self):
        return get_user_model().objects.create_user(
            self.cleaned_data.get('username'),
            self.cleaned_data.get('email1'),
            self.cleaned_data.get('password1'),
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'))


class DisputeForm(forms.Form):
    description = forms.CharField(widget=forms.Textarea)
