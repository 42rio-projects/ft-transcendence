from django import forms
from django.contrib.auth.password_validation import validate_password
from .models import User
from django.contrib import messages


class LoginForm(forms.Form):
    username = forms.CharField(label="Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput)


class RegisterForm(forms.Form):
    username = forms.CharField(label="Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput, validators=[validate_password])
    confirm_password = forms.CharField(label="Confirm password", widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data


class ChangePasswordForm(forms.Form):
	current_password = forms.CharField(label="Current password", widget=forms.PasswordInput)
	new_password = forms.CharField(label="New password", widget=forms.PasswordInput, validators=[validate_password])
	new_password_confirm = forms.CharField(label="Confirm new password", widget=forms.PasswordInput)

	def clean(self):
		cleaned_data = super().clean()
		new_password = cleaned_data.get('new_password')
		new_password_confirm = cleaned_data.get('new_password_confirm')

		if new_password != new_password_confirm:
			raise forms.ValidationError("Passwords do not match")

		return cleaned_data

class EmailChangeForm(forms.Form):
    new_email = forms.EmailField(label='Novo e-mail', required=True)
    confirm_email = forms.EmailField(label='Confirme o novo e-mail', required=True)

    def clean(self):
        cleaned_data = super().clean()
        new_email = cleaned_data.get("new_email")
        confirm_email = cleaned_data.get("confirm_email")

        if new_email and confirm_email:
            if new_email != confirm_email:
                raise forms.ValidationError("Os novos e-mails não correspondem.")
        return cleaned_data


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['avatar']
