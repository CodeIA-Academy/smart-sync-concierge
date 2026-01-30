"""
Management command to populate demo data for Smart-Sync Concierge.
Usage: python manage.py populate_demo_data

This command creates demo data for testing using Django ORM models.
Works with PostgreSQL/Neon database.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, time
from apps.contacts.models import Contact
from apps.services.models import Service
from apps.appointments.models import Appointment


class Command(BaseCommand):
    help = 'Populate database with demo data for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creando datos de demostración...\n')

        # Create demo contacts (doctors)
        contacts_data = [
            {
                'id': 'dr_juan_perez',
                'nombre': 'Dr. Juan Pérez',
                'titulo': 'Médico General',
                'email': 'juan.perez@hospital.com',
                'telefono': '+34912345678',
                'tipo': 'prestador',
                'especialidades': ['consulta_general', 'pediatria'],
            },
            {
                'id': 'dra_maria_garcia',
                'nombre': 'Dra. María García',
                'titulo': 'Cardióloga',
                'email': 'maria.garcia@hospital.com',
                'telefono': '+34987654321',
                'tipo': 'prestador',
                'especialidades': ['cardiologia'],
            },
            {
                'id': 'dr_carlos_lopez',
                'nombre': 'Dr. Carlos López',
                'titulo': 'Dermatólogo',
                'email': 'carlos.lopez@hospital.com',
                'telefono': '+34956789012',
                'tipo': 'prestador',
                'especialidades': ['dermatologia'],
            },
        ]

        for contact_data in contacts_data:
            contact, created = Contact.objects.get_or_create(
                id=contact_data['id'],
                defaults=contact_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Contacto creado: {contact.nombre}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠ Contacto ya existe: {contact.nombre}')
                )

        # Create demo services
        services_data = [
            {
                'id': 'consulta_general',
                'nombre': 'Consulta General',
                'categoria': 'medica',
                'descripcion': 'Consulta médica general',
                'duracion_minutos': 30,
            },
            {
                'id': 'consulta_cardiologia',
                'nombre': 'Consulta Cardiología',
                'categoria': 'medica',
                'descripcion': 'Consulta especializada en cardiología',
                'duracion_minutos': 45,
            },
            {
                'id': 'consulta_dermatologia',
                'nombre': 'Consulta Dermatología',
                'categoria': 'medica',
                'descripcion': 'Consulta especializada en dermatología',
                'duracion_minutos': 40,
            },
            {
                'id': 'consulta_pediatria',
                'nombre': 'Consulta Pediatría',
                'categoria': 'medica',
                'descripcion': 'Consulta pediátrica',
                'duracion_minutos': 25,
            },
        ]

        for service_data in services_data:
            service, created = Service.objects.get_or_create(
                id=service_data['id'],
                defaults=service_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Servicio creado: {service.nombre}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠ Servicio ya existe: {service.nombre}')
                )

        # Create demo appointments
        now = timezone.now()

        appointments_data = [
            {
                'id': 'apt_20260131_001',
                'fecha': (now + timedelta(days=1)).date(),
                'hora_inicio': time(10, 0),
                'hora_fin': time(10, 30),
                'duracion_minutos': 30,
                'status': 'confirmed',
                'tipo': {
                    'id': 'consulta_general',
                    'nombre': 'Consulta General',
                    'categoria': 'medica'
                },
                'participantes': [
                    {
                        'id': 'dr_juan_perez',
                        'nombre': 'Dr. Juan Pérez',
                        'rol': 'prestador'
                    }
                ],
                'usuario_id': 'user_001',
                'prompt_original': 'cita mañana 10am con Dr. Pérez',
                'notas': {
                    'cliente': 'Primera consulta',
                    'interna': 'Paciente nuevo'
                }
            },
            {
                'id': 'apt_20260201_002',
                'fecha': (now + timedelta(days=2)).date(),
                'hora_inicio': time(14, 0),
                'hora_fin': time(14, 45),
                'duracion_minutos': 45,
                'status': 'confirmed',
                'tipo': {
                    'id': 'consulta_cardiologia',
                    'nombre': 'Consulta Cardiología',
                    'categoria': 'medica'
                },
                'participantes': [
                    {
                        'id': 'dra_maria_garcia',
                        'nombre': 'Dra. María García',
                        'rol': 'prestador'
                    }
                ],
                'usuario_id': 'user_002',
                'prompt_original': 'cita el sábado 2pm con Dra. García cardiología',
                'notas': {
                    'cliente': 'Seguimiento cardiaco',
                    'interna': 'Paciente regular'
                }
            },
            {
                'id': 'apt_20260202_003',
                'fecha': (now + timedelta(days=3)).date(),
                'hora_inicio': time(11, 0),
                'hora_fin': time(11, 40),
                'duracion_minutos': 40,
                'status': 'confirmed',
                'tipo': {
                    'id': 'consulta_dermatologia',
                    'nombre': 'Consulta Dermatología',
                    'categoria': 'medica'
                },
                'participantes': [
                    {
                        'id': 'dr_carlos_lopez',
                        'nombre': 'Dr. Carlos López',
                        'rol': 'prestador'
                    }
                ],
                'usuario_id': 'user_001',
                'prompt_original': 'cita el domingo 11am con Dr. López dermatólogo',
                'notas': {
                    'cliente': 'Consulta dermatológica',
                    'interna': 'Revisión de lesiones'
                }
            },
        ]

        for apt_data in appointments_data:
            appointment, created = Appointment.objects.get_or_create(
                id=apt_data['id'],
                defaults=apt_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Cita creada: {appointment.id} '
                        f'({appointment.fecha} {appointment.hora_inicio})'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠ Cita ya existe: {appointment.id}')
                )

        self.stdout.write(
            self.style.SUCCESS('\n✓ ¡Datos de demostración creados exitosamente!')
        )
