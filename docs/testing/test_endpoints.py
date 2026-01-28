#!/usr/bin/env python3
"""
Test script for Smart-Sync Concierge API endpoints.
Tests all major endpoints with proper Django setup.
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

# Initialize clients
client = APIClient()
django_client = Client()

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(title):
    print(f"\n{BLUE}{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}{RESET}\n")

def print_success(test_name):
    print(f"{GREEN}✓ {test_name}{RESET}")

def print_error(test_name, error):
    print(f"{RED}✗ {test_name}{RESET}")
    print(f"  Error: {error}")

def print_info(message):
    print(f"{YELLOW}ℹ {message}{RESET}")

def test_health_endpoint():
    """Test /api/v1/health/ endpoint"""
    print_header("Test 1: Health Check Endpoint")

    try:
        response = client.get('/api/v1/health/')

        if response.status_code == 200:
            data = response.json()
            print_success("Health endpoint returns 200 OK")
            print(json.dumps(data, indent=2))

            if data.get('status') == 'healthy':
                print_success("API reports as healthy")
            else:
                print_error("Health status", "API did not report as healthy")
        else:
            print_error("Health endpoint", f"Returned status {response.status_code}")
    except Exception as e:
        print_error("Health endpoint", str(e))

def test_api_root():
    """Test /api/v1/ API root endpoint"""
    print_header("Test 2: API Root Endpoint")

    try:
        response = client.get('/api/v1/')

        if response.status_code == 200:
            data = response.json()
            print_success("API root returns 200 OK")
            print(json.dumps(data, indent=2))

            endpoints = data.get('endpoints', {})
            if 'appointments' in endpoints:
                print_success("Appointments endpoint registered")
            if 'contacts' in endpoints:
                print_success("Contacts endpoint registered")
            if 'services' in endpoints:
                print_success("Services endpoint registered")
        else:
            print_error("API root", f"Returned status {response.status_code}")
    except Exception as e:
        print_error("API root", str(e))

def test_appointments_list():
    """Test /api/v1/appointments/ endpoint"""
    print_header("Test 3: List Appointments")

    try:
        response = client.get('/api/v1/appointments/')

        if response.status_code == 200:
            data = response.json()
            print_success("Appointments list returns 200 OK")

            if isinstance(data, dict) and 'results' in data:
                appointments = data['results']
                print_success(f"Retrieved {len(appointments)} appointments")
            elif isinstance(data, list):
                print_success(f"Retrieved {len(data)} appointments")
            else:
                print_info(f"Response: {json.dumps(data, indent=2)}")
        else:
            print_error("Appointments list", f"Returned status {response.status_code}")
    except Exception as e:
        print_error("Appointments list", str(e))

def test_create_appointment():
    """Test creating appointment with agent orchestrator"""
    print_header("Test 4: Create Appointment with Orchestrator")

    try:
        # First, ensure we have some test data
        contact_store = ContactStore()
        service_store = ServiceStore()

        # Get or create test contact
        contacts = contact_store.list_all()
        if not contacts:
            print_info("No contacts found. Creating test contact...")
            test_contact = contact_store.create({
                'nombre': 'Dr. Test',
                'especialidad': 'Medicina General',
                'email': 'test@example.com',
                'telefono': '5551234567'
            })
            contact_id = test_contact['id']
        else:
            contact_id = contacts[0]['id']

        # Get or create test service
        services = service_store.list_all()
        if not services:
            print_info("No services found. Creating test service...")
            test_service = service_store.create({
                'nombre': 'Consulta General',
                'descripcion': 'Consulta médica general',
                'duracion': 30
            })
            service_id = test_service['id']
        else:
            service_id = services[0]['id']

        # Create appointment
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

        appointment_data = {
            'contacto': contact_id,
            'fecha': tomorrow,
            'hora_inicio': '10:00',
            'hora_fin': '10:30',
            'servicio': service_id,
            'ubicacion': 'Consultorio 1',
            'notas': 'Cita de prueba'
        }

        response = client.post(
            '/api/v1/appointments/',
            appointment_data,
            format='json'
        )

        if response.status_code in [200, 201]:
            data = response.json()
            print_success(f"Appointment created with status {response.status_code}")

            if 'trace_id' in data:
                print_success(f"DecisionTrace saved: {data['trace_id']}")

            print(json.dumps(data, indent=2))
        else:
            print_error("Create appointment", f"Returned status {response.status_code}")
            print(f"Response: {response.json()}")
    except Exception as e:
        print_error("Create appointment", str(e))
        import traceback
        traceback.print_exc()

def test_traces_endpoint():
    """Test /api/v1/traces/ endpoint"""
    print_header("Test 5: List Traces")

    try:
        response = client.get('/api/v1/traces/')

        # Check if authentication is required
        if response.status_code == 401:
            print_info("Authentication required for traces endpoint (expected)")

            # Traces endpoint requires authentication
            print_info("Note: Traces endpoint requires authentication token")
        elif response.status_code == 200:
            data = response.json()
            print_success("Traces endpoint returns 200 OK")
            print(json.dumps(data, indent=2))
        else:
            print_error("Traces endpoint", f"Returned status {response.status_code}")
    except Exception as e:
        print_error("Traces endpoint", str(e))

def test_agent_pipeline():
    """Test agent pipeline with sample prompt"""
    print_header("Test 6: Agent Pipeline")

    try:
        from apps.agents import AgentOrchestrator

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

        # Create test data if needed
        contacts = contact_store.list_all()
        if not contacts:
            contact_store.create({
                'nombre': 'Dr. Juan García',
                'especialidad': 'Cardiología',
                'email': 'juan@clinic.com',
                'telefono': '5551234567'
            })

        services = service_store.list_all()
        if not services:
            service_store.create({
                'nombre': 'Consulta de Cardiología',
                'descripcion': 'Consulta cardiológica completa',
                'duracion': 45
            })

        # Test prompt
        prompt = "cita mañana a las 10am con el Dr. García en consultorio 1"

        print_info(f"Testing prompt: '{prompt}'")

        result = orchestrator.process_appointment_prompt(
            prompt=prompt,
            user_timezone='America/Mexico_City',
            user_id='test_user_123',
            stores=stores
        )

        print_success("Agent pipeline executed")
        print(f"\nResult Status: {result['status']}")

        if result['status'] == 'success':
            print_success("Appointment created successfully")
        elif result['status'] == 'conflict':
            print_info("Conflict detected - suggestions provided")

        if 'trace_id' in result:
            print_success(f"Trace ID: {result['trace_id']}")

        print("\nFull Response:")
        print(json.dumps(result, indent=2))

    except Exception as e:
        print_error("Agent pipeline", str(e))
        import traceback
        traceback.print_exc()

def main():
    """Run all endpoint tests"""
    print(f"\n{BLUE}╔════════════════════════════════════════════════════════════════════╗{RESET}")
    print(f"{BLUE}║  Smart-Sync Concierge API Endpoint Testing                          ║{RESET}")
    print(f"{BLUE}║  Version 0.2.0 - Phase 3 Agent Integration                          ║{RESET}")
    print(f"{BLUE}╚════════════════════════════════════════════════════════════════════╝{RESET}")

    # Run tests
    test_health_endpoint()
    test_api_root()
    test_appointments_list()
    test_traces_endpoint()
    test_agent_pipeline()
    test_create_appointment()

    print(f"\n{BLUE}{'='*70}")
    print("Testing Complete")
    print(f"{'='*70}{RESET}\n")

if __name__ == '__main__':
    main()
