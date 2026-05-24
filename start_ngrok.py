import sys
import time
from pyngrok import ngrok

def main():
    token = "3EABDo79ukUCl3wW15jvWgtXrVX_66iCGTm5fEtSHpZBmA3sD"
    print("[*] Setting ngrok authtoken...")
    ngrok.set_auth_token(token)
    
    print("[*] Opening tunnel on port 8000...")
    try:
        tunnel = ngrok.connect(8000)
        print(f"\n==============================================\n")
        print(f"🚀 NGROK PUBLIC URL: {tunnel.public_url}")
        print(f"\n==============================================\n")
        sys.stdout.flush()
        
        while True:
            time.sleep(1)
    except Exception as e:
        print(f"Error starting ngrok: {e}")
        sys.stdout.flush()

if __name__ == "__main__":
    main()
