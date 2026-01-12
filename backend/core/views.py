from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import get_user_model

User = get_user_model()

def index(request):
    return render(request, 'index.html')

from appointments.models import Appointment
from hospitals.models import Doctor, Hospital, City

@login_required
def dashboard_dispatch(request):
    user = request.user
    if user.role == User.Role.PATIENT:
        return redirect('patient_dashboard')
    elif user.role == User.Role.HOSPITAL:
        return redirect('hospital_dashboard')
    elif user.is_staff or user.role == User.Role.ADMIN:
        return redirect('admin_dashboard')
    elif user.role == User.Role.DOCTOR:
        # Fallback for doctors if needed, or redirect to a doctor dashboard
        # For now, maybe index or hospital dashboard
        return redirect('index') 
    return redirect('index')

@login_required
def patient_dashboard(request):
    appointments = Appointment.objects.filter(patient=request.user).select_related('doctor', 'doctor__hospital', 'doctor__hospital__city').order_by('date', 'time')
    return render(request, 'dashboard/patient_dashboard.html', {'appointments': appointments})

@login_required
def hospital_dashboard(request):
    # Check if user is hospital admin
    if not hasattr(request.user, 'hospital_managed'):
        return render(request, 'dashboard/error.html', {'message': 'No Hospital Profile found. Please contact Admin.'})
    
    hospital = request.user.hospital_managed
    
    if not hospital.is_verified:
        return render(request, 'dashboard/hospital_verification_pending.html', {'hospital': hospital})
        
    doctors = Doctor.objects.filter(hospital=hospital)
    # appointments = Appointment.objects.filter(doctor__hospital=hospital).order_by('date', 'time')
    
    # Group Appointments
    all_appointments = Appointment.objects.filter(doctor__hospital=hospital).order_by('date', 'time')
    pending_appointments = all_appointments.filter(status=Appointment.Status.PENDING)
    confirmed_appointments = all_appointments.filter(status=Appointment.Status.CONFIRMED)
    completed_appointments = all_appointments.filter(status=Appointment.Status.COMPLETED)
    cancelled_appointments = all_appointments.filter(status=Appointment.Status.CANCELLED)
    
    from hospitals.models import Staff, Bed
    staff = Staff.objects.filter(hospital=hospital)
    beds = Bed.objects.filter(hospital=hospital)
    
    return render(request, 'dashboard/hospital_dashboard.html', {
        'hospital': hospital,
        'doctors': doctors,
        'appointments': all_appointments, # Keep for overview stats
        'pending_appointments': pending_appointments,
        'confirmed_appointments': confirmed_appointments,
        'completed_appointments': completed_appointments,
        'cancelled_appointments': cancelled_appointments,
        'staff': staff,
        'beds': beds
    })

from .models import Vitals
from .forms import VitalsForm
from hospitals.forms import HospitalForm
from hospitals.models import Hospital
from accounts.models import User
from django.contrib import messages

@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('index')
    
    total_hospitals = Hospital.objects.count()
    total_doctors = User.objects.filter(role=User.Role.DOCTOR).count()
    total_patients = User.objects.filter(role=User.Role.PATIENT).count()
    
    recent_users = User.objects.order_by('-date_joined')[:5]
    unverified_hospitals = Hospital.objects.filter(is_verified=False)
    
    # Users who are HOSPITAL role but have no Hospital profile linkage
    orphaned_users = User.objects.filter(role=User.Role.HOSPITAL, hospital_managed__isnull=True)
    
    return render(request, 'dashboard/admin_dashboard.html', {
        'total_hospitals': total_hospitals,
        'total_doctors': total_doctors,
        'total_patients': total_patients,
        'recent_users': recent_users,
        'unverified_hospitals': unverified_hospitals,
        'orphaned_users': orphaned_users
    })

@login_required
def verify_hospital(request, hospital_id):
    if not request.user.is_staff:
        return redirect('index')
    
    try:
        hospital = Hospital.objects.get(id=hospital_id)
        hospital.is_verified = True
        hospital.save()
        messages.success(request, f"{hospital.name} verified successfully.")
    except Hospital.DoesNotExist:
        messages.error(request, "Hospital not found.")
        
    return redirect('admin_dashboard')

@login_required
def add_hospital(request):
    if not request.user.is_staff:
        return redirect('index')
    
    if request.method == 'POST':
        form = HospitalForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists")
            else:
                user = User.objects.create_user(username=username, password=password, role=User.Role.HOSPITAL)
                hospital = form.save(commit=False)
                hospital.admin = user
                hospital.save()
                messages.success(request, "Hospital Added Successfully")
                return redirect('admin_dashboard')
    else:
        form = HospitalForm()
    
    return render(request, 'dashboard/add_hospital.html', {'form': form})

@login_required
def vitals_view(request):
    if request.user.role != User.Role.PATIENT:
        return redirect('index')
    
    if request.method == 'POST':
        form = VitalsForm(request.POST)
        if form.is_valid():
            vitals = form.save(commit=False)
            vitals.patient = request.user
            vitals.save()
            messages.success(request, "Vitals Recorded")
            return redirect('patient_dashboard')
    else:
        form = VitalsForm()
    
    
    # Get previous vitals to display
    history = Vitals.objects.filter(patient=request.user).order_by('-date')
    
    return render(request, 'dashboard/vitals.html', {'form': form, 'history': history})

@login_required
def update_hospital_info(request):
    if not hasattr(request.user, 'hospital_managed'):
        return redirect('index')
    
    if request.method == 'POST':
        hospital = request.user.hospital_managed
        hospital.name = request.POST.get('name')
        hospital.address = request.POST.get('address')
        hospital.phone = request.POST.get('phone')
        hospital.email = request.POST.get('email')
        hospital.save()
        messages.success(request, "Hospital Details Updated")
    
    return redirect('hospital_dashboard')

    return redirect('hospital_dashboard')

@login_required
def add_doctor(request):
    if not hasattr(request.user, 'hospital_managed'): return redirect('index')
    
    if request.method == 'POST':
        fname = request.POST.get('first_name')
        lname = request.POST.get('last_name')
        specialization = request.POST.get('specialization')
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Simple validation
        if User.objects.filter(username=username).exists():
             messages.error(request, "Username already exists")
        else:
             # Create User
             user = User.objects.create_user(username=username, password=password, first_name=fname, last_name=lname, role=User.Role.DOCTOR)
             
             # Create Doctor Profile
             from hospitals.models import Doctor
             Doctor.objects.create(
                 user=user,
                 hospital=request.user.hospital_managed,
                 specialization=specialization
             )
             messages.success(request, f"Dr. {fname} {lname} added successfully!")
             
    return redirect('hospital_dashboard')

@login_required
def add_staff(request):
    if not hasattr(request.user, 'hospital_managed'): return redirect('index')
    
    if request.method == 'POST':
        from hospitals.models import Staff
        Staff.objects.create(
            hospital=request.user.hospital_managed,
            name=request.POST.get('name'),
            role=request.POST.get('role'),
            phone=request.POST.get('phone')
        )
        messages.success(request, "Staff Added")
        
    return redirect('hospital_dashboard')

@login_required
def add_bed(request):
    if not hasattr(request.user, 'hospital_managed'): return redirect('index')
    
    if request.method == 'POST':
        from hospitals.models import Bed
        Bed.objects.create(
            hospital=request.user.hospital_managed,
            ward=request.POST.get('ward'),
            number=request.POST.get('number')
        )
        messages.success(request, "Bed Added")
        
    return redirect('hospital_dashboard')

@login_required
def toggle_bed(request, bed_id):
    if not hasattr(request.user, 'hospital_managed'): return redirect('index')
    
    from hospitals.models import Bed
    try:
        bed = Bed.objects.get(id=bed_id, hospital=request.user.hospital_managed)
        bed.is_occupied = not bed.is_occupied
        bed.save()
        messages.success(request, "Bed Status Updated")
    except Bed.DoesNotExist:
        pass
        
    return redirect('hospital_dashboard')

@login_required
def create_hospital_profile(request, user_id):
    if not request.user.is_staff: return redirect('index')
    
    target_user = User.objects.get(id=user_id)
    from hospitals.forms import HospitalProfileForm
    
    if request.method == 'POST':
        form = HospitalProfileForm(request.POST)
        if form.is_valid():
            hospital = form.save(commit=False)
            hospital.admin = target_user
            hospital.is_verified = True # Admin creating it implies verification
            hospital.save()
            messages.success(request, f"Hospital Profile created for {target_user.username}")
            return redirect('admin_dashboard')
    else:
        form = HospitalProfileForm()

    return render(request, 'dashboard/create_hospital_profile.html', {'form': form, 'target_user': target_user})

def get_cities(request):
    state = request.GET.get('state')
    cities = City.objects.filter(state=state).values('id', 'name')
    return JsonResponse(list(cities), safe=False)

def get_hospitals(request):
    city_id = request.GET.get('city')
    hospitals = Hospital.objects.filter(city_id=city_id, is_verified=True).values('id', 'name')
    return JsonResponse(list(hospitals), safe=False)

def get_doctors(request):
    hospital_id = request.GET.get('hospital')
    doctors = Doctor.objects.filter(hospital_id=hospital_id).select_related('user').values('id', 'user__username', 'specialization', 'user__first_name', 'user__last_name')
    
    # Format name better
    data = []
    for doc in doctors:
        name = f"Dr. {doc['user__first_name']} {doc['user__last_name']}" if doc['user__first_name'] else f"Dr. {doc['user__username']}"
        data.append({
            'id': doc['id'],
            'name': name,
            'specialization': doc['specialization']
        })
    return JsonResponse(data, safe=False)

@login_required
def update_apt_status(request, apt_id):
    if not hasattr(request.user, 'hospital_managed'): return redirect('index')
    
    if request.method == 'POST':
        from appointments.models import Appointment
        try:
            apt = Appointment.objects.get(id=apt_id, doctor__hospital=request.user.hospital_managed)
            new_status = request.POST.get('status')
            if new_status in Appointment.Status.values:
                apt.status = new_status
                apt.save()
                messages.success(request, f"Appointment status updated to {new_status}")
        except Appointment.DoesNotExist:
            pass
            
    return redirect('hospital_dashboard')

@login_required
def consultation_view(request, apt_id):
    if not hasattr(request.user, 'hospital_managed'): return redirect('index')
    
    from appointments.models import Appointment, Consultation, Prescription
    try:
        apt = Appointment.objects.get(id=apt_id, doctor__hospital=request.user.hospital_managed)
    except Appointment.DoesNotExist:
        return redirect('hospital_dashboard')
        
    # Get or Create Consultation
    consultation, created = Consultation.objects.get_or_create(appointment=apt)
    
    if request.method == 'POST':
        # Update Consultation Details
        consultation.nurse_name = request.POST.get('nurse_name')
        consultation.bp = request.POST.get('bp')
        consultation.pulse = request.POST.get('pulse')
        consultation.temperature = request.POST.get('temperature')
        consultation.weight = request.POST.get('weight')
        consultation.symptoms = request.POST.get('symptoms')
        consultation.diagnosis = request.POST.get('diagnosis')
        consultation.advice = request.POST.get('advice')
        consultation.save()
        
        # Also save to Patient's Vital History
        # We need to parse BP (120/80) to systolic/diastolic
        bp_val = request.POST.get('bp', '')
        pulse_val = request.POST.get('pulse')
        temp_val = request.POST.get('temperature')
        weight_val = request.POST.get('weight')
        
        if bp_val or pulse_val or temp_val or weight_val:
            from core.models import Vitals as VitalsHistory
            
            sys = 0
            dia = 0
            if '/' in bp_val:
                try:
                    parts = bp_val.split('/')
                    sys = int(parts[0])
                    dia = int(parts[1])
                except ValueError:
                    pass
            
            # Simple sanitization
            try: hr = int(pulse_val) if pulse_val else 0
            except: hr = 0
            
            try: temp = float(temp_val) if temp_val else 0.0
            except: temp = 0.0
            
            try: wt = float(weight_val) if weight_val else 0.0
            except: wt = 0.0
            
            # Create History Record (Always create new for history tracking, or update if we want 'latest'? History is better)
            # To avoid spamming history on every 'Save Draft', maybe only do it on 'Complete'? 
            # Or check if one exists for today?
            # User requirement: "like we have entered vitals then have to add it into vital table"
            # Let's save it.
            
            VitalsHistory.objects.create(
                patient=apt.patient,
                height=0, # Not captured in consultation currently
                weight=wt,
                bp_systolic=sys,
                bp_diastolic=dia,
                heart_rate=hr,
                temperature=temp,
                hospital=request.user.hospital_managed
            )
        
        # Handle Prescription (Simplified: assume one item add or bulk text for now? 
        # Requirement said: "medicine name , doses, duration, instructions, prescribed date"
        # To handle multiple meds in one go without a complex JS formset, let's assume specific fields or just one med for MVP?
        # Better: Javascript to add rows, and backend reads arrays.
        
        med_names = request.POST.getlist('med_name[]')
        dosages = request.POST.getlist('dosage[]')
        durations = request.POST.getlist('duration[]')
        instructions = request.POST.getlist('instruction[]')
        
        # Clear old prescriptions to avoid duplication on edit? Or append? 
        # For simplicity in this session, we wipe and recreate if safe, or just add new.
        # Let's wipe to ensure the form reflects current state.
        consultation.prescriptions.all().delete()
        
        for i in range(len(med_names)):
            if med_names[i]:
                Prescription.objects.create(
                    consultation=consultation,
                    medicine_name=med_names[i],
                    dosage=dosages[i] if i < len(dosages) else '',
                    duration=durations[i] if i < len(durations) else '',
                    instructions=instructions[i] if i < len(instructions) else ''
                )
        
        # Mark as Completed if requested
        if 'complete_consultation' in request.POST:
            from django.utils import timezone
            consultation.completed_at = timezone.now()
            consultation.save()
            
            apt.status = Appointment.Status.COMPLETED
            apt.save()
            messages.success(request, "Consultation Completed Successfully")
            return redirect('hospital_dashboard')
            
        messages.success(request, "Consultation Saved")
        
    return render(request, 'dashboard/consultation_form.html', {'apt': apt, 'consultation': consultation})
    return render(request, 'dashboard/consultation_form.html', {'apt': apt, 'consultation': consultation})

@login_required
def appointment_detail_view(request, apt_id):
    from appointments.models import Appointment
    
    try:
        apt = Appointment.objects.get(id=apt_id)
    except Appointment.DoesNotExist:
         return redirect('index')

    # Authorization Check
    is_hospital = hasattr(request.user, 'hospital_managed') and apt.doctor.hospital == request.user.hospital_managed
    is_patient = request.user == apt.patient
    
    if not (is_hospital or is_patient):
        return redirect('index')

    consultation = getattr(apt, 'consultation', None)
    
    # Health Calculation Algorithm
    health_status = None
    health_color = "secondary"
    health_msg = ""
    
    if consultation:
        # 1. Parse BP
        sys, dia = 0, 0
        bp_score = 100
        if consultation.bp and '/' in consultation.bp:
            try:
                sys, dia = map(int, consultation.bp.split('/'))
                if sys > 140 or sys < 90 or dia > 90 or dia < 60:
                    bp_score = 50
                    health_msg += "Blood Pressure is irregualr. "
            except: pass
            
        # 2. Temperature
        temp_score = 100
        try:
            t = float(consultation.temperature) if consultation.temperature else 98.6
            if t > 99.5: 
                temp_score = 60
                health_msg += "Fever detected. "
        except: pass
        
        # 3. Pulse
        pulse_score = 100
        try:
            p = int(consultation.pulse) if consultation.pulse else 72
            if p > 100 or p < 60: 
                pulse_score = 70
                health_msg += "Pulse rate abnormal. "
        except: pass
        
        # Calculate Overall
        score = (bp_score + temp_score + pulse_score) / 3
        
        if score >= 90:
            health_status = "Excellent"
            health_color = "success"
            if not health_msg: health_msg = "Vitals are within healthy range."
        elif score >= 70:
            health_status = "Good"
            health_color = "info"
        elif score >= 50:
            health_status = "Needs Attention"
            health_color = "warning"
        else:
            health_status = "Critical"
            health_color = "danger"
            
    return render(request, 'dashboard/appointment_detail.html', {
        'apt': apt, 
        'consultation': consultation, 
        'is_patient': is_patient,
        'health_status': health_status,
        'health_color': health_color,
        'health_msg': health_msg,
        'patient_age': apt.patient.age
    })

@login_required
def patient_history(request):
    if request.user.role != User.Role.PATIENT:
        return redirect('index')
        
    from appointments.models import Appointment
    # Fetch Completed and Cancelled appointments
    history = Appointment.objects.filter(patient=request.user, status__in=[Appointment.Status.COMPLETED, Appointment.Status.CANCELLED]).order_by('-date', '-time')
    
    return render(request, 'dashboard/patient_history.html', {'history': history})
    return render(request, 'dashboard/patient_history.html', {'history': history})

@login_required
def patient_profile(request):
    if request.user.role != User.Role.PATIENT:
        return redirect('index')
    
    from accounts.forms import UserUpdateForm
    
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile Updated Successfully")
            return redirect('patient_profile')
    else:
        form = UserUpdateForm(instance=request.user)
    
    return render(request, 'dashboard/patient_profile.html', {'form': form})

@login_required
def admin_hospitals(request):
    if not request.user.is_staff: return redirect('index')
    hospitals = Hospital.objects.all().order_by('-id')
    return render(request, 'dashboard/admin_list_hospitals.html', {'hospitals': hospitals})

@login_required
def admin_doctors(request):
    if not request.user.is_staff: return redirect('index')
    doctors = Doctor.objects.select_related('user', 'hospital').all().order_by('-user__date_joined')
    return render(request, 'dashboard/admin_list_doctors.html', {'doctors': doctors})

@login_required
def admin_patients(request):
    if not request.user.is_staff: return redirect('index')
    patients = User.objects.filter(role=User.Role.PATIENT).order_by('-date_joined')
    return render(request, 'dashboard/admin_list_patients.html', {'patients': patients})
