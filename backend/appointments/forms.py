from django import forms
from .models import Appointment
from hospitals.models import Doctor

class AppointmentForm(forms.ModelForm):
    doctor = forms.ModelChoiceField(queryset=Doctor.objects.all(), empty_label="Select Doctor")
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))

    class Meta:
        model = Appointment
        fields = ['doctor', 'date', 'time', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].widget.attrs.update({'class': 'form-control'})
        self.fields['time'].widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')
        
        from django.utils import timezone
        import datetime
        
        if date and time:
            now = timezone.now()
            # Combine date and time to check strict future
            apt_datetime = datetime.datetime.combine(date, time)
            if timezone.is_aware(now):
                apt_datetime = timezone.make_aware(apt_datetime)
            
            if apt_datetime < now:
                raise forms.ValidationError("Appointment cannot be in the past.")
        
        return cleaned_data
