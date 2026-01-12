from django.db import models
from django.conf import settings
from hospitals.models import Doctor

class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        CONFIRMED = 'CONFIRMED', 'Confirmed'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Appointment: {self.patient} with {self.doctor} on {self.date}"

class Consultation(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='consultation')
    
    # Step 1: Session Details
    started_at = models.DateTimeField(auto_now_add=True)
    nurse_name = models.CharField(max_length=100, blank=True) # Could be ForeignKey to Staff
    
    # Step 2: Vitals at time of consultation
    bp = models.CharField(max_length=20, blank=True, null=True, verbose_name="Blood Pressure")
    pulse = models.CharField(max_length=20, blank=True, null=True)
    temperature = models.CharField(max_length=20, blank=True, null=True)
    weight = models.CharField(max_length=20, blank=True, null=True)
    height = models.CharField(max_length=20, blank=True, null=True, verbose_name="Height (ft)")
    
    # Step 3: Clinical
    symptoms = models.TextField(blank=True)
    diagnosis = models.TextField(blank=True)
    advice = models.TextField(blank=True)
    
    completed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Consultation for {self.appointment}"

class Prescription(models.Model):
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name='prescriptions')
    medicine_name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100) # e.g. "1-0-1"
    duration = models.CharField(max_length=100) # e.g. "5 days"
    instructions = models.TextField(blank=True) # e.g. "After food"
    
    def __str__(self):
        return self.medicine_name
