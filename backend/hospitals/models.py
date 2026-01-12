from django.db import models
from django.conf import settings

class City(models.Model):
    name = models.CharField(max_length=100)
    state = models.CharField(max_length=100, default='Maharashtra')

    def __str__(self):
        return self.name

class Hospital(models.Model):
    name = models.CharField(max_length=255)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, related_name='hospitals')
    address = models.TextField()
    phone = models.CharField(max_length=20, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    admin = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='hospital_managed')
    is_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} ({self.city.name if self.city else 'No City'})"

class Department(models.Model):
    name = models.CharField(max_length=100)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='departments')

    def __str__(self):
        return f"{self.name} - {self.hospital.name}"

class Doctor(models.Model):
    SPECIALIZATION_CHOICES = [
        ('General Physician', 'General Physician'),
        ('Cardiologist', 'Cardiologist'),
        ('Dermatologist', 'Dermatologist'),
        ('Pediatrician', 'Pediatrician'),
        ('Neurologist', 'Neurologist'),
        ('The Gynecologist', 'The Gynecologist'),
        ('Orthopedist', 'Orthopedist'),
        ('Surgeon', 'Surgeon'),
        ('Psychiatrist', 'Psychiatrist'),
        ('ENT Specialist', 'ENT Specialist'),
        ('Ophthalmologist', 'Ophthalmologist'),
        ('Dentist', 'Dentist'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='doctor_profile')
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='doctors')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='doctors')
    specialization = models.CharField(max_length=100, choices=SPECIALIZATION_CHOICES, default='General Physician')
    available = models.BooleanField(default=True)

    def __str__(self):
        return f"Dr. {self.user.get_full_name()} ({self.specialization})"

class Staff(models.Model):
    class Role(models.TextChoices):
        DOCTOR = 'Doctor', 'Doctor'
        NURSE = 'Nurse', 'Nurse'
        COMPOUNDER = 'Compounder', 'Compounder'
        RECEPTIONIST = 'Receptionist', 'Receptionist'
        OTHER = 'Other', 'Other'

    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='staff')
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=100, choices=Role.choices, default=Role.OTHER)
    phone = models.CharField(max_length=20)
    
    def __str__(self):
        return f"{self.name} ({self.role})"

class Bed(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='beds')
    ward = models.CharField(max_length=100)
    number = models.CharField(max_length=20)
    is_occupied = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.ward} - {self.number}"
