"""
JSON-based data stores for Smart-Sync Concierge MVP.

Handles CRUD operations for appointments, contacts, and services.
Stores data in JSON files instead of a database for MVP.

Production migration path: PostgreSQL in v0.3.0
"""

import json
import os
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Tuple
import uuid
import re


class BaseStore:
    """Base class for JSON data stores."""

    def __init__(self, file_name: str):
        """Initialize store with JSON file path."""
        self.file_path = os.path.join(
            os.path.dirname(__file__),
            file_name
        )
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Ensure JSON file exists with proper structure."""
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Data file not found: {self.file_path}")

    def _read_data(self) -> Dict[str, Any]:
        """Read data from JSON file."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            raise RuntimeError(f"Error reading {self.file_path}: {str(e)}")

    def _write_data(self, data: Dict[str, Any]):
        """Write data to JSON file."""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            raise RuntimeError(f"Error writing to {self.file_path}: {str(e)}")

    def _generate_id(self, prefix: str) -> str:
        """Generate unique ID with prefix."""
        unique_part = str(uuid.uuid4())[:8]
        return f"{prefix}_{unique_part}"

    def _update_metadata(self, data: Dict[str, Any], key: str, value: int):
        """Update metadata in store."""
        if 'metadata' in data:
            data['metadata'][key] = value
            data['metadata']['last_updated'] = datetime.utcnow().isoformat()


class AppointmentStore(BaseStore):
    """Store for appointment data."""

    def __init__(self):
        super().__init__('appointments.json')

    def list_all(self) -> List[Dict[str, Any]]:
        """Get all appointments."""
        data = self._read_data()
        return data.get('appointments', [])

    def list_by_contact(self, contact_id: str) -> List[Dict[str, Any]]:
        """Get appointments for a specific contact."""
        appointments = self.list_all()
        return [
            apt for apt in appointments
            if any(p.get('id') == contact_id for p in apt.get('participantes', []))
        ]

    def get_by_id(self, appointment_id: str) -> Optional[Dict[str, Any]]:
        """Get appointment by ID."""
        appointments = self.list_all()
        for apt in appointments:
            if apt.get('id') == appointment_id:
                return apt
        return None

    def create(self, appointment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new appointment."""
        data = self._read_data()
        appointments = data.get('appointments', [])

        # Generate ID with date
        fecha = appointment_data.get('fecha', date.today().isoformat())
        fecha_str = fecha.replace('-', '')
        appointment_id = f"apt_{fecha_str}_{self._generate_id('').split('_')[1]}"

        appointment = {
            **appointment_data,
            'id': appointment_id,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
        }

        appointments.append(appointment)
        data['appointments'] = appointments
        self._update_metadata(data, 'total_appointments', len(appointments))
        self._write_data(data)

        return appointment

    def update(self, appointment_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update existing appointment."""
        data = self._read_data()
        appointments = data.get('appointments', [])

        for i, apt in enumerate(appointments):
            if apt.get('id') == appointment_id:
                apt.update(update_data)
                apt['updated_at'] = datetime.utcnow().isoformat()
                appointments[i] = apt
                data['appointments'] = appointments
                self._write_data(data)
                return apt

        return None

    def check_conflicts(
        self,
        appointment_data: Dict[str, Any],
        exclude_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Check for appointment conflicts with given time and participants."""
        appointments = self.list_all()
        conflicts = []

        fecha = appointment_data.get('fecha')
        hora_inicio = appointment_data.get('hora_inicio')
        hora_fin = appointment_data.get('hora_fin')
        participantes = appointment_data.get('participantes', [])

        if not fecha or not hora_inicio:
            return []

        # Get participant IDs
        participant_ids = [p.get('id') for p in participantes if p.get('id')]

        for apt in appointments:
            if exclude_id and apt.get('id') == exclude_id:
                continue

            if apt.get('status') == 'cancelled':
                continue

            apt_fecha = apt.get('fecha')
            apt_hora_inicio = apt.get('hora_inicio')
            apt_hora_fin = apt.get('hora_fin')

            # Check if dates match
            if apt_fecha != fecha:
                continue

            # Check if times overlap
            if self._times_overlap(hora_inicio, hora_fin, apt_hora_inicio, apt_hora_fin):
                # Check if any participant matches
                apt_participants = [p.get('id') for p in apt.get('participantes', [])]
                for pid in participant_ids:
                    if pid in apt_participants:
                        conflicts.append({
                            'type': 'full_overlap',
                            'existing_appointment_id': apt.get('id'),
                            'message': f"Conflict with appointment {apt.get('id')}"
                        })
                        break

        return conflicts

    def get_suggestions(self, appointment_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get alternative time slot suggestions."""
        suggestions = []
        fecha = appointment_data.get('fecha')
        duracion = appointment_data.get('duracion_minutos', 60)

        if not fecha:
            return suggestions

        # Suggest same day at different times
        for hour in range(8, 18):
            for minute in [0, 30]:
                hora = f"{hour:02d}:{minute:02d}"
                hora_fin = self._add_minutes(hora, duracion)

                test_apt = {
                    **appointment_data,
                    'hora_inicio': hora,
                    'hora_fin': hora_fin
                }

                if not self.check_conflicts(test_apt):
                    suggestions.append({
                        'fecha': fecha,
                        'hora_inicio': hora,
                        'hora_fin': hora_fin,
                        'confidence': 0.9,
                        'reason': f"Available slot on same day"
                    })
                    if len(suggestions) >= 3:
                        break
            if len(suggestions) >= 3:
                break

        # Suggest next few days
        if len(suggestions) < 3:
            fecha_obj = datetime.strptime(fecha, '%Y-%m-%d')
            for days_ahead in range(1, 4):
                next_fecha = (fecha_obj + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
                hora = "10:00"
                hora_fin = self._add_minutes(hora, duracion)

                test_apt = {
                    **appointment_data,
                    'fecha': next_fecha,
                    'hora_inicio': hora,
                    'hora_fin': hora_fin
                }

                if not self.check_conflicts(test_apt):
                    suggestions.append({
                        'fecha': next_fecha,
                        'hora_inicio': hora,
                        'hora_fin': hora_fin,
                        'confidence': 0.85 - (days_ahead * 0.05),
                        'reason': f"Available on {next_fecha}"
                    })

        return suggestions[:5]

    @staticmethod
    def _times_overlap(start1: str, end1: str, start2: str, end2: str) -> bool:
        """Check if two time ranges overlap."""
        if not all([start1, end1, start2, end2]):
            return False

        def time_to_minutes(time_str: str) -> int:
            h, m = map(int, time_str.split(':'))
            return h * 60 + m

        start1_min = time_to_minutes(start1)
        end1_min = time_to_minutes(end1) if end1 else start1_min + 60
        start2_min = time_to_minutes(start2)
        end2_min = time_to_minutes(end2) if end2 else start2_min + 60

        return not (end1_min <= start2_min or end2_min <= start1_min)

    @staticmethod
    def _add_minutes(time_str: str, minutes: int) -> str:
        """Add minutes to a time string."""
        h, m = map(int, time_str.split(':'))
        total_minutes = h * 60 + m + minutes
        new_h = (total_minutes // 60) % 24
        new_m = total_minutes % 60
        return f"{new_h:02d}:{new_m:02d}"


class ContactStore(BaseStore):
    """Store for contact (doctor/staff/resource) data using Django ORM."""

    def __init__(self):
        # Don't call parent __init__ since we're using Django ORM
        self.file_path = None

    def list_all(self) -> List[Dict[str, Any]]:
        """Get all contacts."""
        from apps.contacts.models import Contact

        contacts = Contact.objects.all()
        return [self._model_to_dict(contact) for contact in contacts]

    def get_by_id(self, contact_id: str) -> Optional[Dict[str, Any]]:
        """Get contact by ID."""
        from apps.contacts.models import Contact

        try:
            contact = Contact.objects.get(id=contact_id)
            return self._model_to_dict(contact)
        except Contact.DoesNotExist:
            return None

    def create(self, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new contact."""
        from apps.contacts.models import Contact

        # Generate ID if not provided
        if 'id' not in contact_data or not contact_data['id']:
            contact_data['id'] = self._generate_id('cont')

        contact = Contact.objects.create(**contact_data)
        return self._model_to_dict(contact)

    def update(self, contact_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update existing contact."""
        from apps.contacts.models import Contact

        try:
            contact = Contact.objects.get(id=contact_id)
            for key, value in update_data.items():
                setattr(contact, key, value)
            contact.save()
            return self._model_to_dict(contact)
        except Contact.DoesNotExist:
            return None

    @staticmethod
    def _model_to_dict(contact) -> Dict[str, Any]:
        """Convert Django Contact model to dictionary."""
        return {
            'id': contact.id,
            'nombre': contact.nombre,
            'titulo': contact.titulo,
            'email': contact.email,
            'telefono': contact.telefono,
            'tipo': contact.tipo,
            'especialidades': contact.especialidades,
            'activo': contact.activo,
            'created_at': contact.created_at.isoformat(),
            'updated_at': contact.updated_at.isoformat(),
        }

    def check_availability(
        self,
        contact_id: str,
        fecha: str,
        hora_inicio: str,
        hora_fin: Optional[str] = None,
        ubicacion_id: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """Check if contact is available at given time."""
        contact = self.get_by_id(contact_id)
        if not contact:
            return False, "Contacto no encontrado"

        if not contact.get('activo'):
            return False, "Contacto inactivo"

        # Check location availability if specified
        if ubicacion_id:
            locations = contact.get('ubicaciones', [])
            location = next((loc for loc in locations if loc.get('id') == ubicacion_id), None)
            if not location:
                return False, f"Ubicación {ubicacion_id} no encontrada"
            if not location.get('disponible'):
                return False, "Ubicación no disponible"

        # In MVP, assume all listed contacts are available during business hours
        # TODO: Implement actual schedule checking logic
        return True, None

    def get_available_slots(
        self,
        contact_id: str,
        days_ahead: int = 7,
        duration_minutes: int = 60,
        location_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get available time slots for a contact."""
        slots = []
        start_date = date.today()

        for day_offset in range(days_ahead):
            current_date = (start_date + timedelta(days=day_offset)).isoformat()

            # Skip weekends for now
            if (start_date + timedelta(days=day_offset)).weekday() >= 5:
                continue

            # Generate slots for business hours (8-18)
            for hour in range(8, 18):
                for minute in [0, 30]:
                    hora_inicio = f"{hour:02d}:{minute:02d}"
                    hora_fin = AppointmentStore._add_minutes(hora_inicio, duration_minutes)

                    slots.append({
                        'fecha': current_date,
                        'hora_inicio': hora_inicio,
                        'hora_fin': hora_fin,
                        'disponible': True
                    })

        return slots[:10]  # Return top 10 slots


class ServiceStore(BaseStore):
    """Store for service/appointment-type catalog data using Django ORM."""

    def __init__(self):
        # Don't call parent __init__ since we're using Django ORM
        self.file_path = None

    def list_all(self) -> List[Dict[str, Any]]:
        """Get all services."""
        from apps.services.models import Service

        services = Service.objects.all()
        return [self._model_to_dict(service) for service in services]

    def get_by_id(self, service_id: str) -> Optional[Dict[str, Any]]:
        """Get service by ID."""
        from apps.services.models import Service

        try:
            service = Service.objects.get(id=service_id)
            return self._model_to_dict(service)
        except Service.DoesNotExist:
            return None

    def create(self, service_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new service."""
        from apps.services.models import Service

        # If no ID provided, generate one
        if 'id' not in service_data:
            service_data['id'] = self._generate_id('service')

        # Filter only fields that exist in the Service model
        model_fields = {'id', 'nombre', 'categoria', 'descripcion', 'duracion_minutos', 'activo'}
        filtered_data = {k: v for k, v in service_data.items() if k in model_fields}

        service = Service.objects.create(**filtered_data)
        return self._model_to_dict(service)

    def update(self, service_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update existing service."""
        from apps.services.models import Service

        try:
            service = Service.objects.get(id=service_id)
            # Filter only fields that exist in the Service model
            model_fields = {'nombre', 'categoria', 'descripcion', 'duracion_minutos', 'activo'}
            for key, value in update_data.items():
                if key in model_fields:
                    setattr(service, key, value)
            service.save()
            return self._model_to_dict(service)
        except Service.DoesNotExist:
            return None

    @staticmethod
    def _model_to_dict(service) -> Dict[str, Any]:
        """Convert Django Service model to dictionary."""
        return {
            'id': service.id,
            'nombre': service.nombre,
            'categoria': service.categoria,
            'descripcion': service.descripcion,
            'duracion_minutos': service.duracion_minutos,
            'activo': service.activo,
            'created_at': service.created_at.isoformat(),
            'updated_at': service.updated_at.isoformat(),
        }


class TraceStore(BaseStore):
    """Store for AI agent decision traces."""

    def __init__(self):
        """Initialize TraceStore."""
        super().__init__('traces.json')

    def list_all(self) -> List[Dict[str, Any]]:
        """Get all traces."""
        data = self._read_data()
        return data.get('traces', [])

    def get_by_id(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """Get trace by ID."""
        data = self._read_data()
        traces = data.get('traces', [])

        for trace in traces:
            if trace.get('trace_id') == trace_id:
                return trace

        return None

    def create(self, trace_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new trace."""
        data = self._read_data()
        traces = data.get('traces', [])

        # Ensure trace has required fields
        if 'trace_id' not in trace_data:
            trace_data['trace_id'] = self._generate_id('trace')

        trace_data['created_at'] = datetime.utcnow().isoformat()

        traces.append(trace_data)
        data['traces'] = traces
        data['metadata']['total_traces'] = len(traces)
        data['metadata']['last_updated'] = datetime.utcnow().isoformat()

        self._write_data(data)
        return trace_data

    def list_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """Get traces for specific user."""
        data = self._read_data()
        traces = data.get('traces', [])

        return [t for t in traces if t.get('user_id') == user_id]

    def list_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get traces by final status (success, error, conflict)."""
        data = self._read_data()
        traces = data.get('traces', [])

        return [t for t in traces if t.get('final_status') == status]
