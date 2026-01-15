#!/usr/bin/env python3
"""
List all sessions stored in memory for a specific user
"""
import os
from bedrock_agentcore.memory import MemoryClient

REGION = os.getenv("AWS_REGION", "ap-south-1")
client = MemoryClient(region_name=REGION)

# Get memory ID
memory_name = "Sentra_Agent_Memory_V1"
memories = client.list_memories()
existing = next((m for m in memories if m["id"].startswith(memory_name)), None)

if not existing:
    print("No memory found!")
    exit(1)

memory_id = existing["id"]
print(f"Memory ID: {memory_id}\n")

# Try to list all events for kamaljeet.singh
actor_id = "kamaljeet.singh"
print(f"Searching for sessions for actor: {actor_id}\n")
print("="*70)

# We'll try a few common session patterns
test_sessions = [
    "sentra_session",  # Old hardcoded session
    "1765536611",  # Recent timestamp-based
]

# Also check if there are any recent sessions by trying to get memory
# AWS Bedrock Memory doesn't have a "list all sessions" API, so we need to know the session_id
print("Note: AWS Bedrock Memory requires knowing the session_id to retrieve data.")
print("Checking known session patterns...\n")

for session_id in test_sessions:
    try:
        turns = client.get_last_k_turns(
            memory_id=memory_id,
            actor_id=actor_id,
            session_id=session_id,
            k=1
        )
        if turns:
            print(f"✅ Found session: {session_id}")
            print(f"   Has {len(turns)} turn(s)")
        else:
            print(f"❌ No data for session: {session_id}")
    except Exception as e:
        print(f"❌ Error checking session {session_id}: {str(e)}")

print("\n" + "="*70)
print("\nTo view a specific session, use:")
print(f"python3 view_store_memory.py {actor_id} <session_id>")
