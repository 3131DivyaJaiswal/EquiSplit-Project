from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Group, Expense, UserProfile

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', "group_image",'members']
        widgets = {'members': forms.CheckboxSelectMultiple}

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['description', 'amount', 'paid_by', 'participants']
        widgets = {
            'participants': forms.CheckboxSelectMultiple,
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'profile_image', 'phone_number', 'gender', 'address', 'pincode', 
            'upi_id', 'whatsapp_number'
        ]
        widgets = {
            'gender': forms.Select(choices=UserProfile.GENDER_CHOICES, attrs={'class': 'form-select'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'pincode': forms.TextInput(attrs={'class': 'form-control'}),
            'upi_id': forms.TextInput(attrs={'class': 'form-control'}),
            'whatsapp_number': forms.TextInput(attrs={'class': 'form-control'}),
        }
