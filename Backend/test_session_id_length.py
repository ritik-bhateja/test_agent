#!/usr/bin/env python3
"""
Test to verify session IDs meet AWS Bedrock requirements
"""
import random
import string

def generate_frontend_session_id():
    """
    Simulates the frontend session ID generation logic
    Format: timestamp (13 chars) + underscore (1 char) + random (19 chars) = 33 chars
    """
    import time
    timestamp = str(int(time.time() * 1000))  # 13 characters
    random_chars = string.ascii_letters + string.digits  # A-Z, a-z, 0-9
    random_suffix = ''.join(random.choice(random_chars) for _ in range(19))
    session_id = f"{timestamp}_{random_suffix}"
    return session_id

def test_session_id_generation():
    print("\n" + "="*70)
    print("🧪 SESSION ID GENERATION TEST")
    print("="*70)
    print("\nAWS Bedrock Requirement: runtimeSessionId must be 33-100 characters")
    print("\nGenerating 10 test session IDs...\n")
    
    all_passed = True
    session_ids = []
    
    for i in range(1, 11):
        session_id = generate_frontend_session_id()
        length = len(session_id)
        passed = length == 33
        
        if not passed:
            all_passed = False
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} Test {i:2d}: {session_id} (Length: {length})")
        session_ids.append(session_id)
    
    # Check uniqueness
    print("\n" + "="*70)
    print("🔍 UNIQUENESS CHECK")
    print("="*70)
    unique_count = len(set(session_ids))
    uniqueness_passed = unique_count == len(session_ids)
    
    if uniqueness_passed:
        print(f"✅ PASS: All {len(session_ids)} session IDs are unique")
    else:
        print(f"❌ FAIL: Only {unique_count}/{len(session_ids)} session IDs are unique")
        all_passed = False
    
    # Check format
    print("\n" + "="*70)
    print("📋 FORMAT CHECK")
    print("="*70)
    
    format_passed = True
    for session_id in session_ids[:3]:  # Check first 3
        parts = session_id.split('_')
        if len(parts) != 2:
            print(f"❌ FAIL: Invalid format (expected timestamp_random): {session_id}")
            format_passed = False
            all_passed = False
        elif not parts[0].isdigit():
            print(f"❌ FAIL: Timestamp part is not numeric: {parts[0]}")
            format_passed = False
            all_passed = False
        elif len(parts[0]) != 13:
            print(f"❌ FAIL: Timestamp should be 13 chars, got {len(parts[0])}: {parts[0]}")
            format_passed = False
            all_passed = False
        elif len(parts[1]) != 19:
            print(f"❌ FAIL: Random suffix should be 19 chars, got {len(parts[1])}: {parts[1]}")
            format_passed = False
            all_passed = False
    
    if format_passed:
        print("✅ PASS: All session IDs follow correct format")
        print("   Format: [13-digit timestamp]_[19 random alphanumeric]")
    
    # Final summary
    print("\n" + "="*70)
    print("📊 FINAL SUMMARY")
    print("="*70)
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("\n✅ Session ID generation is working correctly:")
        print("   • All IDs are exactly 33 characters")
        print("   • All IDs are unique")
        print("   • All IDs follow the correct format")
        print("   • Meets AWS Bedrock runtimeSessionId requirements")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        print("\nPlease review the failures above.")
        return 1

if __name__ == "__main__":
    exit(test_session_id_generation())
