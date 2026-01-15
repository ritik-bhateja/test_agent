#!/usr/bin/env python3
"""Test memory functionality and session isolation"""
import boto3
import json
import time

AGENT_ARN = 'arn:aws:bedrock-agentcore:ap-south-1:628897991744:runtime/Sentra_Agent-vtVCPEFWbx'
REGION = 'ap-south-1'

def call_agent(query, user_id, session_id, runtime_session_id=None):
    """Call the agent with proper user_id and session_id"""
    client = boto3.client('bedrock-agentcore', region_name=REGION)
    payload = json.dumps({
        "user_query": query, 
        "user_id": user_id,
        "session_id": session_id
    })
    
    # Use session_id as runtimeSessionId if not provided
    if runtime_session_id is None:
        runtime_session_id = session_id
    
    print(f"\n{'='*60}")
    print(f"Query: {query}")
    print(f"User: {user_id}, Session: {session_id}")
    print(f"Runtime Session: {runtime_session_id}")
    print(f"{'='*60}")
    
    response = client.invoke_agent_runtime(
        agentRuntimeArn=AGENT_ARN,
        runtimeSessionId=runtime_session_id,
        payload=payload,
        qualifier="DEFAULT"
    )
    
    response_body = response['response'].read()
    response_data = json.loads(response_body)
    explanation = response_data.get('explanation', str(response_data))
    print(f"Response: {explanation[:200]}...")
    return response_data

def test_session_isolation():
    """Test that different sessions maintain separate conversation contexts"""
    print("\n" + "="*80)
    print("🧪 TEST 1: Session Isolation (Same User, Different Sessions)")
    print("="*80)
    
    timestamp = int(time.time())
    user_id = "test_user_isolation_v1"
    session_1 = f"test_session_1_{timestamp}_12345678901234"
    session_2 = f"test_session_2_{timestamp}_12345678901234"
    
    print(f"\n🔑 Test Setup:")
    print(f"   User ID: {user_id}")
    print(f"   Session 1 ID: {session_1}")
    print(f"   Session 2 ID: {session_2}")
    
    # Session 1: Ask about insurance
    print("\n📝 Session 1 - Message 1:")
    call_agent("What is the total premium collected?", user_id, session_1)
    time.sleep(3)
    
    # Session 2: Ask about banking
    print("\n📝 Session 2 - Message 1:")
    call_agent("How many customers do we have?", user_id, session_2)
    time.sleep(3)
    
    # Session 1: Ask about previous question (should remember insurance)
    print("\n📝 Session 1 - Message 2 (Memory Test):")
    print("   Expected: Should remember 'premium' question")
    result_1 = call_agent("What was my previous question?", user_id, session_1)
    time.sleep(3)
    
    # Session 2: Ask about previous question (should remember banking)
    print("\n📝 Session 2 - Message 2 (Memory Test):")
    print("   Expected: Should remember 'customers' question")
    result_2 = call_agent("What was my previous question?", user_id, session_2)
    
    # Verify results
    print("\n" + "="*80)
    print("🎯 SESSION ISOLATION TEST RESULTS:")
    print("="*80)
    
    explanation_1 = result_1.get('explanation', '').lower()
    explanation_2 = result_2.get('explanation', '').lower()
    
    session_1_correct = 'premium' in explanation_1 or 'insurance' in explanation_1
    session_2_correct = 'customer' in explanation_2 or 'banking' in explanation_2
    
    if session_1_correct and session_2_correct:
        print("✅ SUCCESS: Sessions are properly isolated!")
        print(f"   Session 1 remembered: insurance/premium")
        print(f"   Session 2 remembered: customers/banking")
        return True
    else:
        print("❌ FAILED: Session isolation not working properly")
        print(f"   Session 1 response: {explanation_1[:100]}")
        print(f"   Session 2 response: {explanation_2[:100]}")
        return False

def test_user_isolation():
    """Test that different users maintain separate conversation contexts"""
    print("\n" + "="*80)
    print("🧪 TEST 2: User Isolation (Different Users, Different Sessions)")
    print("="*80)
    
    user_1 = "test_user_alice_v1"
    user_2 = "test_user_bob_v1"
    session_1 = f"test_alice_session_{int(time.time())}_12345678901234"
    session_2 = f"test_bob_session_{int(time.time())}_12345678901234"
    
    # User 1: Ask about policies
    print("\n📝 User 1 (Alice) - Message 1:")
    call_agent("Show me policy count by type", user_1, session_1)
    time.sleep(2)
    
    # User 2: Ask about loans
    print("\n📝 User 2 (Bob) - Message 1:")
    call_agent("What is the average loan balance?", user_2, session_2)
    time.sleep(2)
    
    # User 1: Ask about previous question (should remember policies)
    print("\n📝 User 1 (Alice) - Message 2 (Memory Test):")
    result_1 = call_agent("What did I just ask about?", user_1, session_1)
    time.sleep(2)
    
    # User 2: Ask about previous question (should remember loans)
    print("\n📝 User 2 (Bob) - Message 2 (Memory Test):")
    result_2 = call_agent("What did I just ask about?", user_2, session_2)
    
    # Verify results
    print("\n" + "="*80)
    print("🎯 USER ISOLATION TEST RESULTS:")
    print("="*80)
    
    explanation_1 = result_1.get('explanation', '').lower()
    explanation_2 = result_2.get('explanation', '').lower()
    
    user_1_correct = 'policy' in explanation_1 or 'policies' in explanation_1
    user_2_correct = 'loan' in explanation_2
    
    if user_1_correct and user_2_correct:
        print("✅ SUCCESS: Users are properly isolated!")
        print(f"   User 1 (Alice) remembered: policies")
        print(f"   User 2 (Bob) remembered: loans")
        return True
    else:
        print("❌ FAILED: User isolation not working properly")
        print(f"   User 1 response: {explanation_1[:100]}")
        print(f"   User 2 response: {explanation_2[:100]}")
        return False

def test_identifier_propagation():
    """Test that identifiers are properly propagated through the system"""
    print("\n" + "="*80)
    print("🧪 TEST 3: Identifier Propagation")
    print("="*80)
    
    user_id = "test_propagation_user"
    session_id = f"test_propagation_session_{int(time.time())}_12345678901234"
    
    print("\n📝 Sending query with specific identifiers:")
    print(f"   user_id: {user_id}")
    print(f"   session_id: {session_id}")
    
    try:
        result = call_agent("How many insurance policies do we have?", user_id, session_id)
        
        print("\n" + "="*80)
        print("🎯 IDENTIFIER PROPAGATION TEST RESULTS:")
        print("="*80)
        
        if result.get('type') and result.get('explanation'):
            print("✅ SUCCESS: Request processed successfully with identifiers")
            print(f"   Response type: {result.get('type')}")
            return True
        else:
            print("❌ FAILED: Invalid response format")
            return False
    except Exception as e:
        print("❌ FAILED: Error during request")
        print(f"   Error: {str(e)}")
        return False

def test_missing_identifiers():
    """Test that missing identifiers are properly validated"""
    print("\n" + "="*80)
    print("🧪 TEST 4: Missing Identifier Validation")
    print("="*80)
    
    client = boto3.client('bedrock-agentcore', region_name=REGION)
    
    # Test missing user_id
    print("\n📝 Test 4a: Missing user_id")
    try:
        payload = json.dumps({
            "user_query": "test query",
            "session_id": "test_session_12345678901234567890123"
        })
        
        response = client.invoke_agent_runtime(
            agentRuntimeArn=AGENT_ARN,
            runtimeSessionId="test_session_12345678901234567890123",
            payload=payload,
            qualifier="DEFAULT"
        )
        
        response_body = response['response'].read()
        response_data = json.loads(response_body)
        explanation = response_data.get('explanation', '')
        
        if 'user_id is required' in explanation or 'missing' in explanation.lower():
            print("✅ SUCCESS: Missing user_id properly detected")
            test_4a = True
        else:
            print("❌ FAILED: Missing user_id not detected")
            print(f"   Response: {explanation}")
            test_4a = False
    except Exception as e:
        print(f"⚠️  Exception occurred: {str(e)}")
        test_4a = False
    
    time.sleep(2)
    
    # Test missing session_id
    print("\n📝 Test 4b: Missing session_id")
    try:
        payload = json.dumps({
            "user_query": "test query",
            "user_id": "test_user"
        })
        
        response = client.invoke_agent_runtime(
            agentRuntimeArn=AGENT_ARN,
            runtimeSessionId="test_session_12345678901234567890123",
            payload=payload,
            qualifier="DEFAULT"
        )
        
        response_body = response['response'].read()
        response_data = json.loads(response_body)
        explanation = response_data.get('explanation', '')
        
        if 'session_id is required' in explanation or 'missing' in explanation.lower():
            print("✅ SUCCESS: Missing session_id properly detected")
            test_4b = True
        else:
            print("❌ FAILED: Missing session_id not detected")
            print(f"   Response: {explanation}")
            test_4b = False
    except Exception as e:
        print(f"⚠️  Exception occurred: {str(e)}")
        test_4b = False
    
    print("\n" + "="*80)
    print("🎯 MISSING IDENTIFIER VALIDATION TEST RESULTS:")
    print("="*80)
    
    if test_4a and test_4b:
        print("✅ SUCCESS: All validation tests passed")
        return True
    else:
        print("❌ FAILED: Some validation tests failed")
        return False

if __name__ == "__main__":
    print("\n" + "="*80)
    print("🚀 STARTING END-TO-END SESSION ISOLATION TESTS")
    print("="*80)
    
    results = []
    
    # Run all tests
    results.append(("Session Isolation", test_session_isolation()))
    time.sleep(3)
    
    results.append(("User Isolation", test_user_isolation()))
    time.sleep(3)
    
    results.append(("Identifier Propagation", test_identifier_propagation()))
    time.sleep(3)
    
    results.append(("Missing Identifier Validation", test_missing_identifiers()))
    
    # Print final summary
    print("\n" + "="*80)
    print("📊 FINAL TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print("\n" + "="*80)
    print(f"🎯 OVERALL RESULT: {passed}/{total} tests passed")
    print("="*80)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Session isolation is working correctly.")
        exit(0)
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the output above.")
        exit(1)
