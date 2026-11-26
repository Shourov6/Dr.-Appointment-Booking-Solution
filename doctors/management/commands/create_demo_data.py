"""
Management command to create demo data for testing
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings
from datetime import date, time, timedelta
from decimal import Decimal

from doctors.models import (
    Doctor,
    Specialty,
    Hospital,
    DoctorAvailability,
    DoctorHospital,
    DoctorWeeklySchedule,
    Review,
)
from accounts.models import EmployeeProfile, PatientProfile
from appointments.models import Appointment, CartItem

User = get_user_model()


class Command(BaseCommand):
    help = 'Create demo data for testing the healthcare platform'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating demo data...'))
        self.create_admin()
        
        # Create demo hospitals
        hospitals = self.create_hospitals()
        
        # Create demo doctors
        doctors = self.create_doctors(hospitals)
        
        # Create demo availability
        self.create_availability(doctors, hospitals)
        self.create_weekly_schedules(doctors)
        
        # Create demo patient
        patient = self.create_patient()
        self.create_patient_dashboard_data(patient, doctors)
        
        # Create demo employees
        self.create_employees()
        
        # Create demo reviews
        self.create_reviews(doctors)
        
        # Create demo appointments
        self.create_appointments(patient, doctors, hospitals)
        self.assign_demo_appointments(patient)
        
        # Create demo payments
        self.create_payments()
        
        self.stdout.write(self.style.SUCCESS('\nAll demo data created successfully!'))
        self.stdout.write(self.style.WARNING('\nTest Credentials:'))
        self.stdout.write(self.style.WARNING('  Admin: admin.demo@gmail.com'))
        self.stdout.write(self.style.WARNING('  Patient: patient@gmail.com'))
        self.stdout.write(self.style.WARNING('  Doctor: dr.karim@gmail.com'))
        self.stdout.write(self.style.WARNING('  Employee: rahima@gmail.com'))
        self.stdout.write(self.style.WARNING(f'  Password: {settings.DEMO_LOGIN_PASSWORD}'))

    def create_admin(self):
        """Create a dedicated admin account for the demo environment."""
        user, created = User.objects.get_or_create(
            email='admin.demo@gmail.com',
            defaults={
                'username': 'demo_admin',
                'first_name': 'Demo',
                'last_name': 'Admin',
                'role': 'admin',
                'is_staff': False,
                'is_superuser': False,
                'is_verified': True,
            },
        )
        if created or user.username == 'demo_admin':
            user.role = 'admin'
            user.is_staff = False
            user.is_superuser = False
            user.is_verified = True
            user.set_password(settings.DEMO_LOGIN_PASSWORD)
            user.save()
        if created:
            self.stdout.write('  Created demo admin account')
    
    def create_hospitals(self):
        """Create demo hospitals"""
        hospitals_data = [
            {
                'name': 'Dhaka Medical College',
                'address': '123 Medical Plaza, Dhanmondi',
                'city': 'Dhaka',
                'district': 'Dhaka',
                'phone': '+8809678901',
                'email': 'info@dmc.gov.bd',
                'total_beds': 150,
                'icu_beds_available': 12,
            },
            {
                'name': 'Bangabandhu Sheikh Mujib Medical University',
                'address': '456 Health Avenue, Gulshan',
                'city': 'Dhaka',
                'district': 'Dhaka',
                'phone': '+8809678902',
                'email': 'info@bsmmu.edu.bd',
                'total_beds': 200,
                'icu_beds_available': 8,
            },
            {
                'name': 'Sir Salimullah Medical College',
                'address': '789 Care Street, Panthapath',
                'city': 'Dhaka',
                'district': 'Dhaka',
                'phone': '+8809678903',
                'email': 'info@smc.gov.bd',
                'total_beds': 120,
                'icu_beds_available': 15,
            },
            {
                'name': 'Chittagong Medical College',
                'address': '321 Hospital Road, Chittagong',
                'city': 'Chittagong',
                'district': 'Chittagong',
                'phone': '+8809678904',
                'email': 'info@cmc.gov.bd',
                'total_beds': 180,
                'icu_beds_available': 10,
            },
        ]
        
        hospitals = []
        for hospital_data in hospitals_data:
            hospital, created = Hospital.objects.get_or_create(
                name=hospital_data['name'],
                defaults=hospital_data
            )
            if created:
                self.stdout.write(f'  Created hospital: {hospital.name}')
            hospitals.append(hospital)
        
        return hospitals
    
    def create_doctors(self, hospitals):
        """Create demo doctors"""
        doctors_data = [
            {
                'first_name': 'Karim',
                'last_name': 'Ahmed',
                'email': 'dr.karim@gmail.com',
                'phone': '+8801711111111',
                'role': 'doctor',
                'doctor': {
                    'bmdc_number': 'BMDC001',
                    'qualifications': 'MBBS, MD (Cardiology)',
                    'experience_years': 12,
                    'about': 'Experienced cardiologist with expertise in complex cardiac cases',
                    'consultation_fee_online': Decimal('0.00'),
                    'consultation_fee_in_person': Decimal('1000.00'),
                    'is_verified': True,
                    'rating': Decimal('4.8'),
                    'total_reviews': 45,
                    'specialties': ['Cardiologist'],
                }
            },
            {
                'first_name': 'Fatima',
                'last_name': 'Khan',
                'email': 'dr.fatima@gmail.com',
                'phone': '+8801722222222',
                'role': 'doctor',
                'doctor': {
                    'bmdc_number': 'BMDC002',
                    'qualifications': 'MBBS, BCS (Pediatrics)',
                    'experience_years': 8,
                    'about': 'Specialized in child health and development',
                    'consultation_fee_online': Decimal('0.00'),
                    'consultation_fee_in_person': Decimal('800.00'),
                    'is_verified': True,
                    'rating': Decimal('4.9'),
                    'total_reviews': 52,
                    'specialties': ['Pediatrician'],
                }
            },
            {
                'first_name': 'Mohammad',
                'last_name': 'Hasan',
                'email': 'dr.hasan@gmail.com',
                'phone': '+8801733333333',
                'role': 'doctor',
                'doctor': {
                    'bmdc_number': 'BMDC003',
                    'qualifications': 'MBBS, DO (Ophthalmology)',
                    'experience_years': 10,
                    'about': 'Expert in eye care and vision correction',
                    'consultation_fee_online': Decimal('0.00'),
                    'consultation_fee_in_person': Decimal('900.00'),
                    'is_verified': True,
                    'rating': Decimal('4.7'),
                    'total_reviews': 38,
                    'specialties': ['Ophthalmologist'],
                }
            },
            {
                'first_name': 'Ayesha',
                'last_name': 'Begum',
                'email': 'dr.ayesha@gmail.com',
                'phone': '+8801744444444',
                'role': 'doctor',
                'doctor': {
                    'bmdc_number': 'BMDC004',
                    'qualifications': 'MBBS, MS (Orthopedics)',
                    'experience_years': 11,
                    'about': 'Specialist in bone and joint disorders',
                    'consultation_fee_online': Decimal('0.00'),
                    'consultation_fee_in_person': Decimal('1100.00'),
                    'is_verified': True,
                    'rating': Decimal('4.6'),
                    'total_reviews': 41,
                    'specialties': ['Orthopedic'],
                }
            },
            {
                'first_name': 'Sohel',
                'last_name': 'Rahman',
                'email': 'dr.sohel@gmail.com',
                'phone': '+8801755555555',
                'role': 'doctor',
                'doctor': {
                    'bmdc_number': 'BMDC005',
                    'qualifications': 'MBBS, Diploma in Neurology',
                    'experience_years': 9,
                    'about': 'Experienced neurologist with expertise in headaches and seizures',
                    'consultation_fee_online': Decimal('0.00'),
                    'consultation_fee_in_person': Decimal('1200.00'),
                    'is_verified': True,
                    'rating': Decimal('4.8'),
                    'total_reviews': 36,
                    'specialties': ['Neurologist'],
                }
            },
            {
                'first_name': 'Nasrin',
                'last_name': 'Akter',
                'email': 'dr.nasrin@gmail.com',
                'phone': '+8801766666666',
                'role': 'doctor',
                'doctor': {
                    'bmdc_number': 'BMDC006',
                    'qualifications': 'MBBS, MD (Dermatology)',
                    'experience_years': 7,
                    'about': 'Skin specialist with expertise in cosmetic and medical dermatology',
                    'consultation_fee_online': Decimal('0.00'),
                    'consultation_fee_in_person': Decimal('800.00'),
                    'is_verified': True,
                    'rating': Decimal('4.9'),
                    'total_reviews': 48,
                    'specialties': ['Dermatologist'],
                }
            },
            {
                'first_name': 'Rafiq',
                'last_name': 'Uddin',
                'email': 'dr.rafiq@gmail.com',
                'phone': '+8801777777777',
                'role': 'doctor',
                'doctor': {
                    'bmdc_number': 'BMDC007',
                    'qualifications': 'MBBS, MD (Internal Medicine)',
                    'experience_years': 13,
                    'about': 'General physician with expertise in chronic diseases',
                    'consultation_fee_online': Decimal('0.00'),
                    'consultation_fee_in_person': Decimal('700.00'),
                    'is_verified': True,
                    'rating': Decimal('4.5'),
                    'total_reviews': 55,
                    'specialties': ['Medicine Specialist'],
                }
            },
            {
                'first_name': 'Nasima',
                'last_name': 'Sultana',
                'email': 'dr.nasima@gmail.com',
                'phone': '+8801788888888',
                'role': 'doctor',
                'doctor': {
                    'bmdc_number': 'BMDC008',
                    'qualifications': 'MBBS, DGO (Obstetrics & Gynecology)',
                    'experience_years': 11,
                    'about': 'Experienced gynecologist with expertise in women health',
                    'consultation_fee_online': Decimal('0.00'),
                    'consultation_fee_in_person': Decimal('1000.00'),
                    'is_verified': True,
                    'rating': Decimal('4.7'),
                    'total_reviews': 43,
                    'specialties': ['Gynecologist'],
                }
            },
        ]
        
        doctors = []
        specialties = Specialty.objects.all()
        
        for doc_data in doctors_data:
            # Create or get user
            user, created = User.objects.get_or_create(
                email=doc_data['email'],
                defaults={
                    'first_name': doc_data['first_name'],
                    'last_name': doc_data['last_name'],
                    'username': doc_data['email'].split('@')[0],
                    'phone': doc_data['phone'],
                    'role': 'doctor',
                    'is_verified': True,
                }
            )
            
            if created:
                user.set_password(settings.DEMO_LOGIN_PASSWORD)
                user.save()
            
            # Create or get doctor profile
            doctor_info = doc_data['doctor'].copy()
            specialty_names = doctor_info.pop('specialties')
            
            doctor, created = Doctor.objects.get_or_create(
                user=user,
                defaults=doctor_info
            )
            
            if created:
                # Assign specialties
                for spec_name in specialty_names:
                    spec = specialties.filter(name=spec_name).first()
                    if spec:
                        doctor.specialties.add(spec)
                
                # Assign hospitals using DoctorHospital model
                for idx, hospital in enumerate(hospitals[:2]):
                    DoctorHospital.objects.get_or_create(
                        doctor=doctor,
                        hospital=hospital,
                        defaults={
                            'is_primary': idx == 0,
                            'is_active': True,
                        }
                    )
                
                self.stdout.write(f'  Created doctor: Dr. {user.get_full_name()}')
            
            doctors.append(doctor)
        
        return doctors
    
    def create_availability(self, doctors, hospitals):
        """Create demo availability slots"""
        slot_times = ['09:00-11:00', '11:00-13:00', '14:00-16:00', '16:00-18:00']
        
        # Create availability for next 14 days
        count = 0
        for doctor in doctors:
            for hospital in hospitals[:2]:
                for days_ahead in range(1, 15):
                    appointment_date = date.today() + timedelta(days=days_ahead)
                    
                    for slot_time in slot_times:
                        availability, created = DoctorAvailability.objects.get_or_create(
                            doctor=doctor,
                            hospital=hospital,
                            date=appointment_date,
                            time_slot=slot_time,
                            defaults={
                                'is_available': True,
                                'is_booked': False,
                            }
                        )
                        if created:
                            count += 1
        
        self.stdout.write(f'  Created {count} availability slots')
    
    def create_patient(self):
        """Create demo patient account"""
        patient_user, created = User.objects.get_or_create(
            email='patient@gmail.com',
            defaults={
                'first_name': 'Tariq',
                'last_name': 'Hussain',
                'username': 'patient',
                'phone': '+8801900000000',
                'role': 'patient',
                'is_verified': True,
            }
        )
        
        if created:
            patient_user.set_password(settings.DEMO_LOGIN_PASSWORD)
            patient_user.save()
            self.stdout.write(f'  Created patient: {patient_user.get_full_name()}')
        
        PatientProfile.objects.get_or_create(
            user=patient_user,
            defaults={
                'date_of_birth': date(1990, 5, 15),
                'gender': 'male',
                'blood_group': 'O+',
                'address': '123 Residential Road, Dhaka',
                'city': 'Dhaka',
                'district': 'Dhaka',
                'emergency_contact': '+8801900000001',
                'medical_history': 'No major medical history',
                'allergies': 'None known',
            },
        )
        return patient_user

    def create_weekly_schedules(self, doctors):
        """Create recurring schedule entries for demo doctor dashboards."""
        for index, doctor in enumerate(doctors):
            hospital_link = doctor.hospitals.filter(is_active=True, is_primary=True).first()
            if not hospital_link:
                continue
            DoctorWeeklySchedule.objects.update_or_create(
                doctor=doctor,
                hospital=hospital_link.hospital,
                day_of_week=index % 6,
                defaults={
                    'start_time': time(9, 0),
                    'end_time': time(17, 0),
                    'is_active': True,
                },
            )

    def create_patient_dashboard_data(self, patient, doctors):
        """Add demo favorites and one open cart item to the patient dashboard."""
        profile, _ = PatientProfile.objects.get_or_create(user=patient)
        profile.favorite_doctors.add(*doctors[:3])

        if not doctors:
            return

        availability = DoctorAvailability.objects.filter(
            doctor=doctors[0],
            date__gte=date.today(),
            is_available=True,
            is_booked=False,
        ).select_related('hospital').first()
        if availability:
            CartItem.objects.get_or_create(
                patient=patient,
                availability=availability,
                defaults={
                    'doctor': availability.doctor,
                    'hospital': availability.hospital,
                    'consultation_fee': availability.doctor.get_consultation_fee(),
                    'service_fee': Decimal('150.00'),
                    'symptoms': 'Demo cart item for testing checkout.',
                },
            )
    
    def create_reviews(self, doctors):
        """Create demo reviews"""
        review_comments = [
            'Excellent doctor with great bedside manner. Highly recommended!',
            'Very professional and knowledgeable. Great experience.',
            'Best doctor I have ever visited. Solved my problem completely.',
            'Good doctor, a bit busy but very competent.',
            'Fantastic service and very caring approach.',
            'Thoroughly checked and explained everything clearly.',
            'Very punctual and dedicated to patient care.',
            'Amazing experience, will visit again!',
        ]
        
        review_ratings = [5, 4, 5, 4, 5, 5, 4, 5]
        
        # Get or create patient
        patient_user = User.objects.filter(email='patient@gmail.com').first()
        
        if patient_user:
            count = 0
            for idx, doctor in enumerate(doctors):
                review, created = Review.objects.get_or_create(
                    doctor=doctor,
                    patient=patient_user,
                    defaults={
                        'rating': review_ratings[idx % len(review_ratings)],
                        'comment': review_comments[idx % len(review_comments)],
                        'is_active': True,
                    }
                )
                if created:
                    count += 1
            
            self.stdout.write(f'  Created {count} reviews')
    
    def create_employees(self):
        """Create demo employees"""
        employees_data = [
            {
                'first_name': 'Rahima',
                'last_name': 'Akter',
                'email': 'rahima@gmail.com',
                'phone': '+8801712345678',
                'employee_id': 'EMP001',
                'department': 'Appointments',
                'designation': 'Appointment Manager',
            },
            {
                'first_name': 'Kamrul',
                'last_name': 'Hasan',
                'email': 'kamrul@gmail.com',
                'phone': '+8801712345679',
                'employee_id': 'EMP002',
                'department': 'Appointments',
                'designation': 'Senior Coordinator',
            },
            {
                'first_name': 'Shahinur',
                'last_name': 'Rahman',
                'email': 'shahinur@gmail.com',
                'phone': '+8801712345680',
                'employee_id': 'EMP003',
                'department': 'Appointments',
                'designation': 'Appointment Coordinator',
            },
            {
                'first_name': 'Fatima',
                'last_name': 'Khanom',
                'email': 'fatima.employee@gmail.com',
                'phone': '+8801712345681',
                'employee_id': 'EMP004',
                'department': 'Appointments',
                'designation': 'Appointment Assistant',
            },
            {
                'first_name': 'Tanvir',
                'last_name': 'Islam',
                'email': 'tanvir@gmail.com',
                'phone': '+8801712345682',
                'employee_id': 'EMP005',
                'department': 'Appointments',
                'designation': 'Junior Coordinator',
            },
        ]
        
        count = 0
        for emp_data in employees_data:
            user, created = User.objects.get_or_create(
                email=emp_data['email'],
                defaults={
                    'first_name': emp_data['first_name'],
                    'last_name': emp_data['last_name'],
                    'username': emp_data['email'].split('@')[0],
                    'phone': emp_data['phone'],
                    'role': 'employee',
                    'is_verified': True,
                }
            )
            
            if created:
                user.set_password(settings.DEMO_LOGIN_PASSWORD)
                user.save()
                count += 1

            EmployeeProfile.objects.get_or_create(
                user=user,
                defaults={
                    'employee_id': emp_data['employee_id'],
                    'department': emp_data['department'],
                    'designation': emp_data['designation'],
                    'joining_date': date.today(),
                }
            )
        
        self.stdout.write(f'  Created {count} employees')
    
    def create_appointments(self, patient, doctors, hospitals):
        """Create demo appointments with comprehensive coverage"""
        from appointments.models import Appointment
        
        count = 0
        
        # 1. Create TODAY's appointments for each doctor (for "Today's Appointments" section)
        for idx, doctor in enumerate(doctors[:3]):  # Create for first 3 doctors
            hospital = hospitals[idx % len(hospitals)]
            
            appointment, created = Appointment.objects.get_or_create(
                patient=patient,
                doctor=doctor,
                hospital=hospital,
                date=date.today(),
                time_slot=f'{9 + idx}:00-{10 + idx}:00',
                defaults={
                    'consultation_type': 'in_person',
                    'status': 'confirmed',
                    'consultation_fee': Decimal('800'),
                    'service_fee': Decimal('150'),
                    'total_amount': Decimal('950'),
                    'is_paid': True,
                    'payment_method': 'card',
                    'symptoms': 'General checkup and health consultation',
                }
            )
            if created:
                count += 1
        
        # 2. Create UPCOMING appointments for next 7 days (for "Upcoming" section)
        for idx, doctor in enumerate(doctors):
            hospital = hospitals[idx % len(hospitals)]
            appointment_date = date.today() + timedelta(days=(idx % 7 + 1))
            
            appointment, created = Appointment.objects.get_or_create(
                patient=patient,
                doctor=doctor,
                hospital=hospital,
                date=appointment_date,
                time_slot=f'{10 + (idx % 6)}:00-{11 + (idx % 6)}:00',
                defaults={
                    'consultation_type': 'in_person',
                    'status': 'pending' if idx % 3 == 0 else 'confirmed',
                    'consultation_fee': Decimal('800'),
                    'service_fee': Decimal('150'),
                    'total_amount': Decimal('950'),
                    'is_paid': True,
                    'payment_method': 'card',
                    'symptoms': 'Follow-up consultation' if idx % 2 else 'New patient evaluation',
                }
            )
            if created:
                count += 1
        
        # 3. Create PAST/COMPLETED appointments (for "Total Patients" and earnings)
        for idx, doctor in enumerate(doctors):
            hospital = hospitals[idx % len(hospitals)]
            # Create appointments from past 30 days
            past_date = date.today() - timedelta(days=(idx % 30 + 1))
            
            appointment, created = Appointment.objects.get_or_create(
                patient=patient,
                doctor=doctor,
                hospital=hospital,
                date=past_date,
                time_slot=f'{14 + (idx % 4)}:00-{15 + (idx % 4)}:00',
                defaults={
                    'consultation_type': 'in_person',
                    'status': 'completed',
                    'consultation_fee': Decimal('800'),
                    'service_fee': Decimal('150'),
                    'total_amount': Decimal('950'),
                    'is_paid': True,
                    'payment_method': 'card',
                    'doctor_notes': 'Follow-up recommended',
                    'symptoms': 'Health consultation',
                }
            )
            if created:
                count += 1
        
        self.stdout.write(f'  Created {count} appointments')

    def assign_demo_appointments(self, patient):
        """Distribute this demo patient's appointments among demo employees."""
        employees = list(User.objects.filter(role='employee').order_by('username'))
        if not employees:
            return

        appointments = Appointment.objects.filter(patient=patient).order_by('id')
        for index, appointment in enumerate(appointments):
            if appointment.assigned_to_id is None:
                appointment.assigned_to = employees[index % len(employees)]
                appointment.save(update_fields=['assigned_to', 'updated_at'])
    
    def create_payments(self):
        """Create demo payments and doctor earnings"""
        from payments.models import DoctorEarning, Invoice, Payment
        
        # Create payments for all paid appointments
        appointments = Appointment.objects.filter(is_paid=True)
        
        payment_count = 0
        invoice_count = 0
        earning_count = 0
        
        for appt in appointments:
            # Create payment record
            payment, created = Payment.objects.get_or_create(
                appointment=appt,
                defaults={
                    'amount': appt.total_amount,
                    'status': 'completed' if appt.status in ['completed', 'confirmed'] else 'pending',
                    'method': appt.payment_method or 'card',
                    'transaction_id': f'TXN{appt.id}{appt.patient.id}',
                }
            )
            
            if created:
                payment_count += 1

            try:
                appt.invoice
            except Invoice.DoesNotExist:
                invoice = Invoice(
                    appointment=appt,
                    invoice_number='',
                    consultation_fee=appt.consultation_fee,
                    service_fee=appt.service_fee,
                    discount=Decimal('0.00'),
                    tax=Decimal('0.00'),
                    total_amount=appt.total_amount,
                    payment_method=payment.method,
                    transaction_id=payment.transaction_id,
                    paid_at=payment.created_at if payment.status == 'completed' else None,
                )
                invoice.generate_invoice_number()
                invoice.save()
                invoice_count += 1
            
            # Create earning record for each completed or confirmed appointment
            if appt.status in ['completed', 'confirmed']:
                earning_exists = DoctorEarning.objects.filter(
                    doctor=appt.doctor,
                    appointment=appt
                ).exists()
                
                if not earning_exists:
                    # Calculate earnings properly
                    total = appt.total_amount
                    commission_rate = Decimal('15.00')
                    platform_commission = (total * commission_rate) / Decimal('100')
                    doctor_amount = total - platform_commission
                    
                    earning = DoctorEarning.objects.create(
                        doctor=appt.doctor,
                        appointment=appt,
                        total_amount=total,
                        commission_rate=commission_rate,
                        platform_commission=platform_commission,
                        doctor_amount=doctor_amount,
                        month=appt.date.month,
                        year=appt.date.year,
                        is_paid_to_doctor=appt.status == 'completed',
                    )
                    earning_count += 1
        
        self.stdout.write(f'  Created {payment_count} payments')
        self.stdout.write(f'  Created {invoice_count} invoices')
        self.stdout.write(f'  Created {earning_count} doctor earnings records')
