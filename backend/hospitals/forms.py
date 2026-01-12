from django import forms
from .models import Hospital, City, Staff, Bed
from accounts.models import User

class HospitalForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    city = forms.ModelChoiceField(queryset=City.objects.all(), empty_label="Select City")

    class Meta:
        model = Hospital
        fields = ['name', 'city', 'address', 'phone', 'email', 'website']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
        }
    
class HospitalProfileForm(forms.ModelForm):
    city = forms.ModelChoiceField(queryset=City.objects.all(), empty_label="Select City")
    class Meta:
        model = Hospital
        fields = ['name', 'city', 'address', 'phone', 'email', 'website']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
        }

class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['name', 'role', 'phone']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }

class BedForm(forms.ModelForm):
    class Meta:
        model = Bed
        fields = ['ward', 'number', 'is_occupied']
        widgets = {
            'ward': forms.TextInput(attrs={'class': 'form-control'}),
            'number': forms.TextInput(attrs={'class': 'form-control'}),
            'is_occupied': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
