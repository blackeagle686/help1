import sys
import time
from pyngrok import ngrok
from pyngrok.exception import PyngrokNgrokError


TOKEN = "3EABDo79ukUCl3wW15jvWgtXrVX_66iCGTm5fEtSHpZBmA3sD"
PORT = 8005


def is_tunnel_already_running(port: int) -> bool:
    """
    Check if there is already an active ngrok tunnel
    for the target port on this machine.
    """
    try:
        tunnels = ngrok.get_tunnels()

        for tunnel in tunnels:
            config = getattr(tunnel, "config", {})

            # Example addr: http://localhost:8005
            addr = config.get("addr", "")

            if str(port) in str(addr):
                print(f"[!] Tunnel already running for port {port}")
                print(f"[!] Existing URL: {tunnel.public_url}")
                return True

        return False

    except Exception as e:
        print(f"[!] Could not check existing tunnels: {e}")
        return False


def main():
    print("[*] Setting ngrok authtoken...")
    ngrok.set_auth_token(TOKEN)

    # Check BEFORE creating new tunnel
    if is_tunnel_already_running(PORT):
        print("[*] Reusing existing tunnel. Exiting safely.")
        sys.exit(0)

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