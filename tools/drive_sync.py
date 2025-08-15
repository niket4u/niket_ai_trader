
#!/usr/bin/env python3
import os, sys, glob, zipfile, datetime
from dotenv import load_dotenv
load_dotenv()

LOG_DIR = os.getenv("LOG_DIR", "/tmp/niketbot_logs")
SERVICE_JSON = os.getenv("DRIVE_SERVICE_ACCOUNT_JSON", "")
FOLDER_ID = os.getenv("DRIVE_FOLDER_ID", "")
MAX_ARCHIVES = int(os.getenv("DRIVE_MAX_ARCHIVES", "8"))

if not SERVICE_JSON or not os.path.exists(SERVICE_JSON):
    print("[!] DRIVE_SERVICE_ACCOUNT_JSON missing or not found:", SERVICE_JSON, file=sys.stderr); sys.exit(1)
if not FOLDER_ID:
    print("[!] DRIVE_FOLDER_ID is required.", file=sys.stderr); sys.exit(2)

from pydrive2.auth import ServiceAccountCredentials, GoogleAuth
from pydrive2.drive import GoogleDrive

SCOPES = ["https://www.googleapis.com/auth/drive"]
gauth = GoogleAuth(settings={
    "client_config_backend": "service",
    "service_config": { "client_json_file_path": SERVICE_JSON, "scope": SCOPES }
})
gauth.ServiceAuth()
drive = GoogleDrive(gauth)

today = datetime.datetime.utcnow().strftime("%Y%m%d")
archive_name = f"niketbot_logs_{today}.zip"
archive_path = f"/tmp/{archive_name}"

def build_zip(src_dir: str, out_path: str):
    files = glob.glob(os.path.join(src_dir, "*.log"))
    state_path = os.path.join(src_dir, "state.json")
    if os.path.exists(state_path):
        files.append(state_path)
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        for f in files:
            z.write(f, arcname=os.path.basename(f))
    return out_path

print(f"[i] Zipping from {LOG_DIR} -> {archive_path}")
build_zip(LOG_DIR, archive_path)

print(f"[i] Uploading {archive_name} to Drive folder {FOLDER_ID}")
gfile = drive.CreateFile({"title": archive_name, "parents": [{"id": FOLDER_ID}]})
gfile.SetContentFile(archive_path); gfile.Upload()
print("[+] Upload complete:", gfile["id"])

try:
    if MAX_ARCHIVES and MAX_ARCHIVES > 0:
        file_list = drive.ListFile({
            "q": f"'{FOLDER_ID}' in parents and trashed=false and title contains 'niketbot_logs_'",
            "maxResults": 1000
        }).GetList()
        file_list.sort(key=lambda f: f.get("createdDate",""))
        if len(file_list) > MAX_ARCHIVES:
            for f in file_list[0:len(file_list)-MAX_ARCHIVES]:
                f.Delete()
except Exception as e:
    print("[!] Prune failed:", e, file=sys.stderr)
print("[✓] Drive sync finished.")
