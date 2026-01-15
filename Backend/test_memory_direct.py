#!/usr/bin/env python3
"""Direct test of memory client isolation"""
import time
from memory.memory_setup import client, memory_id

def test_memory_isolation():
    """Test that memory client properly isolates by session_id"""
    
    actor_id = "test_actor"
    session_1 = f"direct_test_session_1_{int(time.time())}"
    session_2 = f"direct_test_session_2_{int(time.time())}"
    
    print(f"\n🔑 Test Setup:")
    print(f"   Memory ID: {memory_id}")
    print(f"   Actor ID: {actor_id}")
    print(f"   Session 1: {session_1}")
    print(f"   Session 2: {session_2}")
    
    # Store message in session 1
    print(f"\n📝 Storing message in Session 1...")
    client.create_event(
        memory_id=memory_id,
        actor_id=actor_id,
        session_id=session_1,
        messages=[("What is the total premium?", "user")]
    )
    time.sleep(2)
    
    # Store message in session 2
    print(f"\n📝 Storing message in Session 2...")
    client.create_event(
        memory_id=memory_id,
        actor_id=actor_id,
        session_id=session_2,
        messages=[("How many customers?", "user")]
    )
    time.sleep(2)
    
    # Retrieve from session 1
    print(f"\n📚 Retrieving from Session 1...")
    turns_1 = client.get_last_k_turns(
        memory_id=memory_id,
        actor_id=actor_id,
        session_id=session_1,
        k=5
    )
    
    print(f"   Retrieved {len(turns_1)} turns")
    if turns_1:
        for i, turn in enumerate(turns_1):
            for msg in turn:
                print(f"   Turn {i}: {msg['role']} - {msg['content']['text'][:50]}")
    
    # Retrieve from session 2
    print(f"\n📚 Retrieving from Session 2...")
    turns_2 = client.get_last_k_turns(
        memory_id=memory_id,
        actor_id=actor_id,
        session_id=session_2,
        k=5
    )
    
    print(f"   Retrieved {len(turns_2)} turns")
    if turns_2:
        for i, turn in enumerate(turns_2):
            for msg in turn:
                print(f"   Turn {i}: {msg['role']} - {msg['content']['text'][:50]}")
    
    # Verify isolation
    print(f"\n🎯 Verification:")
    session_1_has_premium = any("premium" in msg['content']['text'].lower() 
                                 for turn in turns_1 for msg in turn)
    session_1_has_customers = any("customers" in msg['content']['text'].lower() 
                                   for turn in turns_1 for msg in turn)
    session_2_has_premium = any("premium" in msg['content']['text'].lower() 
                                 for turn in turns_2 for msg in turn)
    session_2_has_customers = any("customers" in msg['content']['text'].lower() 
                                   for turn in turns_2 for msg in turn)
    
    print(f"   Session 1 has 'premium': {session_1_has_premium}")
    print(f"   Session 1 has 'customers': {session_1_has_customers}")
    print(f"   Session 2 has 'premium': {session_2_has_premium}")
    print(f"   Session 2 has 'customers': {session_2_has_customers}")
    
    if session_1_has_premium and not session_1_has_customers and \
       session_2_has_customers and not session_2_has_premium:
        print(f"\n✅ SUCCESS: Memory is properly isolated by session_id!")
        return True
    else:
        print(f"\n❌ FAILED: Memory isolation is not working correctly")
        return False

if __name__ == "__main__":
    test_memory_isolation()
