import urllib.request
import re
import sys
import os

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

# 7.68.0.884121604 is the last tested standalone non-split APK version compatible with De-Vanced patches
STABLE_VERSION = "7.68.0.884121604"

def get_html(url):
    req = urllib.request.Request(url, headers=headers)
    return urllib.request.urlopen(req).read().decode('utf-8')

def main():
    action = sys.argv[1] if len(sys.argv) > 1 else "version"
    
    if action == "version":
        print(STABLE_VERSION)
        return

    try:
        os.makedirs("stock", exist_ok=True)
        dest_file = "stock/gphotos-stock.apk"
        
        # Primary source: Archive mirror of original standalone stock APK
        primary_url = f"https://archive.org/download/jhc-apks/apks/com.google.android.apps.photos/com.google.android.apps.photos-{STABLE_VERSION}-arm64-v8a.apk"
        print(f"Downloading Google Photos {STABLE_VERSION} standalone stock APK...")
        
        req_file = urllib.request.Request(primary_url, headers=headers)
        with urllib.request.urlopen(req_file) as resp:
            content = resp.read()
            if len(content) > 10000000:
                with open(dest_file, "wb") as f:
                    f.write(content)
                print(f"Successfully downloaded {len(content)} bytes from primary mirror!")
                return

    except Exception as e:
        print(f"Primary mirror download warning: {e}", file=sys.stderr)

    try:
        # Fallback source: GitHub release fallback of original standalone stock APK
        fallback_url = "https://github.com/mentalblank/GPhotos-Revanced/releases/download/39/googlephotos-de-vanced-v7.68.0.884121604-arm64-v8a.apk"
        print("Downloading from fallback stock mirror...")
        req_file = urllib.request.Request(fallback_url, headers=headers)
        with urllib.request.urlopen(req_file) as resp:
            content = resp.read()
            if len(content) > 10000000:
                with open(dest_file, "wb") as f:
                    f.write(content)
                print(f"Successfully downloaded {len(content)} bytes from fallback mirror!")
                return
    except Exception as e:
        print(f"Fallback download error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
