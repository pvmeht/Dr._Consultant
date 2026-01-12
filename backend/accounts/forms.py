from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import User

class UserRegistrationForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.Role.choices, initial=User.Role.PATIENT)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'role']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = self.cleaned_data['role'] # Use the selected role from the form
        if commit:
            user.save()
        return user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'style': 'width: 100%; padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box;'})

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'dob', 'gender', 'blood_group', 'address', 'emergency_contact']
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }
