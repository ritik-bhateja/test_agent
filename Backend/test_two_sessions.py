#!/usr/bin/env python3
"""Test two different sessions"""
import boto3
import json
import time

AGENT_ARN = 'arn:aws:bedrock-agentcore:ap-south-1:628897991744:runtime/Sentra_Agent-vtVCPEFWbx'
REGION = 'ap-south-1'

def call_agent(query, user_id, session_id):
    client = boto3.client('bedrock-agentcore', region_name=REGION)
    payload = json.dumps({
        "user_query": query, 
        "user_id": user_id,
        "session_id": session_id
    })
    
    print(f"\n{'='*60}")
    print(f"Query: {query}")
    print(f"User: {user_id}")
    print(f"Session: {session_id}")
    print(f"{'='*60}")
    
    response = client.invoke_agent_runtime(
        agentRuntimeArn=AGENT_ARN,
        runtimeSessionId=session_id,
        payload=payload,
        qualifier="DEFAULT"
    )
    
    response_body = response['response'].read()
    response_data = json.loads(response_body)
    explanation = response_data.get('explanation', str(response_data))
    print(f"Response: {explanation[:150]}...")
    return response_data

timestamp = int(time.time())
user_id = "two_session_test_user"
session_1 = f"two_session_test_1_{timestamp}_1234567890123456789"
session_2 = f"two_session_test_2_{timestamp}_1234567890123456789"

print("\n🧪 Two Session Isolation Test")
print("="*60)
print(f"Session 1: {session_1}")
print(f"Session 2: {session_2}")

# Session 1 - First message
print("\n📝 Session 1 - Message 1:")
call_agent("What is the total premium?", user_id, session_1)
time.sleep(3)

# Session 2 - First message
print("\n📝 Session 2 - Message 1:")
call_agent("How many customers do we have?", user_id, session_2)
time.sleep(3)

# Session 1 - Memory test (should remember premium)
print("\n📝 Session 1 - Message 2 (Memory Test):")
print("   Expected: Should remember 'premium' question")
result_1 = call_agent("What was my previous question?", user_id, session_1)
time.sleep(3)

# Session 2 - Memory test (should remember customers)
print("\n📝 Session 2 - Message 2 (Memory Test):")
print("   Expected: Should remember 'customers' question")
result_2 = call_agent("What was my previous question?", user_id, session_2)

# Verify
print("\n" + "="*60)
print("🎯 VERIFICATION:")
print("="*60)

explanation_1 = result_1.get('explanation', '').lower()
explanation_2 = result_2.get('explanation', '').lower()

session_1_correct = 'premium' in explanation_1
session_2_correct = 'customer' in explanation_2

print(f"Session 1 has 'premium': {session_1_correct}")
print(f"Session 2 has 'customer': {session_2_correct}")

if session_1_correct and session_2_correct:
    print("\n✅ SUCCESS: Sessions are properly isolated!")
else:
    print("\n❌ FAILED: Session isolation not working")
    print(f"Session 1 response: {explanation_1[:200]}")
    print(f"Session 2 response: {explanation_2[:200]}")
