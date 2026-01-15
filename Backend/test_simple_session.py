#!/usr/bin/env python3
"""Simple session isolation test"""
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
user_id = "simple_test_user"
session_1 = f"simple_session_1_{timestamp}_1234567890123456789"

print("\n🧪 Simple Session Test")
print("="*60)

# First message
print("\n📝 Message 1:")
call_agent("What is the total premium?", user_id, session_1)
time.sleep(3)

# Second message - should remember first
print("\n📝 Message 2 (Memory Test):")
result = call_agent("What was my previous question?", user_id, session_1)

explanation = result.get('explanation', '').lower()
if 'premium' in explanation:
    print("\n✅ SUCCESS: Memory is working!")
else:
    print(f"\n❌ FAILED: Memory not working. Response: {explanation[:200]}")
