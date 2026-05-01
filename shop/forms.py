from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from .models import Order, Profile

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone must be in format: '+999999999'."
    )
    
    phone_number = forms.CharField(
        validators=[phone_regex], 
        max_length=17, 
        required=True, 
        label="Phone number"
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

    def save(self, commit=True):
        user = super().save(commit=commit)
        phone = self.cleaned_data.get('phone_number')
        Profile.objects.create(user=user, phone_number=phone)
        return user

class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name','email', 'phone', 'address'] # Поля, які ми хочемо від юзера

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your first name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your last name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
        }

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone_number']
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': '+380...',
            }),
        }