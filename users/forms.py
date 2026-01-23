"""
Formulaires pour l'authentification et le profil utilisateur
"""

from django import forms
from django.contrib.auth import authenticate
from users.models import CustomUser


class LoginForm(forms.Form):
    """Formulaire de connexion"""
    email = forms.CharField(
        label="Email ou Téléphone",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email ou Téléphone',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Votre mot de passe',
        })
    )


class RegisterForm(forms.Form):
    """Formulaire d'inscription"""
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Prénom',
        })
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom',
        })
    )
    username = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': "Nom d'utilisateur (Optionnel - sera généré si vide)",
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email',
        })
    )
    phone = forms.CharField(
        max_length=17,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+1234567890',
        }),
        help_text="Format requis: +2126..."
    )
    country = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Pays',
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mot de passe',
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmer le mot de passe',
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('Cet email est déjà utilisé')
        return email
    
    def clean_username(self):
        username = self.cleaned_data['username']
        # Si le nom d'utilisateur n'est pas vide, on vérifie s'il est unique
        if username:
            if CustomUser.objects.filter(username=username).exists():
                raise forms.ValidationError('Ce nom d\'utilisateur est déjà pris')
        return username

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Nettoyage basique avant vérification
            phone = phone.strip().replace(' ', '')
            if CustomUser.objects.filter(phone=phone).exists():
                raise forms.ValidationError('Ce numéro de téléphone est déjà utilisé par un autre compte.')
        return phone
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Les mots de passe ne correspondent pas')
        
        return cleaned_data


class UserProfileForm(forms.ModelForm):
    """Formulaire de mise à jour du profil"""
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'phone', 'address', 'city', 'country', 'avatar', 'date_of_birth']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
