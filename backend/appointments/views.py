from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import AppointmentForm
from django.contrib import messages
from accounts.models import User

# @login_required # Removed decorator to allow guest access
def book_appointment(request):
    if request.user.is_authenticated and request.user.role != User.Role.PATIENT:
        return redirect('index')
        
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            if request.user.is_authenticated:
                apt = form.save(commit=False)
                apt.patient = request.user
                apt.save()
                messages.success(request, "Appointment Booked Successfully")
                return redirect('patient_dashboard')
            else:
                # Guest Flow: Store details in session and redirect to register
                booking_data = {
                    'doctor_id': form.cleaned_data['doctor'].id,
                    'date': form.cleaned_data['date'].isoformat(),
                    'time': form.cleaned_data['time'].isoformat(),
                    'notes': form.cleaned_data['notes']
                }
                request.session['guest_appointment_data'] = booking_data
                messages.info(request, "Please register to confirm your appointment.")
                return redirect('register')
    else:
        form = AppointmentForm()
    
    from hospitals.models import City
    states = City.objects.order_by('state').values_list('state', flat=True).distinct()
    
    return render(request, 'appointments/book_appointment.html', {'form': form, 'states': states})
