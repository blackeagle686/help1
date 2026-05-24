import os
import sys
import time
import signal
import subprocess
from pyngrok import ngrok
from pyngrok.exception import PyngrokNgrokError

TOKEN = "3EABDo79ukUCl3wW15jvWgtXrVX_66iCGTm5fEtSHpZBmA3sD"
PORT = 8005

def cleanup_existing_tunnels():
    """
    Check if there are any active tunnels locally and disconnect them,
    then kill any existing ngrok system processes to avoid auth and port conflicts.
    """
    print("[*] Checking for and cleaning up existing ngrok tunnels/processes...")
    
    # 1. Kill ngrok PID from saved file if exists
    try:
        if os.path.exists(".ngrok.pid"):
            with open(".ngrok.pid", "r") as f:
                old_pid = int(f.read().strip())
            print(f"[!] Found old ngrok PID {old_pid} in .ngrok.pid. Terminating it...")
            os.kill(old_pid, signal.SIGKILL)
            time.sleep(1)
            # Remove file
            try:
                os.remove(".ngrok.pid")
            except Exception:
                pass
    except Exception as e:
        print(f"[*] Could not kill process from .ngrok.pid: {e}")

    # 2. Check local ngrok API for active tunnels
    try:
        tunnels = ngrok.get_tunnels()
        for tunnel in tunnels:
            print(f"[!] Disconnecting existing tunnel: {tunnel.public_url}")
            ngrok.disconnect(tunnel.public_url)
    except Exception as e:
        print(f"[*] No active local tunnels detected via API: {e}")

    # 3. Fallback: kill any other ngrok processes
    try:
        print("[*] Killing existing ngrok system processes...")
        # Terminate any running ngrok binary process to release the token session
        subprocess.run(["pkill", "-x", "ngrok"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1.5) # Give it a moment to release ports/connections
        print("[✔] Cleanup complete.")
    except Exception as e:
        print(f"[*] Error while killing ngrok processes: {e}")

def main():
    # Clean up before setting token and connecting
    cleanup_existing_tunnels()

    print("[*] Setting ngrok authtoken...")
    ngrok.set_auth_token(TOKEN)

    print(f"[*] Opening tunnel on port {PORT}...")
    try:
        tunnel = ngrok.connect(PORT)
        print("\n==============================================\n")
        print(f"🚀 NGROK PUBLIC URL: {tunnel.public_url}")
        print("\n==============================================\n")
        
        # Get the underlying ngrok process PID and write it to a file
        try:
            ngrok_process = ngrok.get_ngrok_process()
            ngrok_pid = ngrok_process.proc.pid
            with open(".ngrok.pid", "w") as f:
                f.write(str(ngrok_pid))
            print(f"[*] Saved ngrok PID {ngrok_pid} to .ngrok.pid")
        except Exception as pe:
            print(f"[!] Could not save ngrok PID: {pe}")
            
        sys.stdout.flush()

        while True:
            time.sleep(1)

    except PyngrokNgrokError as e:
        print(f"[!] Ngrok error: {e}")
        sys.stdout.flush()
    except Exception as e:
        print(f"[!] Unexpected error: {e}")
        sys.stdout.flush()

if __name__ == "__main__":
    main()