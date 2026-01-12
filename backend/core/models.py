from django.db import models
from django.conf import settings

class Vitals(models.Model):
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vitals')
    date = models.DateTimeField(auto_now_add=True)
    height = models.FloatField(help_text="Height in cm")
    weight = models.FloatField(help_text="Weight in kg")
    bp_systolic = models.IntegerField(help_text="Systolic Blood Pressure (mmHg)")
    bp_diastolic = models.IntegerField(help_text="Diastolic Blood Pressure (mmHg)")
    heart_rate = models.IntegerField(help_text="Heart Rate (bpm)")
    temperature = models.FloatField(help_text="Temperature (Celsius)")
    
    # Added by Hospital tracking
    from hospitals.models import Hospital
    hospital = models.ForeignKey(Hospital, on_delete=models.SET_NULL, null=True, blank=True, related_name='recorded_vitals')

    def __str__(self):
        return f"Vitals for {self.patient} on {self.date.date()}"
