#!/usr/bin/env python3
"""
Test script for Agent Pipeline - Local Testing
Tests the 6-agent pipeline with various prompts.
"""

import os
import sys
import django
import json
from datetime import datetime, timedelta
from pprint import pprint

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.agents import AgentOrchestrator
from data.stores import AppointmentStore, ContactStore, ServiceStore, TraceStore

# Color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(title):
    print(f"\n{BLUE}{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}{RESET}\n")

def print_success(message):
    print(f"{GREEN}✓ {message}{RESET}")

def print_error(message):
    print(f"{RED}✗ {message}{RESET}")

def print_info(message):
    print(f"{YELLOW}ℹ {message}{RESET}")

def setup_test_data():
    """Create initial test data"""
    print_header("Setting Up Test Data")

    contact_store = ContactStore()
    service_store = ServiceStore()

    # Get existing contacts
    contacts = contact_store.list_all()
    if contacts:
        print_success(f"Found {len(contacts)} existing contacts")
        for contact in contacts[:3]:
            print(f"  - {contact['nombre']} ({contact['id']})")
    else:
        print_info("No contacts found. Creating test contacts...")
        test_contacts = [
            {'nombre': 'Dr. Juan García', 'especialidad': 'Cardiología', 'email': 'juan@clinic.com', 'telefono': '5551234567'},
            {'nombre': 'Dra. María López', 'especialidad': 'Neuología', 'email': 'maria@clinic.com', 'telefono': '5559876543'},
            {'nombre': 'Dr. Carlos Rodríguez', 'especialidad': 'Oftalmología', 'email': 'carlos@clinic.com', 'telefono': '5554444444'},
        ]
        for contact_data in test_contacts:
            created = contact_store.create(contact_data)
            print_success(f"Created: {created['nombre']} ({created['id']})")

    # Get existing services
    services = service_store.list_all()
    if services:
        print_success(f"Found {len(services)} existing services")
        for service in services[:3]:
            print(f"  - {service['nombre']} ({service['duracion']} min)")
    else:
        print_info("No services found. Creating test services...")
        test_services = [
            {'nombre': 'Consulta General', 'descripcion': 'Consulta médica general', 'duracion': 30},
            {'nombre': 'Consulta Especializada', 'descripcion': 'Consulta con especialista', 'duracion': 45},
            {'nombre': 'Seguimiento', 'descripcion': 'Cita de seguimiento', 'duracion': 20},
        ]
        for service_data in test_services:
            created = service_store.create(service_data)
            print_success(f"Created: {created['nombre']} ({created['duracion']} min)")

def test_pipeline(prompt, user_timezone="America/Mexico_City", user_id="test_user_001"):
    """Test the agent pipeline with a given prompt"""
    print_header(f"Testing Prompt: '{prompt}'")

    orchestrator = AgentOrchestrator()

    # Initialize stores
    contact_store = ContactStore()
    service_store = ServiceStore()
    appointment_store = AppointmentStore()
    trace_store = TraceStore()

    stores = {
        'contact': contact_store,
        'service': service_store,
        'appointment': appointment_store,
        'trace': trace_store,
    }

    print(f"Prompt: {BLUE}{prompt}{RESET}")
    print(f"Timezone: {user_timezone}")
    print(f"User ID: {user_id}\n")

    try:
        result = orchestrator.process_appointment_prompt(
            prompt=prompt,
            user_timezone=user_timezone,
            user_id=user_id,
            stores=stores
        )

        status = result.get('status', 'unknown')
        print(f"Result Status: {BLUE}{status.upper()}{RESET}")

        # Display result based on status
        if status == 'success':
            print_success("Appointment created successfully")
            appointment = result.get('data', {})
            print(f"  Appointment ID: {appointment.get('id')}")
            print(f"  Contact: {appointment.get('contacto_nombre', 'N/A')}")
            print(f"  Date: {appointment.get('fecha')}")
            print(f"  Time: {appointment.get('hora_inicio')} - {appointment.get('hora_fin')}")

        elif status == 'conflict':
            print_error("Time conflict detected")
            suggestions = result.get('suggestions', [])
            print_info(f"Found {len(suggestions)} alternative slots")
            for i, suggestion in enumerate(suggestions[:3], 1):
                print(f"  {i}. {suggestion.get('fecha')} at {suggestion.get('hora_inicio')} (confidence: {suggestion.get('confidence')})")

        elif status == 'error':
            print_error("Processing failed")
            error_msg = result.get('error_message', 'Unknown error')
            print(f"  Error: {error_msg}")

        # Display trace info
        trace_id = result.get('trace_id')
        if trace_id:
            print_success(f"Trace ID: {trace_id}")

        # Display detailed trace information
        if 'trace' in result:
            trace = result['trace']
            print(f"\nTrace Details:")
            if hasattr(trace, 'final_status'):
                # It's a DecisionTrace dataclass
                print(f"  Status: {trace.final_status}")
                print(f"  Duration: {trace.total_duration_ms}ms")

                agents = trace.agents if hasattr(trace, 'agents') else []
                print(f"  Agents Executed: {len(agents)}")
                for agent_data in agents:
                    agent_name = agent_data.get('agent_name', 'Unknown')
                    agent_status = agent_data.get('status', 'unknown')
                    duration = agent_data.get('duration_ms', 0)
                    confidence = agent_data.get('confidence', 0)
                    print(f"    - {agent_name}: {agent_status} ({duration}ms, confidence: {confidence})")
            else:
                # It's a dict
                print(f"  Status: {trace.get('final_status')}")
                print(f"  Duration: {trace.get('total_duration_ms')}ms")

    except Exception as e:
        print_error(f"Exception during processing: {str(e)}")
        import traceback
        traceback.print_exc()

def test_multiple_prompts():
    """Test pipeline with various prompts"""
    print_header("Testing Multiple Prompts")

    test_cases = [
        "cita mañana a las 10am con el Dr. García",
        "quiero una cita la próxima semana con la Dra. López a las 14:00",
        "cita en consultorio 2 con Dr. Carlos a las 9am",
        "cita hoy 23:00 con el doctor García",  # Outside business hours
        "cita mañana",  # Missing information
        "próxima semana con García",  # Ambiguous
    ]

    for i, prompt in enumerate(test_cases, 1):
        print(f"\n{YELLOW}[Test Case {i}/{len(test_cases)}]{RESET}")
        test_pipeline(prompt)

def main():
    """Run all pipeline tests"""
    print(f"\n{BLUE}╔════════════════════════════════════════════════════════════════════════╗{RESET}")
    print(f"{BLUE}║  Smart-Sync Concierge - Agent Pipeline Local Testing                   ║{RESET}")
    print(f"{BLUE}║  Version 0.2.0 - Phase 3 Agent Integration                             ║{RESET}")
    print(f"{BLUE}╚════════════════════════════════════════════════════════════════════════╝{RESET}")

    # Setup test data
    setup_test_data()

    # Test pipeline with specific prompts
    test_multiple_prompts()

    print(f"\n{BLUE}{'='*80}")
    print("Pipeline Testing Complete")
    print(f"{'='*80}{RESET}\n")

if __name__ == '__main__':
    main()
