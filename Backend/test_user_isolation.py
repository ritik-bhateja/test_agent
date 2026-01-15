#!/usr/bin/env python3
"""Test user isolation"""
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
user_1 = "test_user_alice"
user_2 = "test_user_bob"
session_1 = f"alice_session_{timestamp}_1234567890123456789"
session_2 = f"bob_session_{timestamp}_1234567890123456789"

print("\n🧪 User Isolation Test")
print("="*60)
print(f"User 1: {user_1}, Session: {session_1}")
print(f"User 2: {user_2}, Session: {session_2}")

# User 1 - Ask about policies
print("\n📝 User 1 (Alice) - Message 1:")
call_agent("Show me policy count by type", user_1, session_1)
time.sleep(3)

# User 2 - Ask about loans
print("\n📝 User 2 (Bob) - Message 1:")
call_agent("What is the average loan balance?", user_2, session_2)
time.sleep(3)

# User 1 - Memory test (should remember policies)
print("\n📝 User 1 (Alice) - Message 2 (Memory Test):")
print("   Expected: Should remember 'policy' question")
result_1 = call_agent("What did I just ask about?", user_1, session_1)
time.sleep(3)

# User 2 - Memory test (should remember loans)
print("\n📝 User 2 (Bob) - Message 2 (Memory Test):")
print("   Expected: Should remember 'loan' question")
result_2 = call_agent("What did I just ask about?", user_2, session_2)

# Verify
print("\n" + "="*60)
print("🎯 VERIFICATION:")
print("="*60)

explanation_1 = result_1.get('explanation', '').lower()
explanation_2 = result_2.get('explanation', '').lower()

user_1_correct = 'polic' in explanation_1  # matches 'policy' or 'policies'
user_2_correct = 'loan' in explanation_2

print(f"User 1 (Alice) has 'policy': {user_1_correct}")
print(f"User 2 (Bob) has 'loan': {user_2_correct}")

if user_1_correct and user_2_correct:
    print("\n✅ SUCCESS: Users are properly isolated!")
else:
    print("\n❌ FAILED: User isolation not working")
    print(f"User 1 response: {explanation_1[:200]}")
    print(f"User 2 response: {explanation_2[:200]}")
