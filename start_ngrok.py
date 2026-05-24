import os
import sys
import time
import signal
from pyngrok import ngrok
from pyngrok.exception import PyngrokNgrokError

TOKEN = "3EABDo79ukUCl3wW15jvWgtXrVX_66iCGTm5fEtSHpZBmA3sD"
PORT = 8005

def cleanup_existing_tunnels():
    """
    Check if there is an active tunnel for our specific port (8005) and disconnect it,
    and kill our previously saved ngrok PID to avoid interrupting other ngrok sessions.
    """
    print("[*] Checking for and cleaning up this project's ngrok tunnel/process...")
    
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

    # 2. Check local ngrok API for active tunnels on our target port and disconnect them
    try:
        tunnels = ngrok.get_tunnels()
        for tunnel in tunnels:
            config = getattr(tunnel, "config", {})
            addr = config.get("addr", "")
            if str(PORT) in str(addr):
                print(f"[!] Disconnecting our active tunnel: {tunnel.public_url} (addr: {addr})")
                ngrok.disconnect(tunnel.public_url)
    except Exception as e:
        print(f"[*] No active tunnels on port {PORT} detected: {e}")

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