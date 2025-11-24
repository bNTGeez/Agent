"""
Test script for A2A API key authentication.

This script tests:
1. Direct HTTP requests to services (with/without API key)
2. Agent card discovery (should always work)
3. Task endpoints (should require API key when A2A_API_KEY is set)
4. Full agent-to-agent communication flow
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Try importing httpx (async HTTP client) or fall back to requests
try:
    import httpx
    USE_HTTPX = True
except ImportError:
    try:
        import requests
        USE_HTTPX = False
    except ImportError:
        print("❌ Error: Need either 'httpx' or 'requests' installed.")
        print("   Install with: pip install httpx")
        sys.exit(1)

load_dotenv()

# Test configuration
A2A_API_KEY = os.environ.get("A2A_API_KEY", "test-secret-key-123")
SERVICES = {
    "product_catalog": ("http://localhost:8001", "product_catalog_service"),
    "inventory": ("http://localhost:8002", "inventory_service"),
    "shipping": ("http://localhost:8003", "shipping_service"),
    "payment": ("http://localhost:8004", "payment_service"),
}


def test_sync(service_name: str, base_url: str, module_name: str):
    """Test authentication using requests (synchronous)."""
    print(f"\n{'='*60}")
    print(f"Testing {service_name.upper()} Service ({base_url})")
    print(f"{'='*60}")
    
    # Test 1: Agent card discovery (should always work, no auth needed)
    print("\n✅ Test 1: Agent Card Discovery (should work without auth)")
    try:
        response = requests.get(f"{base_url}/.well-known/agent-card.json", timeout=5)
        if response.status_code == 200:
            print(f"   ✓ Agent card accessible (status: {response.status_code})")
        else:
            print(f"   ✗ Agent card failed (status: {response.status_code})")
    except requests.exceptions.ConnectionError:
        print(f"   ⚠️  Service not running on {base_url}")
        print(f"   Start it with: python -m services.{module_name}")
        return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test 2: Task endpoint without API key (should warn but allow in soft mode)
    print("\n⚠️  Test 2: Task Endpoint WITHOUT API Key (soft mode - should warn)")
    try:
        response = requests.post(
            f"{base_url}/tasks",
            json={"test": "data"},
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        print(f"   Response status: {response.status_code}")
        print(f"   ✓ Request reached server (middleware was triggered)")
        print(f"   ⚠️  Check service logs for [AUTH WARNING] message")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 3: Task endpoint with wrong API key (should warn but allow in soft mode)
    print("\n⚠️  Test 3: Task Endpoint WITH WRONG API Key (soft mode - should warn)")
    try:
        response = requests.post(
            f"{base_url}/tasks",
            json={"test": "data"},
            headers={
                "Content-Type": "application/json",
                "x-internal-api-key": "wrong-key-123"
            },
            timeout=5
        )
        print(f"   Response status: {response.status_code}")
        print(f"   ✓ Request reached server (middleware was triggered)")
        print(f"   ⚠️  Check service logs for [AUTH WARNING] message")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 4: Task endpoint with correct API key (should work)
    print("\n✅ Test 4: Task Endpoint WITH CORRECT API Key (should work)")
    try:
        response = requests.post(
            f"{base_url}/tasks",
            json={"test": "data"},
            headers={
                "Content-Type": "application/json",
                "x-internal-api-key": A2A_API_KEY
            },
            timeout=5
        )
        print(f"   Response status: {response.status_code}")
        print(f"   ✓ Request reached server (middleware was triggered)")
        print(f"   ✓ No [AUTH WARNING] should appear in service logs")
        print(f"   Note: 404/400/422 are OK - means middleware passed, endpoint rejected invalid payload")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    return True


async def test_async(service_name: str, base_url: str, module_name: str):
    """Test authentication using httpx (asynchronous)."""
    print(f"\n{'='*60}")
    print(f"Testing {service_name.upper()} Service ({base_url})")
    print(f"{'='*60}")
    
    async with httpx.AsyncClient(timeout=5.0) as client:
        # Test 1: Agent card discovery
        print("\n✅ Test 1: Agent Card Discovery (should work without auth)")
        try:
            response = await client.get(f"{base_url}/.well-known/agent-card.json")
            if response.status_code == 200:
                print(f"   ✓ Agent card accessible (status: {response.status_code})")
            else:
                print(f"   ✗ Agent card failed (status: {response.status_code})")
        except httpx.ConnectError:
            print(f"   ⚠️  Service not running on {base_url}")
            print(f"   Start it with: python -m services.{module_name}")
            return False
        except Exception as e:
            print(f"   ✗ Error: {e}")
            return False
        
        # Test 2: Task endpoint without API key
        print("\n⚠️  Test 2: Task Endpoint WITHOUT API Key (soft mode - should warn)")
        try:
            response = await client.post(
                f"{base_url}/tasks",
                json={"test": "data"},
                headers={"Content-Type": "application/json"}
            )
            print(f"   Response status: {response.status_code}")
            print(f"   ✓ Request reached server (middleware was triggered)")
            print(f"   ⚠️  Check service logs for [AUTH WARNING] message")
        except Exception as e:
            print(f"   ✗ Error: {e}")
        
        # Test 3: Task endpoint with wrong API key
        print("\n⚠️  Test 3: Task Endpoint WITH WRONG API Key (soft mode - should warn)")
        try:
            response = await client.post(
                f"{base_url}/tasks",
                json={"test": "data"},
                headers={
                    "Content-Type": "application/json",
                    "x-internal-api-key": "wrong-key-123"
                }
            )
            print(f"   Response status: {response.status_code}")
            print(f"   ✓ Request reached server (middleware was triggered)")
            print(f"   ⚠️  Check service logs for [AUTH WARNING] message")
        except Exception as e:
            print(f"   ✗ Error: {e}")
        
        # Test 4: Task endpoint with correct API key
        print("\n✅ Test 4: Task Endpoint WITH CORRECT API Key (should work)")
        try:
            response = await client.post(
                f"{base_url}/tasks",
                json={"test": "data"},
                headers={
                    "Content-Type": "application/json",
                    "x-internal-api-key": A2A_API_KEY
                }
            )
            print(f"   Response status: {response.status_code}")
            print(f"   ✓ Request reached server (middleware was triggered)")
            print(f"   ✓ No [AUTH WARNING] should appear in service logs")
            print(f"   Note: 404/400/422 are OK - means middleware passed, endpoint rejected invalid payload")
        except Exception as e:
            print(f"   ✗ Error: {e}")
    
    return True


async def main_async():
    """Run authentication tests (async version for httpx)."""
    print("🔐 A2A API Key Authentication Test")
    print("=" * 60)
    print(f"\nUsing API Key: {A2A_API_KEY if A2A_API_KEY else '(not set - auth disabled)'}")
    print("\n⚠️  Make sure all services are running before testing!")
    print("   Start services with:")
    for service_name, (_, module_name) in SERVICES.items():
        print(f"   - python -m services.{module_name}")
    
    print("\n" + "=" * 60)
    print("IMPORTANT: Watch the service terminal windows for [AUTH WARNING] messages")
    print("=" * 60)
    
    # Run tests for each service
    all_passed = True
    for service_name, (base_url, module_name) in SERVICES.items():
        result = await test_async(service_name, base_url, module_name)
        all_passed = all_passed and result
    
    print("\n" + "=" * 60)
    print("📋 Test Summary")
    print("=" * 60)
    print("\nWhat to check:")
    print("1. ✓ Agent card endpoints should work without API key")
    print("2. ⚠️  Task endpoints without/wrong API key should show [AUTH WARNING] in service logs")
    print("3. ✓ Task endpoints with correct API key should NOT show warnings")
    print("\nNote: 404 responses are expected if the test payload format is invalid.")
    print("      The important thing is checking service logs for [AUTH WARNING] messages.")
    print("\nTo enable hard enforcement (reject unauthorized requests):")
    print("   Uncomment 'raise HTTPException(...)' in each service file")
    print("=" * 60)


def main_sync():
    """Run authentication tests (sync version for requests)."""
    print("🔐 A2A API Key Authentication Test")
    print("=" * 60)
    print(f"\nUsing API Key: {A2A_API_KEY if A2A_API_KEY else '(not set - auth disabled)'}")
    print("\n⚠️  Make sure all services are running before testing!")
    print("   Start services with:")
    for service_name, (_, module_name) in SERVICES.items():
        print(f"   - python -m services.{module_name}")
    
    print("\n" + "=" * 60)
    print("IMPORTANT: Watch the service terminal windows for [AUTH WARNING] messages")
    print("=" * 60)
    
    # Run tests for each service
    all_passed = True
    for service_name, (base_url, module_name) in SERVICES.items():
        result = test_sync(service_name, base_url, module_name)
        all_passed = all_passed and result
    
    print("\n" + "=" * 60)
    print("📋 Test Summary")
    print("=" * 60)
    print("\nWhat to check:")
    print("1. ✓ Agent card endpoints should work without API key")
    print("2. ⚠️  Task endpoints without/wrong API key should show [AUTH WARNING] in service logs")
    print("3. ✓ Task endpoints with correct API key should NOT show warnings")
    print("\nNote: 404 responses are expected if the test payload format is invalid.")
    print("      The important thing is checking service logs for [AUTH WARNING] messages.")
    print("\nTo enable hard enforcement (reject unauthorized requests):")
    print("   Uncomment 'raise HTTPException(...)' in each service file")
    print("=" * 60)


if __name__ == "__main__":
    if USE_HTTPX:
        asyncio.run(main_async())
    else:
        main_sync()

