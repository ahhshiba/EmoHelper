import os
import sys
import subprocess
import json
import hashlib
import site
from pathlib import Path
import shutil
import platform
from dotenv import load_dotenv

class EnvironmentManager:
    def __init__(self):
        self.workspace_dir = Path.cwd()
        self.cache_dir = Path.home() / ".diary_app_cache"
        self.packages_cache = self.cache_dir / "packages"
        self.deps_hash_file = self.cache_dir / "deps_hash.json"
        self.venv_dir = self.workspace_dir / "venv"
        self.requirements_file = self.workspace_dir / "requirements.txt"
        
        # Create cache directories
        self.cache_dir.mkdir(exist_ok=True)
        self.packages_cache.mkdir(exist_ok=True)

    def check_api_key(self):
        """Check if the API key is properly configured"""
        load_dotenv()
        api_key = os.getenv('GOOGLE_API_KEY')

        print("\nChecking Gemini API key configuration...")

        if not api_key:
            print("❌ No API key found in environment variables")
            print("Please make sure:")
            print("1. Your .env file exists in the project root directory")
            print("2. The file contains: GOOGLE_API_KEY=your_api_key_here")
            return False
        else:
            print("✅ API key found in environment variables")
            print(f"Key length: {len(api_key)} characters")
            print(f"First 8 characters: {api_key[:8]}...")
            return True

    def get_requirements_hash(self):
        """Calculate hash of requirements.txt"""
        if not self.requirements_file.exists():
            return None
        with open(self.requirements_file, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()

    def load_cached_hash(self):
        """Load cached requirements hash"""
        if not self.deps_hash_file.exists():
            return None
        try:
            with open(self.deps_hash_file) as f:
                data = json.load(f)
                return data.get("hash")
        except:
            return None

    def save_hash(self, req_hash):
        """Save current requirements hash"""
        with open(self.deps_hash_file, "w") as f:
            json.dump({"hash": req_hash}, f)

    def get_pip_path(self):
        """Get the correct pip path based on OS"""
        if platform.system() == "Windows":
            return self.venv_dir / "Scripts" / "pip.exe"
        return self.venv_dir / "bin" / "pip"

    def get_python_path(self):
        """Get the correct python interpreter path based on OS"""
        if platform.system() == "Windows":
            return self.venv_dir / "Scripts" / "python.exe"
        return self.venv_dir / "bin" / "python"

    def create_venv(self):
        """Create a new virtual environment"""
        try:
            if self.venv_dir.exists():
                shutil.rmtree(self.venv_dir)
            subprocess.run([sys.executable, "-m", "venv", str(self.venv_dir)], check=True)
            return True
        except Exception as e:
            print(f"Error creating virtual environment: {e}")
            return False

    def install_requirements(self):
        """Install requirements using cached packages when possible"""
        pip_path = self.get_pip_path()
        
        try:
            # Update pip first
            subprocess.run([str(pip_path), "install", "--upgrade", "pip"], check=True)
            
            # Install from requirements using cached packages
            cmd = [
                str(pip_path), "install",
                "-r", str(self.requirements_file),
                "--find-links", str(self.packages_cache),
                "--no-index",  # Don't use PyPI
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                # If offline install fails, download packages and cache them
                print("Downloading and caching packages...")
                download_cmd = [
                    str(pip_path), "download",
                    "-r", str(self.requirements_file),
                    "-d", str(self.packages_cache)
                ]
                subprocess.run(download_cmd, check=True)
                
                # Try installing again
                subprocess.run(cmd, check=True)
            
            return True
        except Exception as e:
            print(f"Error installing requirements: {e}")
            return False

    def setup_environment(self):
        """Setup virtual environment and install dependencies if needed"""
        current_hash = self.get_requirements_hash()
        cached_hash = self.load_cached_hash()

        # If hashes match and venv exists, dependencies are up to date
        if current_hash == cached_hash and self.venv_dir.exists():
            print("✨ Dependencies are up to date!")
            return True

        print("🔄 Setting up environment...")
        
        # Create virtual environment
        if not self.create_venv():
            return False

        # Install dependencies
        if self.install_requirements():
            self.save_hash(current_hash)
            print("✅ Dependencies installed successfully!")
            return True
            
        return False 