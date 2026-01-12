
import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HealthCO.settings')
django.setup()

from django.contrib.auth import get_user_model
from hospitals.models import City, Hospital, Doctor, Department, Staff, Bed
from api.serializers import UserSerializer # Just to ensure app registry is fine

User = get_user_model()

def populate():
    # 1. Ensure City (Pune, Maharashtra)
    pune, created = City.objects.get_or_create(name='Pune', defaults={'state': 'Maharashtra'})
    if created:
        print("Created City: Pune")
    else:
        # Update state if it was old entry
        pune.state = 'Maharashtra'
        pune.save()
        print("Updated City: Pune")

    # 2. Departments
    depts_names = ['Cardiology', 'Orthopedics', 'Pediatrics', 'General', 'Neurology']
    
    # 3. Hospitals Data
    hospitals_data = [
        {
            'name': 'YCM Hospital',
            'username': 'ycm_admin',
            'email': 'admin@ycm.com',
            'address': 'Pimpri, Pune',
            'phone': '020-12345678',
            'website': 'https://ycm.pimpri.org'
        },
        {
            'name': 'Ruby Hall Clinic',
            'username': 'ruby_admin',
            'email': 'admin@rubyhall.com',
            'address': 'Sassoon Road, Pune',
            'phone': '020-87654321',
            'website': 'https://rubyhall.com'
        },
        {
            'name': 'Dr. D.Y. Patil Hospital',
            'username': 'dy_admin',
            'email': 'admin@dypatil.com',
            'address': 'Pimpri, Pune',
            'phone': '020-11223344',
            'website': 'https://dypatil.edu'
        }
    ]

    for h_data in hospitals_data:
        # Create User
        if not User.objects.filter(username=h_data['username']).exists():
            user = User.objects.create_user(
                username=h_data['username'], 
                email=h_data['email'], 
                password='password123', 
                role=User.Role.HOSPITAL
            )
            print(f"Created User: {h_data['username']}")
        else:
            user = User.objects.get(username=h_data['username'])
            print(f"User exists: {h_data['username']}")

        # Create Hospital Profile
        hospital, created = Hospital.objects.get_or_create(admin=user, defaults={
            'name': h_data['name'],
            'city': pune,
            'address': h_data['address'],
            'phone': h_data['phone'],
            'website': h_data['website'],
            'is_verified': True 
        })
        if created:
            print(f"Created Hospital: {h_data['name']}")
        else:
            hospital.is_verified = True # Ensure verified
            hospital.save()
            print(f"Verified Hospital: {h_data['name']}")

    # Create Departments for this hospital
        for d_name in depts_names:
            dept, _ = Department.objects.get_or_create(hospital=hospital, name=d_name)

        # Standard Specializations cycle
        specializations = [
            'General Physician', 'Cardiologist', 'Dermatologist', 'Pediatrician',
            'Neurologist', 'The Gynecologist', 'Orthopedist', 'Surgeon',
            'Psychiatrist', 'ENT Specialist', 'Ophthalmologist', 'Dentist'
        ]
        
        # Create 3-4 Doctors per hospital with random specialization
        for i in range(4):
            val_spec = random.choice(specializations)
            doc_username = f"dr_{h_data['username']}_{i}"
            
            if not User.objects.filter(username=doc_username).exists():
                doc_user = User.objects.create_user(
                    username=doc_username,
                    password='password123',
                    role=User.Role.DOCTOR,
                    first_name=f"Doctor",
                    last_name=f"{i+1} ({h_data['name'].split()[0]})"
                )
                
                Doctor.objects.create(
                    user=doc_user,
                    hospital=hospital,
                    specialization=val_spec
                )
                print(f"  Created Doctor: {doc_username} - {val_spec}")
        
    # Explicitly Add Dr. Saurabh for Ruby Hall Clinic as per request
    ruby = Hospital.objects.filter(name='Ruby Hall Clinic').first()
    if ruby:
        saurabh_user, created = User.objects.get_or_create(username='dr_saurabh', defaults={
            'email': 'saurabh@ruby.com',
            'role': User.Role.DOCTOR,
            'first_name': 'Saurabh',
            'last_name': 'Patil'
        })
        if created:
            saurabh_user.set_password('password123')
            saurabh_user.save()
            Doctor.objects.create(
                user=saurabh_user,
                hospital=ruby,
                specialization='Cardiologist'
            )
            print("Explicitly Added Dr. Saurabh to Ruby Hall Clinic")

if __name__ == '__main__':
    populate()
