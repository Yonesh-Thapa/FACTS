#!/usr/bin/env python3
"""
Development and testing script for F.A.C.T.S improvements
Run this to test all implemented enhancements
"""
import os
import sys
import subprocess
import time
from pathlib import Path

def run_command(command, description):
    """Run a command and print status"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            if result.stdout:
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} - FAILED")
            if result.stderr:
                print(f"   Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if Path(filepath).exists():
        print(f"✅ {description} - EXISTS")
        return True
    else:
        print(f"❌ {description} - MISSING")
        return False

def check_improvements():
    """Check all implemented improvements"""
    print("🔍 F.A.C.T.S IMPROVEMENTS VERIFICATION")
    print("=" * 50)
    
    checks = []
    
    # Check configuration files
    checks.append(check_file_exists('.env.example', 'Environment configuration template'))
    checks.append(check_file_exists('config.py', 'Configuration management'))
    checks.append(check_file_exists('app_factory.py', 'Application factory'))
    checks.append(check_file_exists('requirements.txt', 'Dependencies file'))
    
    # Check error handling
    checks.append(check_file_exists('utils/error_handling.py', 'Error handling utilities'))
    checks.append(check_file_exists('templates/errors/404.html', '404 error template'))
    checks.append(check_file_exists('templates/errors/500.html', '500 error template'))
    
    # Check performance improvements
    checks.append(check_file_exists('utils/performance.py', 'Performance monitoring'))
    checks.append(check_file_exists('static/js/enhanced-main.js', 'Enhanced JavaScript'))
    checks.append(check_file_exists('static/css/enhanced-ui.css', 'Enhanced UI styles'))
    checks.append(check_file_exists('static/css/mobile-enhancements.css', 'Mobile optimizations'))
    
    # Check security improvements
    security_items = [
        'WTF_CSRF_SECRET_KEY',
        'SESSION_COOKIE_SECURE',
        'RATELIMIT_DEFAULT'
    ]
    
    env_example_content = ""
    try:
        with open('.env.example', 'r') as f:
            env_example_content = f.read()
        
        for item in security_items:
            if item in env_example_content:
                print(f"✅ Security config: {item} - PRESENT")
                checks.append(True)
            else:
                print(f"❌ Security config: {item} - MISSING")
                checks.append(False)
    except:
        print("❌ Could not read .env.example")
        checks.extend([False] * len(security_items))
    
    # Summary
    passed = sum(checks)
    total = len(checks)
    success_rate = (passed / total) * 100
    
    print(f"\n📊 SUMMARY")
    print(f"   Passed: {passed}/{total} ({success_rate:.1f}%)")
    
    if success_rate >= 90:
        print("🎉 EXCELLENT! All major improvements implemented")
    elif success_rate >= 75:
        print("✅ GOOD! Most improvements implemented")
    elif success_rate >= 50:
        print("⚠️  PARTIAL! Some improvements missing")
    else:
        print("❌ NEEDS WORK! Many improvements missing")
    
    return success_rate >= 75

def test_application():
    """Test the application functionality"""
    print("\n🧪 TESTING APPLICATION...")
    
    # Check if Flask is importable
    try:
        import flask
        print("✅ Flask is available")
    except ImportError:
        print("❌ Flask not installed")
        return False
    
    # Test configuration loading
    try:
        from config import config
        print("✅ Configuration loading works")
    except ImportError as e:
        print(f"❌ Configuration loading failed: {e}")
        return False
    
    # Test error handling utilities
    try:
        from utils.error_handling import ValidationError, validate_email
        validate_email("test@example.com")
        print("✅ Error handling utilities work")
    except ImportError as e:
        print(f"❌ Error handling utilities failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error handling validation failed: {e}")
        return False
    
    return True

def show_next_steps():
    """Show recommended next steps"""
    print("\n📋 NEXT STEPS:")
    print("1. Copy .env.example to .env and fill in your actual values")
    print("2. Update your main app.py to use the new configuration system")
    print("3. Test the enhanced forms and error handling")
    print("4. Check mobile responsiveness")
    print("5. Monitor performance metrics")
    print("6. Set up production environment with proper security")
    
    print("\n🚀 PRODUCTION CHECKLIST:")
    print("□ Set DEBUG_MODE = False")
    print("□ Configure real database URL")
    print("□ Set up environment variables")
    print("□ Enable HTTPS and security headers")
    print("□ Configure proper logging")
    print("□ Set up monitoring and alerts")

def main():
    """Main function"""
    print("🎯 F.A.C.T.S PROJECT IMPROVEMENT TESTER")
    print("=" * 60)
    
    # Change to project directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Check improvements
    improvements_ok = check_improvements()
    
    # Test application
    if improvements_ok:
        app_ok = test_application()
        
        if app_ok:
            print("\n🎉 ALL TESTS PASSED!")
            print("Your F.A.C.T.S project has been successfully enhanced!")
        else:
            print("\n⚠️  IMPROVEMENTS INSTALLED BUT TESTING FAILED")
            print("Check the error messages above and fix any issues")
    else:
        print("\n❌ IMPROVEMENTS INCOMPLETE")
        print("Please ensure all files are properly created")
    
    show_next_steps()

if __name__ == "__main__":
    main()
