from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard_dispatch, name='dashboard_dispatch'),
    path('dashboard/patient/', views.patient_dashboard, name='patient_dashboard'),
    path('dashboard/hospital/', views.hospital_dashboard, name='hospital_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/hospital/update-info/', views.update_hospital_info, name='update_hospital_info'),
    path('dashboard/hospital/add-staff/', views.add_staff, name='add_staff'),
    path('dashboard/hospital/add-doctor/', views.add_doctor, name='add_doctor'),
    path('dashboard/hospital/add-bed/', views.add_bed, name='add_bed'),
    path('dashboard/hospital/toggle-bed/<int:bed_id>/', views.toggle_bed, name='toggle_bed'),
    path('dashboard/admin/add-hospital/', views.add_hospital, name='add_hospital'),
    path('dashboard/admin/create-profile/<int:user_id>/', views.create_hospital_profile, name='create_hospital_profile'),
    path('dashboard/admin/verify/<int:hospital_id>/', views.verify_hospital, name='verify_hospital'),
    
    path('dashboard/admin/hospitals/', views.admin_hospitals, name='admin_hospitals'),
    path('dashboard/admin/doctors/', views.admin_doctors, name='admin_doctors'),
    path('dashboard/admin/patients/', views.admin_patients, name='admin_patients'),
    path('dashboard/vitals/', views.vitals_view, name='vitals'),
    
    path('dashboard/patient/history/', views.patient_history, name='patient_history'),
    path('dashboard/patient/profile/', views.patient_profile, name='patient_profile'),
    path('dashboard/hospital/apt/<int:apt_id>/status/', views.update_apt_status, name='update_apt_status'),
    path('dashboard/hospital/consultation/<int:apt_id>/', views.consultation_view, name='consultation_view'),
    path('dashboard/hospital/appointment/<int:apt_id>/details/', views.appointment_detail_view, name='appointment_detail'),
    
    # AJAX
    path('ajax/cities/', views.get_cities, name='ajax_cities'),
    path('ajax/hospitals/', views.get_hospitals, name='ajax_hospitals'),
    path('ajax/doctors/', views.get_doctors, name='ajax_doctors'),
]
