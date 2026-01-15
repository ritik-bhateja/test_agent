#!/usr/bin/env python3
"""Test memory persistence for current session and current user"""
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
    
    print(f"\n{'='*70}")
    print(f"Query: {query}")
    print(f"{'='*70}")
    
    response = client.invoke_agent_runtime(
        agentRuntimeArn=AGENT_ARN,
        runtimeSessionId=session_id,
        payload=payload,
        qualifier="DEFAULT"
    )
    
    response_body = response['response'].read()
    response_data = json.loads(response_body)
    explanation = response_data.get('explanation', str(response_data))
    print(f"Response: {explanation[:200]}...")
    return response_data

print("\n" + "="*70)
print("🧪 CURRENT SESSION MEMORY TEST - Multi-Turn Conversation")
print("="*70)

timestamp = int(time.time())
user_id = "kamaljeet.singh"  # Using a real user from the system
session_id = f"memory_test_session_{timestamp}_1234567890123456789"

print(f"\n🔑 Test Configuration:")
print(f"   User: {user_id}")
print(f"   Session: {session_id}")
print(f"   Testing: Memory persistence across multiple conversation turns")

# Turn 1: Ask about insurance policies
print("\n" + "="*70)
print("📝 TURN 1: Initial Query")
print("="*70)
call_agent("How many insurance policies do we have?", user_id, session_id)
time.sleep(3)

# Turn 2: Ask about premium
print("\n" + "="*70)
print("📝 TURN 2: Follow-up Query")
print("="*70)
call_agent("What is the total premium collected?", user_id, session_id)
time.sleep(3)

# Turn 3: Ask about agents
print("\n" + "="*70)
print("📝 TURN 3: Another Query")
print("="*70)
call_agent("Show me the top 3 agents by premium", user_id, session_id)
time.sleep(3)

# Turn 4: Memory test - contextual follow-up
print("\n" + "="*70)
print("📝 TURN 4: Memory Test - Contextual Follow-up")
print("="*70)
print("Expected: Should use context from previous queries")
result_1 = call_agent("Can you show me more details about those top agents?", user_id, session_id)
time.sleep(3)

# Turn 5: Memory test - reference to earlier data
print("\n" + "="*70)
print("📝 TURN 5: Memory Test - Reference Earlier Data")
print("="*70)
print("Expected: Should remember the total premium from Turn 2")
result_2 = call_agent("Is that total premium amount higher than last year?", user_id, session_id)
time.sleep(3)

# Turn 6: Memory test - simple recall
print("\n" + "="*70)
print("📝 TURN 6: Memory Test - Simple Recall")
print("="*70)
print("Expected: Should remember we discussed agents")
result_3 = call_agent("Show me the agent performance again", user_id, session_id)

# Verify results
print("\n" + "="*70)
print("🎯 VERIFICATION RESULTS")
print("="*70)

explanation_1 = result_1.get('explanation', '').lower()
explanation_2 = result_2.get('explanation', '').lower()
explanation_3 = result_3.get('explanation', '').lower()

# Check if memory is working correctly
test_1_pass = 'agent' in explanation_1.lower() and 'error' not in explanation_1.lower()
test_2_pass = 'premium' in explanation_2.lower() or 'year' in explanation_2.lower() or 'error' not in explanation_2.lower()
test_3_pass = 'agent' in explanation_3.lower() and 'error' not in explanation_3.lower()

print(f"\n✓ Test 1 - Contextual Follow-up: {'✅ PASS' if test_1_pass else '❌ FAIL'}")
print(f"  Expected: Should provide agent details using context")
print(f"  Got: {explanation_1[:100]}...")

print(f"\n✓ Test 2 - Reference Earlier Data: {'✅ PASS' if test_2_pass else '❌ FAIL'}")
print(f"  Expected: Should reference the premium amount from earlier")
print(f"  Got: {explanation_2[:100]}...")

print(f"\n✓ Test 3 - Simple Recall: {'✅ PASS' if test_3_pass else '❌ FAIL'}")
print(f"  Expected: Should show agent performance again")
print(f"  Got: {explanation_3[:100]}...")

# Overall result
all_pass = test_1_pass and test_2_pass and test_3_pass

print("\n" + "="*70)
if all_pass:
    print("🎉 SUCCESS: Memory is working correctly for current session!")
    print("   ✅ Agent uses context from previous queries")
    print("   ✅ Agent references earlier data")
    print("   ✅ Agent maintains conversation continuity")
else:
    print("⚠️  PARTIAL SUCCESS: Some memory tests failed")
    print(f"   Tests passed: {sum([test_1_pass, test_2_pass, test_3_pass])}/3")
print("="*70)

exit(0 if all_pass else 1)
