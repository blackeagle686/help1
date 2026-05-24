import os
import sys
import time
import signal
import json
import subprocess
import urllib.request
import urllib.error
from pyngrok import ngrok
from pyngrok.exception import PyngrokNgrokError

TOKEN = "3EABDo79ukUCl3wW15jvWgtXrVX_66iCGTm5fEtSHpZBmA3sD"
PORT = 8005
PID_FILE = ".ngrok.pid"
NGROK_API_PORTS = [4040, 4041, 4042, 4043]


def _kill_pid(pid):
    """Terminate a specific process by PID."""
    try:
        os.kill(pid, signal.SIGTERM)
        time.sleep(1)
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    except ProcessLookupError:
        pass
    except Exception as e:
        print(f"[*] Could not kill PID {pid}: {e}")


def _kill_saved_pid():
    """Kill the ngrok process from our saved PID file."""
    if not os.path.exists(PID_FILE):
        return
    try:
        with open(PID_FILE, "r") as f:
            old_pid = int(f.read().strip())
        print(f"[!] Found saved ngrok PID {old_pid}. Terminating...")
        _kill_pid(old_pid)
        print(f"[✔] Killed PID {old_pid}")
    except Exception as e:
        print(f"[*] Could not kill saved PID: {e}")
    finally:
        try:
            os.remove(PID_FILE)
        except Exception:
            pass


def _find_and_kill_orphaned_ngrok():
    """
    Scan local ngrok API ports (4040-4043) to find an orphaned ngrok process
    that has a tunnel for our port (8005). Disconnect the tunnel and kill
    ONLY that specific ngrok process. Does NOT touch other ngrok instances.
    """
    for api_port in NGROK_API_PORTS:
        try:
            url = f"http://127.0.0.1:{api_port}/api/tunnels"
            req = urllib.request.urlopen(url, timeout=2)
            data = json.loads(req.read())

            our_tunnel_found = False
            for tunnel in data.get("tunnels", []):
                addr = tunnel.get("config", {}).get("addr", "")
                if str(PORT) in str(addr):
                    our_tunnel_found = True
                    name = tunnel.get("name", "")
                    public_url = tunnel.get("public_url", "")
                    print(f"[!] Found orphaned tunnel on API :{api_port} → {public_url}")
                    # Disconnect it via the local API
                    try:
                        del_req = urllib.request.Request(
                            f"http://127.0.0.1:{api_port}/api/tunnels/{name}",
                            method="DELETE"
                        )
                        urllib.request.urlopen(del_req, timeout=2)
                        print(f"[✔] Disconnected tunnel '{name}'")
                    except Exception:
                        pass

            if our_tunnel_found:
                # Kill the ngrok process serving this API port
                try:
                    result = subprocess.run(
                        ["fuser", f"{api_port}/tcp"],
                        capture_output=True, text=True, timeout=5
                    )
                    pids = result.stdout.strip().split()
                    for p in pids:
                        pid = int(p)
                        print(f"[!] Killing orphaned ngrok process (PID {pid})")
                        _kill_pid(pid)
                except Exception:
                    # Fallback: try lsof
                    try:
                        result = subprocess.run(
                            ["lsof", "-t", f"-i:{api_port}"],
                            capture_output=True, text=True, timeout=5
                        )
                        for line in result.stdout.strip().split('\n'):
                            if line.strip():
                                pid = int(line.strip())
                                print(f"[!] Killing orphaned ngrok process (PID {pid})")
                                _kill_pid(pid)
                    except Exception:
                        pass
                break  # We found and handled our tunnel, stop scanning

        except (urllib.error.URLError, ConnectionRefusedError, OSError):
            continue  # No ngrok API on this port, try next


def cleanup_existing_tunnels():
    """
    Kill only this project's ngrok tunnel/process.
    Does NOT affect other ngrok tunnels running on this machine.
    """
    print("[*] Cleaning up this project's ngrok tunnel...")
    _kill_saved_pid()
    _find_and_kill_orphaned_ngrok()
    time.sleep(1)
    print("[✔] Cleanup complete.")


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

        # Save the ngrok process PID for future cleanup
        try:
            ngrok_process = ngrok.get_ngrok_process()
            ngrok_pid = ngrok_process.proc.pid
            with open(PID_FILE, "w") as f:
                f.write(str(ngrok_pid))
            print(f"[*] Saved ngrok PID {ngrok_pid} to {PID_FILE}")
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