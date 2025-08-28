"""
Setup script for the LLM-Driven Autonomous Software Engineer
"""
import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required, found {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def create_virtual_environment():
    """Create a virtual environment."""
    if os.path.exists("venv"):
        print("✅ Virtual environment already exists")
        return True
    
    return run_command("python -m venv venv", "Creating virtual environment")

def install_dependencies():
    """Install Python dependencies."""
    # Determine the correct pip command
    if os.name == 'nt':  # Windows
        pip_cmd = "venv\\Scripts\\pip"
    else:  # Unix/Linux/macOS
        pip_cmd = "venv/bin/pip"
    
    return run_command(f"{pip_cmd} install -r requirements.txt", "Installing dependencies")

def setup_environment():
    """Set up environment variables."""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if not env_example.exists():
        print("❌ .env.example file not found")
        return False
    
    # Copy .env.example to .env
    try:
        with open(env_example, 'r') as src, open(env_file, 'w') as dst:
            dst.write(src.read())
        print("✅ Created .env file from template")
        print("⚠️  Please edit .env file and add your Gemini API key")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def run_basic_tests():
    """Run basic functionality tests."""
    return run_command("python test_basic.py", "Running basic tests")

def main():
    """Main setup function."""
    print("�� Setting up LLM-Driven Autonomous Software Engineer")
    print("=" * 70)
    
    # Check prerequisites
    if not check_python_version():
        return False
    
    # Create virtual environment
    if not create_virtual_environment():
        return False
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Set up environment
    if not setup_environment():
        return False
    
    # Run tests
    if not run_basic_tests():
        print("⚠️  Basic tests failed, but setup completed")
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file and add your Gemini API key")
    print("2. Activate virtual environment:")
    if os.name == 'nt':  # Windows
        print("   venv\\Scripts\\activate")
    else:  # Unix/Linux/macOS
        print("   source venv/bin/activate")
    print("3. Run the system: python main.py")
    print("4. Or run the demo: python demo.py")
    print("\n🔑 Get your Gemini API key from: https://makersuite.google.com/app/apikey")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
