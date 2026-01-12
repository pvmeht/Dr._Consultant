
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from hospitals.models import Doctor, Staff, Bed, Hospital
from appointments.models import Appointment
from .serializers import UserSerializer, DoctorSerializer, AppointmentSerializer, StaffSerializer, BedSerializer, HospitalDetailSerializer

User = get_user_model()

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated]

class RegisterViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [] # Allow anonymous registration

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.set_password(request.data['password'])
        user.save()
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "message": "User Created Successfully.  Now perform Login to get your token",
        })

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == User.Role.PATIENT:
            return Appointment.objects.filter(patient=user)
        elif user.role == User.Role.DOCTOR:
             # Assuming doctor profile exists
             return Appointment.objects.filter(doctor__user=user)
        elif user.role == User.Role.HOSPITAL:
             return Appointment.objects.filter(doctor__hospital__admin=user)
class StaffViewSet(viewsets.ModelViewSet):
    serializer_class = StaffSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == User.Role.HOSPITAL:
            return Staff.objects.filter(hospital__admin=user)
        return Staff.objects.none()
    
    def perform_create(self, serializer):
        if self.request.user.role == User.Role.HOSPITAL:
            serializer.save(hospital=self.request.user.hospital_managed)

class BedViewSet(viewsets.ModelViewSet):
    serializer_class = BedSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == User.Role.HOSPITAL:
            return Bed.objects.filter(hospital__admin=user)
        return Bed.objects.none()
    
    def perform_create(self, serializer):
        if self.request.user.role == User.Role.HOSPITAL:
            serializer.save(hospital=self.request.user.hospital_managed)

class HospitalDataViewSet(viewsets.ModelViewSet):
    serializer_class = HospitalDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
         if hasattr(self.request.user, 'hospital_managed'):
             return Hospital.objects.filter(admin=self.request.user)
         return Hospital.objects.none()

class StaffRoleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from hospitals.models import Staff
        roles = [choice[0] for choice in Staff.Role.choices]
        return Response(roles)

from appointments.models import Consultation, Prescription
from .serializers import ConsultationSerializer

class ConsultationViewSet(viewsets.ModelViewSet):
    queryset = Consultation.objects.all()
    serializer_class = ConsultationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only show consultations for hospital's doctors
        user = self.request.user
        if hasattr(user, 'hospital_managed'):
            return Consultation.objects.filter(appointment__doctor__hospital=user.hospital_managed)
        return Consultation.objects.none()

    def create(self, request, *args, **kwargs):
        # Custom create to handle vitals sync and prescriptions
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        consultation = serializer.save()

        # Handle Prescriptions
        prescriptions_data = data.get('prescriptions_data', [])
        for pres_item in prescriptions_data:
            Prescription.objects.create(consultation=consultation, **pres_item)
            
        # Handle Vitals Sync (Same logic as web view)
        self._sync_vitals(consultation, request.user)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        consultation = serializer.save()

        # Handle Prescriptions (Rewrite logic)
        if 'prescriptions_data' in request.data:
            consultation.prescriptions.all().delete()
            prescriptions_data = request.data.get('prescriptions_data', [])
            for pres_item in prescriptions_data:
                Prescription.objects.create(consultation=consultation, **pres_item)

        return Response(serializer.data)

    def _sync_vitals(self, consultation, user):
        # Sync logic here
        from core.models import Vitals as VitalsHistory
        # Basic parsing
        try:
             bp_val = consultation.bp
             sys, dia = 0, 0
             if bp_val and '/' in bp_val:
                 sys, dia = map(int, bp_val.split('/'))
             
             if consultation.weight or consultation.bp:
                 VitalsHistory.objects.create(
                     patient=consultation.appointment.patient,
                     height=0,
                     weight=float(consultation.weight) if consultation.weight else 0,
                     bp_systolic=sys,
                     bp_diastolic=dia,
                     heart_rate=int(consultation.pulse) if consultation.pulse else 0,
                     temperature=float(consultation.temperature) if consultation.temperature else 0,
                     hospital=user.hospital_managed if hasattr(user, 'hospital_managed') else None
                 )
        except Exception as e:
            print(f"Error syncing vitals: {e}")
