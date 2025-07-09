"""
Create this script to check and fix immediate issues
Run: python fix_critical_issues.py
"""
import os
import sys

def check_critical_issues():
    issues = []
    
    # Check if DEBUG_MODE is properly set
    try:
        with open('app.py', 'r') as f:
            content = f.read()
            if 'DEBUG_MODE = True' in content:
                issues.append("🚨 CRITICAL: DEBUG_MODE is enabled - This bypasses authentication!")
    except FileNotFoundError:
        issues.append("❌ app.py not found")
    
    # Check for environment file
    if not os.path.exists('.env'):
        issues.append("⚠️  Missing .env file for environment variables")
    
    # Check database configuration
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        issues.append("⚠️  DATABASE_URL not configured")
    
    # Check essential API keys
    if not os.environ.get('OPENAI_API_KEY'):
        issues.append("⚠️  OPENAI_API_KEY not configured")
    
    if not os.environ.get('SENDGRID_API_KEY'):
        issues.append("⚠️  SENDGRID_API_KEY not configured")
    
    return issues

def main():
    print("F.A.C.T.S Project Health Check")
    print("=" * 40)
    
    issues = check_critical_issues()
    
    if not issues:
        print("✅ No critical issues found!")
        return
    
    print(f"Found {len(issues)} issues:\n")
    for issue in issues:
        print(issue)
    
    print("\n" + "=" * 40)
    print("📋 NEXT STEPS:")
    print("1. Create .env file with your environment variables")
    print("2. Set DEBUG_MODE = False in production")
    print("3. Configure your database and API keys")
    print("4. Test all functionality before deployment")

if __name__ == "__main__":
    main()
