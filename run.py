"""
Quick start script for the Student Risk Prediction System
"""

import os
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'flask', 'pandas', 'numpy', 'sklearn', 
        'joblib', 'langchain', 'openai'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print("[X] Missing required packages:")
        for pkg in missing:
            print(f"   - {pkg}")
        print("\n[!] Install them with: py -m pip install -r requirements.txt")
        return False
    return True


def main():
    print("\n" + "="*70)
    print("STUDENT RISK PREDICTION SYSTEM")
    print("="*70)
    
    # Check dependencies
    print("\n[*] Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    print("[OK] All dependencies installed")
    
    # Check data file
    print("\n[*] Checking data files...")
    if os.path.exists('data/sample_students.csv'):
        print("[OK] Sample data found")
    else:
        print("[X] Sample data not found at data/sample_students.csv")
        sys.exit(1)
    
    # Check for OpenAI key
    print("\n[*] Checking OpenAI configuration...")
    if os.path.exists('.env'):
        print("[OK] .env file found")
        from dotenv import load_dotenv
        load_dotenv()
        if os.getenv('OPENAI_API_KEY'):
            print("[OK] OpenAI API key configured (AI-powered recommendations enabled)")
        else:
            print("[!] OpenAI API key not set (will use rule-based recommendations)")
    else:
        print("[!] No .env file (will use rule-based recommendations)")
        print("   To enable AI recommendations: copy .env.example to .env and add your API key")
    
    print("\n" + "="*70)
    print("Starting the application...")
    print("="*70)
    print("\n>> Access the dashboard at: http://localhost:5000")
    print(">> Press Ctrl+C to stop the server\n")
    print("="*70 + "\n")
    
    # Start the Flask app
    from app import app, load_student_data, initialize_model
    
    load_student_data()
    initialize_model()
    
    app.run(debug=True, host='0.0.0.0', port=5000)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nShutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
