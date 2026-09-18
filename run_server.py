import sys
import os
import time
import webbrowser
import threading
import multiprocessing
import uvicorn

# Adjust path for PyInstaller frozen execution mode
if getattr(sys, 'frozen', False):
    bundle_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    os.chdir(bundle_dir)
    if bundle_dir not in sys.path:
        sys.path.insert(0, bundle_dir)

from app.main import app


def open_browser(url: str):
    time.sleep(1.5)
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"Could not open browser automatically: {e}")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    
    host = "127.0.0.1"
    port = 8000
    url = f"http://{host}:{port}"
    
    print("=" * 60)
    print("  PIIUA - Ukrainian PII Pseudonymization & Restoration Service")
    print(f"  Running on: {url}")
    print("  Press Ctrl+C to stop the server.")
    print("=" * 60)
    
    # Auto open browser in background thread
    threading.Thread(target=open_browser, args=(url,), daemon=True).start()
    
    # Run uvicorn server
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        access_log=True,
    )
