"""One-time YouTube sign-in on YOUR computer. Puts the upload permission straight into GitHub secrets.

    python youtube_auth.py path\\to\\client_secret.json

1. Opens your browser at Google's sign-in page (choose the YouTube channel's account, approve "upload videos").
2. Receives the answer on this computer only (127.0.0.1).
3. Stores YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET and YOUTUBE_REFRESH_TOKEN as secrets of the studio repo
   with the GitHub CLI. Nothing secret is printed, saved to a file or sent anywhere else.
Requires the GitHub CLI logged in as you (SET_SECRETS.bat in the brain folder set that up).
"""
import http.server
import json
import secrets
import shutil
import subprocess
import sys
import threading
import urllib.parse
import urllib.request
import webbrowser

REPO = "FranklinMburu/Autonomous-content-studio"
SCOPE = "https://www.googleapis.com/auth/youtube.upload"
AUTH = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN = "https://oauth2.googleapis.com/token"


def main(path):
    cfg = json.load(open(path, encoding="utf-8"))
    cfg = cfg.get("installed") or cfg.get("web") or cfg
    cid, csec = cfg["client_id"], cfg["client_secret"]
    state = secrets.token_urlsafe(16)
    got = {}

    class H(http.server.BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_GET(self):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            if q.get("state", [""])[0] == state and "code" in q:
                got["code"] = q["code"][0]
                msg = "Done. You can close this tab and go back to the black window."
            else:
                msg = "Sign-in was not completed. Close this tab and run the script again."
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(msg.encode())

    srv = http.server.HTTPServer(("127.0.0.1", 0), H)
    redirect = f"http://127.0.0.1:{srv.server_address[1]}/"
    url = AUTH + "?" + urllib.parse.urlencode({"client_id": cid, "redirect_uri": redirect, "response_type": "code",
                                               "scope": SCOPE, "access_type": "offline", "prompt": "consent",
                                               "state": state})
    print("Opening your browser for Google sign-in (choose the account that owns the YouTube channel)...")
    webbrowser.open(url)
    t = threading.Thread(target=srv.handle_request)
    t.start()
    t.join(timeout=300)
    srv.server_close()
    if "code" not in got:
        print("Sign-in did not finish within 5 minutes. Run the script again.")
        return 1
    data = urllib.parse.urlencode({"code": got["code"], "client_id": cid, "client_secret": csec,
                                   "redirect_uri": redirect, "grant_type": "authorization_code"}).encode()
    with urllib.request.urlopen(urllib.request.Request(TOKEN, data=data, method="POST"), timeout=30) as r:
        tok = json.loads(r.read())
    if "refresh_token" not in tok:
        print("Google did not return a long-term permission. Remove the app's access in your Google account and retry.")
        return 1
    gh = shutil.which("gh")
    if not gh:
        print("GitHub CLI (gh) not found. Run SET_SECRETS.bat once first, then this script again.")
        return 1
    for name, value in (("YOUTUBE_CLIENT_ID", cid), ("YOUTUBE_CLIENT_SECRET", csec),
                        ("YOUTUBE_REFRESH_TOKEN", tok["refresh_token"])):
        r = subprocess.run([gh, "secret", "set", name, "--repo", REPO], input=value.encode(), capture_output=True)
        print(f"  {name:24} {'set' if r.returncode == 0 else 'FAILED'}")
    print("Done. Nothing secret was printed.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
