#!/usr/bin/env python3
"""
Comprehensive Test Suite Summary
Tests all aspects of session memory isolation
"""
import subprocess
import sys

def run_test(test_name, test_file):
    """Run a test and return the result"""
    print(f"\n{'='*80}")
    print(f"Running: {test_name}")
    print(f"{'='*80}")
    
    result = subprocess.run(
        ['python', test_file],
        capture_output=True,
        text=True,
        timeout=180
    )
    
    success = result.returncode == 0
    status = "✅ PASSED" if success else "❌ FAILED"
    print(f"{status}: {test_name}")
    
    return success, result.stdout, result.stderr

def main():
    print("\n" + "="*80)
    print("🧪 SESSION MEMORY ISOLATION - COMPREHENSIVE TEST SUITE")
    print("="*80)
    print("\nRunning all test cases to verify session and user isolation...")
    
    tests = [
        ("Test 1: Simple Session Memory", "test_simple_session.py"),
        ("Test 2: Two Session Isolation", "test_two_sessions.py"),
        ("Test 3: User Isolation", "test_user_isolation.py"),
        ("Test 4: Direct Memory Client", "test_memory_direct.py"),
    ]
    
    results = []
    
    for test_name, test_file in tests:
        try:
            success, stdout, stderr = run_test(test_name, test_file)
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ ERROR running {test_name}: {str(e)}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "="*80)
    print("📊 FINAL TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print("\n" + "="*80)
    print(f"🎯 OVERALL RESULT: {passed}/{total} tests passed")
    print("="*80)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("\n✅ Session Isolation: Working correctly")
        print("✅ User Isolation: Working correctly")
        print("✅ Memory Persistence: Working correctly")
        print("✅ Identifier Propagation: Working correctly")
        print("\n📝 Summary:")
        print("   • Different sessions maintain separate conversation contexts")
        print("   • Different users maintain separate conversation contexts")
        print("   • Memory persists correctly within sessions")
        print("   • Identifiers flow correctly through all system layers")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
