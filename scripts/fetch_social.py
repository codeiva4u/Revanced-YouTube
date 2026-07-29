import urllib.request
import re
import sys
import os
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

# Tested stable target versions for Piko patches
TWITTER_VERSION = "12.7.1-release.0"
INSTAGRAM_VERSION = "435.0.0.37.76"

def get_html(url):
    req = urllib.request.Request(url, headers=headers)
    return urllib.request.urlopen(req).read().decode('utf-8')

def download_file(url, dest_path):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        content = resp.read()
        if len(content) > 5000000:
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            with open(dest_path, "wb") as f:
                f.write(content)
            print(f"Successfully downloaded {len(content)} bytes to {dest_path}")
            return True
    return False

def main():
    action = sys.argv[1] if len(sys.argv) > 1 else "help"
    
    if action == "piko_tag":
        try:
            req = urllib.request.Request("https://api.github.com/repos/crimera/piko/releases/latest", headers={'User-Agent': 'Mozilla/5.0'})
            data = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
            print(data.get("tag_name", "v3.8.0"))
        except Exception:
            print("v3.8.0")
        return

    if action == "piko_mpp_url":
        try:
            req = urllib.request.Request("https://api.github.com/repos/crimera/piko/releases/latest", headers={'User-Agent': 'Mozilla/5.0'})
            data = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
            mpp = [a['browser_download_url'] for a in data.get("assets", []) if a['name'].endswith('.mpp')]
            if mpp:
                print(mpp[0])
                return
            tag = data.get("tag_name", "v3.8.0")
            print(f"https://github.com/crimera/piko/releases/download/{tag}/patches-{tag.replace('v','')}.mpp")
        except Exception:
            print("https://github.com/crimera/piko/releases/download/v3.8.0/patches-3.8.0.mpp")
        return

    if action == "twitter_version":
        print(TWITTER_VERSION)
        return

    if action == "instagram_version":
        print(INSTAGRAM_VERSION)
        return

    if action == "download_twitter":
        os.makedirs("stock", exist_ok=True)
        dest = "stock/twitter-stock.apk"
        
        # Primary Archive Mirror
        url1 = f"https://archive.org/download/jhc-apks/apks/com.twitter.android/com.twitter.android-{TWITTER_VERSION}-arm64-v8a.apk"
        print(f"Downloading Twitter stock APK ({TWITTER_VERSION}) from primary mirror...")
        try:
            if download_file(url1, dest):
                return
        except Exception as e:
            print(f"Primary download warning: {e}", file=sys.stderr)

        # Secondary Github Release Fallback
        url2 = "https://github.com/AbsoluteNeutral/x-revanced-built/releases/download/12.7.1-release.0/twitter-stock.apk"
        print("Downloading Twitter stock APK from fallback mirror...")
        try:
            if download_file(url2, dest):
                return
        except Exception as e:
            print(f"Fallback download error: {e}", file=sys.stderr)
            sys.exit(1)

    if action == "download_instagram":
        os.makedirs("stock", exist_ok=True)
        dest = "stock/instagram-stock.apk"
        
        # Primary Archive Mirror
        url1 = f"https://archive.org/download/jhc-apks/apks/com.instagram.android/com.instagram.android-{INSTAGRAM_VERSION}-arm64-v8a.apk"
        print(f"Downloading Instagram stock APK ({INSTAGRAM_VERSION}) from primary mirror...")
        try:
            if download_file(url1, dest):
                return
        except Exception as e:
            print(f"Primary download warning: {e}", file=sys.stderr)

        # Secondary Github Release Fallback
        url2 = "https://github.com/krvstek/uni-apks/releases/download/instagram-stock/instagram-stock.apk"
        print("Downloading Instagram stock APK from fallback mirror...")
        try:
            if download_file(url2, dest):
                return
        except Exception as e:
            print(f"Fallback download error: {e}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main()
