#!/usr/bin/env python3
"""Simple test script for the simulation backend."""

import json
import os
from urllib import error, request

BASE_URL = "http://localhost:8000"


def test_health_check():
    """Test GET / endpoint."""
    print("\n=== Testing Health Check ===")
    try:
        with request.urlopen(f"{BASE_URL}/") as response:
            data = json.loads(response.read().decode())
            print(f"✅ Status: {response.status}")
            print(f"   Response: {data}")
    except Exception as exc:
        print(f"❌ Error: {exc}")


def test_chat(prompt: str, session_id: str):
    """Test POST /chat endpoint."""
    print(f"\n=== Testing Chat: '{prompt}' ===")
    body = {"prompt": prompt, "session_id": session_id}
    
    req = request.Request(
        f"{BASE_URL}/chat",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    
    try:
        with request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            print(f"✅ Status: {response.status}")
            print(f"   Actions: {len(data['actions'])} action(s)")
            for i, action in enumerate(data["actions"], 1):
                print(f"     {i}. {action['type']}")
            print(f"   Scene State: {data['scene_state']}")
    except error.HTTPError as exc:
        print(f"❌ HTTP Error {exc.code}: {exc.read().decode()}")
    except Exception as exc:
        print(f"❌ Error: {exc}")


if __name__ == "__main__":
    print("=" * 60)
    print("Simulation Backend Test Suite")
    print("=" * 60)
    
    # Test health check
    test_health_check()
    
    # Test various prompts
    test_chat("Create a warehouse with a robot", "test1")
    test_chat("Add a shelf", "test2")
    test_chat("Tell me a joke", "test3")
    test_chat("Create a warehouse, add a robot, place 5 shelves, then move one shelf", "test4")
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)
