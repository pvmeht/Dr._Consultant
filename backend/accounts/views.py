from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import UserRegistrationForm

from django.contrib.auth.views import LoginView

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            
            # Check for guest appointment data
            if 'guest_appointment_data' in request.session:
                try:
                    data = request.session.pop('guest_appointment_data')
                    from appointments.models import Appointment
                    from hospitals.models import Doctor
                    
                    Appointment.objects.create(
                        patient=user,
                        doctor_id=data['doctor_id'],
                        date=data['date'],
                        time=data['time'],
                        notes=data['notes'],
                        status=Appointment.Status.PENDING
                    )
                    from django.contrib import messages
                    messages.success(request, "Registration Successful! Your appointment has been booked.")
                    return redirect('patient_dashboard')
                except Exception as e:
                    print(f"Error booking guest appointment: {e}")
                    return redirect('patient_dashboard') # Redirect anyway
            
            return redirect('/')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    
    def form_valid(self, form):
        # Remember Me Logic
        remember_me = self.request.POST.get('remember_me')
        if not remember_me:
            # Expire session on browser close
            self.request.session.set_expiry(0)
        else:
            # Set expiry to 2 weeks (default or specific)
            self.request.session.set_expiry(1209600) 
        return super().form_valid(form)
