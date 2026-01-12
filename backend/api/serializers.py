from rest_framework import serializers
from django.contrib.auth import get_user_model
from hospitals.models import Doctor, Hospital, Department, Staff, Bed
from appointments.models import Appointment

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']

class DoctorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    hospital_name = serializers.CharField(source='hospital.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = Doctor
        fields = ['id', 'user', 'hospital_name', 'department_name', 'specialization', 'available']

class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = ['id', 'name', 'role', 'phone']

class BedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bed
        fields = ['id', 'ward', 'number', 'is_occupied']

class HospitalDetailSerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(source='city.name', read_only=True)
    class Meta:
        model = Hospital
        fields = ['id', 'name', 'city', 'city_name', 'address', 'phone', 'email', 'website']

class PatientProfileSerializer(serializers.ModelSerializer):
    age = serializers.ReadOnlyField()
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'phone', 'dob', 'age', 'gender', 'blood_group', 'address', 'emergency_contact']

class AppointmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    patient_details = PatientProfileSerializer(source='patient', read_only=True)
    doctor_name = serializers.CharField(source='doctor.user.get_full_name', read_only=True)
    
    class Meta:
        model = Appointment
        fields = ['id', 'patient', 'doctor', 'patient_name', 'patient_details', 'doctor_name', 'date', 'time', 'status', 'notes']

from appointments.models import Consultation, Prescription

class PrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = ['id', 'medicine_name', 'dosage', 'duration', 'instructions']

class ConsultationSerializer(serializers.ModelSerializer):
    prescriptions = PrescriptionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Consultation
        fields = ['id', 'appointment', 'started_at', 'nurse_name', 'bp', 'pulse', 'temperature', 'weight', 'height', 'symptoms', 'diagnosis', 'advice', 'completed_at', 'prescriptions']
