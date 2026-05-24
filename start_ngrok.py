import sys
import time
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
    try:
        tunnels = ngrok.get_tunnels()
        for tunnel in tunnels:
            print(f"[!] Disconnecting existing tunnel: {tunnel.public_url}")
            ngrok.disconnect(tunnel.public_url)
    except Exception as e:
        print(f"[*] No active local tunnels detected via API: {e}")

    try:
        print("[*] Killing existing ngrok system processes...")
        # Terminate any running ngrok binary process to release the token session
        # We use -x to match the exact binary name 'ngrok' and avoid killing this python script (start_ngrok.py)
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