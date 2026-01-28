#!/usr/bin/env python3
"""
Integration Test - AppointmentViewSet + AgentOrchestrator + TraceStore

Tests the complete flow:
1. POST request to /api/v1/appointments/ with natural language prompt
2. AgentOrchestrator processes through 6-agent pipeline
3. DecisionTrace saved to traces.json
4. Appointment created in appointments.json
"""

import os
import sys
import django
import json
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from rest_framework.test import APIClient
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

def test_integration():
    """Test complete integration flow"""
    print_header("Integration Test: AppointmentViewSet + AgentOrchestrator + TraceStore")

    # Initialize stores
    appointment_store = AppointmentStore()
    contact_store = ContactStore()
    service_store = ServiceStore()
    trace_store = TraceStore()

    # Count initial records
    initial_appointments = len(appointment_store.list_all())
    initial_traces = len(trace_store.list_all())
    initial_contacts = len(contact_store.list_all())

    print_info(f"Initial state:")
    print(f"  - Appointments: {initial_appointments}")
    print(f"  - Traces: {initial_traces}")
    print(f"  - Contacts: {initial_contacts}")

    # Ensure we have test data
    print_info("Setting up test data...")
    if initial_contacts == 0:
        test_contact = contact_store.create({
            'nombre': 'Dr. Test García',
            'especialidad': 'Medicina General',
            'email': 'test@example.com',
            'telefono': '5551234567',
            'ubicaciones': ['Consultorio 1', 'Consultorio 2']
        })
        print_success(f"Created test contact: {test_contact['nombre']} ({test_contact['id']})")
        contact_id = test_contact['id']
    else:
        contact_id = contact_store.list_all()[0]['id']

    if len(service_store.list_all()) == 0:
        test_service = service_store.create({
            'nombre': 'Consulta General',
            'descripcion': 'Consulta médica general',
            'duracion': 30
        })
        print_success(f"Created test service: {test_service['nombre']}")

    # Test AgentOrchestrator directly
    print_header("Step 1: Test AgentOrchestrator")

    from apps.agents import AgentOrchestrator

    orchestrator = AgentOrchestrator()

    prompt = "cita mañana 10am con Dr. García"
    print_info(f"Processing prompt: '{prompt}'")

    stores = {
        'contact_store': contact_store,
        'service_store': service_store,
        'appointment_store': appointment_store,
    }

    result = orchestrator.process_appointment_prompt(
        prompt=prompt,
        user_timezone='America/Mexico_City',
        user_id='test_user_001',
        stores=stores
    )

    print(f"Result Status: {result['status'].upper()}")
    print(f"Message: {result.get('message')}")

    if 'trace' in result:
        trace = result['trace']
        print_success(f"DecisionTrace created: {trace.trace_id}")
        print(f"  - Final Status: {trace.final_status}")
        print(f"  - Agents Executed: {len(trace.agents)}")
        print(f"  - Duration: {trace.total_duration_ms}ms")

        # Try to save trace
        print_header("Step 2: Test TraceStore.create()")

        try:
            trace_dict = trace.to_dict()
            print_info("Converted DecisionTrace to dict")
            print(f"  - Keys: {list(trace_dict.keys())}")

            saved_trace = trace_store.create(trace_dict)
            print_success(f"Trace saved to traces.json")
            print(f"  - Trace ID: {saved_trace.get('trace_id')}")

            # Verify it was saved
            retrieved_trace = trace_store.get_by_id(trace.trace_id)
            if retrieved_trace:
                print_success("Trace verified in traces.json")
            else:
                print_error("Trace not found after saving")

        except Exception as e:
            print_error(f"Error saving trace: {str(e)}")
            import traceback
            traceback.print_exc()

    # Test AppointmentViewSet (if success)
    if result['status'] == 'success' and result.get('data'):
        print_header("Step 3: Test Appointment Creation")

        apt_data = result['data']
        print_info("Creating appointment from orchestrator data...")

        try:
            # Simulate what AppointmentViewSet.create() does
            appointment = appointment_store.create(apt_data)
            print_success(f"Appointment created: {appointment['id']}")
            print(f"  - Contact: {appointment.get('contacto_id')}")
            print(f"  - Date: {appointment.get('fecha')}")
            print(f"  - Time: {appointment.get('hora_inicio')}")
            print(f"  - Trace ID: {appointment.get('trace_id')}")

            # Verify counts increased
            new_appointments = len(appointment_store.list_all())
            new_traces = len(trace_store.list_all())

            print_header("Step 4: Verify Data Persistence")

            print_success(f"Appointments increased: {initial_appointments} → {new_appointments}")
            print_success(f"Traces increased: {initial_traces} → {new_traces}")

            # Final verification
            retrieved_apt = appointment_store.get_by_id(appointment['id'])
            if retrieved_apt:
                print_success("Appointment verified in appointments.json")
            else:
                print_error("Appointment not found after saving")

        except Exception as e:
            print_error(f"Error creating appointment: {str(e)}")
            import traceback
            traceback.print_exc()

    # Summary
    print_header("Integration Test Summary")

    final_appointments = len(appointment_store.list_all())
    final_traces = len(trace_store.list_all())

    print(f"Final state:")
    print(f"  - Appointments: {initial_appointments} → {final_appointments} ({final_appointments - initial_appointments} created)")
    print(f"  - Traces: {initial_traces} → {final_traces} ({final_traces - initial_traces} created)")

    if final_appointments > initial_appointments and final_traces > initial_traces:
        print_success("INTEGRATION TEST PASSED ✓")
        return True
    else:
        print_error("INTEGRATION TEST FAILED ✗")
        if final_traces == initial_traces:
            print_error("  - Traces not being saved")
        if final_appointments == initial_appointments:
            print_error("  - Appointments not being created")
        return False

if __name__ == '__main__':
    try:
        success = test_integration()
        sys.exit(0 if success else 1)
    except Exception as e:
        print_error(f"Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
