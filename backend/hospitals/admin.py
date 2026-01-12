from django.contrib import admin
from .models import Hospital, Department, Doctor, Staff, Bed, City
from appointments.models import Appointment
from core.models import Vitals
from accounts.models import User

admin.site.register(Hospital)
admin.site.register(Department)
admin.site.register(Doctor)
admin.site.register(Staff)
admin.site.register(Bed)
admin.site.register(City)
admin.site.register(Appointment)
admin.site.register(Vitals)
