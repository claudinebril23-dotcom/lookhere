#!/usr/bin/env python
"""
Quick Installation Script for Photobooth Booking System
This script installs dependencies and sets up the database
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during {description}:")
        print(f"   Command: {command}")
        print(f"   Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} is not supported")
        print("   Please use Python 3.8 or higher")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_dependencies():
    """Install required Python packages"""
    packages = [
        "Django>=6.0.3",
        "Pillow>=10.0.0", 
        "psycopg2-binary>=2.9.0",
        "python-dotenv>=1.0.0"
    ]
    
    for package in packages:
        if not run_command(f"pip install {package}", f"Installing {package}"):
            return False
    
    return True

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_file = Path(".env")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    print("\n📝 Creating .env file...")
    
    # Get database password from user
    print("\n🔐 Database Configuration:")
    db_password = input("Enter PostgreSQL password (default: 'password'): ").strip()
    if not db_password:
        db_password = "password"
    
    env_content = f"""# Database Configuration
DB_NAME=photobooth_db
DB_USER=postgres
DB_PASSWORD={db_password}
DB_HOST=localhost
DB_PORT=5432

# Email Configuration (optional)
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password

# AWS Configuration (optional)
AWS_REGION=ap-southeast-1
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
"""
    
    try:
        with open(".env", "w") as f:
            f.write(env_content)
        print("✅ .env file created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def check_postgresql():
    """Check if PostgreSQL is accessible"""
    try:
        result = subprocess.run(
            "psql --version", 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True
        )
        print(f"✅ PostgreSQL found: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError:
        print("⚠️  PostgreSQL not found in PATH")
        print("   Please make sure PostgreSQL is installed and accessible")
        print("   Download from: https://www.postgresql.org/download/")
        
        # Ask user if they want to continue anyway
        response = input("\nContinue anyway? (y/N): ").strip().lower()
        return response in ['y', 'yes']

def main():
    """Main installation function"""
    print("🚀 Photobooth Booking System - Quick Installation")
    print("=" * 55)
    
    # Step 1: Check Python version
    if not check_python_version():
        return
    
    # Step 2: Check PostgreSQL
    if not check_postgresql():
        return
    
    # Step 3: Install dependencies
    print("\n📦 Installing Python Dependencies")
    if not install_dependencies():
        print("\n❌ Installation failed. Please check the errors above.")
        return
    
    # Step 4: Create .env file
    if not create_env_file():
        return
    
    # Step 5: Run database setup
    print("\n🗄️  Setting up Database")
    if not run_command("python setup_database.py", "Database setup"):
        print("\n⚠️  Database setup failed. You can run it manually later:")
        print("   python setup_database.py")
    
    # Success message
    print("\n🎉 Installation completed successfully!")
    print("\n📝 Next Steps:")
    print("   1. Start the server: python manage.py runserver")
    print("   2. Visit: http://localhost:8000")
    print("   3. Admin panel: http://localhost:8000/admin (admin/admin123)")
    print("\n💡 Useful Commands:")
    print("   • View database: python manage.py show_db")
    print("   • Create admin user: python manage.py createsuperuser")
    print("   • Run migrations: python manage.py migrate")

if __name__ == '__main__':
    main()