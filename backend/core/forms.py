from django import forms
from .models import Vitals

class VitalsForm(forms.ModelForm):
    class Meta:
        model = Vitals
        fields = ['height', 'weight', 'bp_systolic', 'bp_diastolic', 'heart_rate', 'temperature']
        widgets = {
            'height': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'cm'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'kg'}),
            'bp_systolic': forms.NumberInput(attrs={'class': 'form-control'}),
            'bp_diastolic': forms.NumberInput(attrs={'class': 'form-control'}),
            'heart_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'temperature': forms.NumberInput(attrs={'class': 'form-control'}),
        }
