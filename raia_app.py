import os
import sys
import webbrowser
import threading
import time
import subprocess
from pathlib import Path
import socket

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def check_files():
    """Check if all required files exist"""
    print("\n=== File Check ===")
    required_files = [
        "main.py",
        "config.py", 
        "services/intelligent_analyzer.py",
        "services/document_processor.py",
        "services/compliance_checker.py",
        "services/report_generator.py",
        "models/schemas.py",
        "static/index.html"
    ]
    
    all_found = True
    for file_path in required_files:
        full_path = get_resource_path(file_path)
        exists = os.path.exists(full_path)
        status = "[OK]" if exists else "[MISSING]"
        print(f"{status} {file_path}")
        if not exists:
            all_found = False
    
    return all_found

def test_imports():
    """Test if we can import required modules"""
    print("\n=== Import Test ===")
    try:
        # Add the bundle path to Python path
        bundle_path = get_resource_path(".")
        if bundle_path not in sys.path:
            sys.path.insert(0, bundle_path)
        
        # Test critical imports
        import uvicorn
        print("[OK] uvicorn imported successfully")
        
        import fastapi
        print("[OK] fastapi imported successfully")
        
        # Try to import our modules
        sys.path.insert(0, get_resource_path("services"))
        sys.path.insert(0, get_resource_path("models"))
        
        import config
        print("[OK] config imported successfully")
        
        return True
    except Exception as e:
        print(f"[ERROR] Import failed: {e}")
        return False

def is_port_available(port):
    """Check if a port is available"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return True
        except OSError:
            return False

def start_server_simple(port=8010):
    """Start the FastAPI server - simplified version"""
    print(f"\n=== Starting Server on Port {port} ===")
    
    # Get the path to main.py
    main_path = get_resource_path("main.py")
    
    if not os.path.exists(main_path):
        print(f"ERROR: main.py not found at {main_path}")
        return None, port
    
    # Set environment variables for proper encoding
    env = os.environ.copy()
    env['PYTHONPATH'] = get_resource_path(".")
    env['PYTHONIOENCODING'] = 'utf-8'
    env['PYTHONUNBUFFERED'] = '1'
    
    # Use uvicorn directly instead of subprocess to avoid encoding issues
    try:
        # Import uvicorn and run in the same process
        import uvicorn
        import threading
        
        # Change to the correct directory
        original_cwd = os.getcwd()
        os.chdir(get_resource_path("."))
        
        # Import the main app
        sys.path.insert(0, get_resource_path("."))
        import main
        
        # Start uvicorn in a separate thread
        def run_server():
            try:
                uvicorn.run(
                    main.app,
                    host="0.0.0.0",
                    port=port,
                    log_level="error",  # Reduce log output to avoid encoding issues
                    access_log=False
                )
            except Exception as e:
                print(f"Server thread error: {e}")
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Restore original directory
        os.chdir(original_cwd)
        
        return server_thread, port
        
    except Exception as e:
        print(f"Failed to start server: {e}")
        return None, port

def wait_for_server(port=8010, timeout=30):
    """Wait for server to be ready"""
    try:
        import requests
        start_time = time.time()
        url = f"http://localhost:{port}"
        
        print(f"Waiting for server at {url}...")
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{url}/health", timeout=2)
                if response.status_code == 200:
                    print("Server is ready!")
                    return True
            except:
                pass
            time.sleep(2)
        
        print("Server failed to start within timeout")
        return False
    except ImportError:
        print("WARNING: requests module not available, assuming server is ready")
        time.sleep(5)  # Give server time to start
        return True

def main():
    try:
        # Set console encoding for Windows
        if os.name == 'nt':
            try:
                import locale
                locale.setlocale(locale.LC_ALL, 'C')
            except:
                pass
        
        print("RAIA - Rewards AI Assistant")
        print("=" * 40)
        print(f"Python executable: {sys.executable}")
        print(f"PyInstaller bundle: {hasattr(sys, '_MEIPASS')}")
        
        # Check if all files exist
        if not check_files():
            print("ERROR: Some required files are missing!")
            input("Press Enter to exit...")
            return
        
        # Test imports
        if not test_imports():
            print("ERROR: Failed to import required modules!")
            input("Press Enter to exit...")
            return
        
        # Check port availability
        port = 8010
        if not is_port_available(port):
            print(f"WARNING: Port {port} is already in use")
            for test_port in range(8011, 8020):
                if is_port_available(test_port):
                    port = test_port
                    print(f"Using alternative port: {port}")
                    break
            else:
                print("ERROR: No available ports found")
                input("Press Enter to exit...")
                return
        
        print(f"Using port: {port}")
        
        # Start the server
        server_thread, actual_port = start_server_simple(port)
        if not server_thread:
            print("ERROR: Failed to start server")
            input("Press Enter to exit...")
            return
        
        # Wait for server to be ready
        if wait_for_server(actual_port):
            print(f"\nRAIA is running at http://localhost:{actual_port}")
            print("Opening browser...")
            
            try:
                webbrowser.open(f"http://localhost:{actual_port}")
            except Exception as e:
                print(f"Could not open browser automatically: {e}")
                print(f"Please open http://localhost:{actual_port} manually")
            
            print("\nRAIA is now running!")
            print("Close this window to stop the application.")
            print("=" * 40)
            
            try:
                # Keep the main thread alive
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nShutting down RAIA...")
        else:
            print("ERROR: Server failed to start properly")
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()