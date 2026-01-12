from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views as auth_views
from .views import (
    UserViewSet, DoctorViewSet, AppointmentViewSet, RegisterViewSet, 
    StaffViewSet, BedViewSet, HospitalDataViewSet, StaffRoleView, ConsultationViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'doctors', DoctorViewSet)
router.register(r'appointments', AppointmentViewSet)
router.register(r'staff', StaffViewSet, basename='staff')
router.register(r'beds', BedViewSet, basename='beds')
router.register(r'hospital-details', HospitalDataViewSet, basename='hospital-details')
router.register(r'consultations', ConsultationViewSet, basename='consultations')
router.register(r'register', RegisterViewSet, basename='register')

urlpatterns = [
    path('api-token-auth/', auth_views.obtain_auth_token),
    path('staff-roles/', StaffRoleView.as_view(), name='staff-roles'),
    path('', include(router.urls)),
]
