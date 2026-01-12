from hospitals.models import City

cities = [
    "Mumbai", "Pune", "Nagpur", "Thane", "Nashik", "Aurangabad", "Solapur", 
    "Amravati", "Nanded", "Kolhapur", "Sangli", "Jalgaon", "Akola", "Latur", 
    "Dhule", "Ahmednagar", "Chandrapur", "Parbhani", "Ichalkaranji", "Jalna", 
    "Bhusawal", "Navi Mumbai", "Panvel", "Vasai-Virar", "Malegaon"
]

for name in cities:
    City.objects.get_or_create(name=name)

print(f"Successfully populated {len(cities)} cities from Maharashtra.")
