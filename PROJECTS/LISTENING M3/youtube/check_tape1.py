import sys
sys.path.insert(0, "PROJECTS/LISTENING M3")
import upload_to_youtube as u

svc = u.get_authenticated_service(["https://www.googleapis.com/auth/youtube.readonly"])
vid = "PAC65Ewnrdk"

# caption tracks
cap = svc.captions().list(part="snippet", videoId=vid).execute()
items = cap.get("items", [])
print("caption tracks:", len(items))
for it in items:
    s = it["snippet"]
    print(" -", s["language"], s["trackKind"], "| name:", s.get("name"), "| status:", s.get("status"))

# video status + snippet
v = svc.videos().list(part="status,snippet", id=vid).execute()
it = v["items"][0]
print("title:", it["snippet"]["title"])
print("uploadStatus:", it["status"]["uploadStatus"])
print("privacy:", it["status"]["privacyStatus"])
