import subprocess
import re
import sys
import os
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

TWITTER_VERSION = "12.7.1-release.0"

def get_html_curl(url):
    cmd = [
        "curl", "-s", "-L",
        "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "-H", "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "-H", "Accept-Language: en-US,en;q=0.9",
        url
    ]
    try:
        return subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode('utf-8', errors='ignore')
    except Exception:
        return ""

def get_feurstagram_info():
    try:
        req = urllib.request.Request("https://api.github.com/repos/jean-voila/FeurStagram/releases/latest", headers={'User-Agent': 'Mozilla/5.0'})
        data = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
        tag = data.get("tag_name", "v437-0-0-33-78")
        version = tag.lstrip('v').replace('-', '.')
        apk_url = ""
        for asset in data.get("assets", []):
            if asset['name'].endswith('.apk') and 'clone' not in asset['name']:
                apk_url = asset['browser_download_url']
                break
        if not apk_url and data.get("assets"):
            apk_url = data["assets"][0]['browser_download_url']
        return version, apk_url, tag
    except Exception as e:
        print(f"FeurStagram API warning: {e}", file=sys.stderr)
        return "437.0.0.33.78", "https://github.com/jean-voila/FeurStagram/releases/download/v437-0-0-33-78/feurstagram-437-0-0-33-78.apk", "v437-0-0-33-78"

def download_file(url, dest_path):
    print(f"Downloading from {url} ...")
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        content = resp.read()
        print(f"Downloaded size: {len(content)} bytes")
        if len(content) > 5000000:
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            with open(dest_path, "wb") as f:
                f.write(content)
            print(f"Successfully saved to {dest_path}")
            return True
    return False

def main():
    action = sys.argv[1] if len(sys.argv) > 1 else "help"
    
    if action == "piko_tag":
        try:
            cmd = ["gh", "api", "repos/crimera/piko/releases/latest", "--jq", ".tag_name"]
            tag = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode('utf-8').strip()
            print(tag if tag else "v3.8.0")
        except Exception:
            print("v3.8.0")
        return

    if action == "piko_mpp_url":
        try:
            cmd = ["gh", "api", "repos/crimera/piko/releases/latest", "--jq", ".assets[] | select(.name | endswith(\".mpp\")) | .browser_download_url"]
            url = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode('utf-8').strip()
            if url:
                print(url.splitlines()[0])
                return
            tag = subprocess.check_output(["gh", "api", "repos/crimera/piko/releases/latest", "--jq", ".tag_name"]).decode('utf-8').strip()
            print(f"https://github.com/crimera/piko/releases/download/{tag}/patches-{tag.replace('v','')}.mpp")
        except Exception:
            print("https://github.com/crimera/piko/releases/download/v3.8.0/patches-3.8.0.mpp")
        return

    if action == "twitter_version":
        print(TWITTER_VERSION)
        return

    if action == "instagram_version":
        ver, _, _ = get_feurstagram_info()
        print(ver)
        return

    if action == "download_twitter":
        os.makedirs("stock", exist_ok=True)
        dest = "stock/twitter-stock.apk"
        
        urls = [
            "https://github.com/crimera/twitter-apk/releases/download/12.7.1-release.0/twitter-piko-v12.7.1-release.0.apk",
            "https://github.com/krvstek/uni-apks/releases/download/26.07.24-piko/twitter-piko-v12.7.1-release.0-all.apk",
            f"https://archive.org/download/jhc-apks/apks/com.twitter.android/com.twitter.android-{TWITTER_VERSION}-arm64-v8a.apk"
        ]
        
        for url in urls:
            try:
                if download_file(url, dest):
                    return
            except Exception as e:
                print(f"Mirror warning ({url}): {e}", file=sys.stderr)
        sys.exit(1)

    if action == "download_instagram":
        os.makedirs("stock", exist_ok=True)
        dest = "stock/instagram-stock.apk"
        
        version, url, tag = get_feurstagram_info()
        print(f"Downloading FeurStagram ({version}) from {url}...")
        try:
            if download_file(url, dest):
                return
        except Exception as e:
            print(f"FeurStagram primary download warning: {e}", file=sys.stderr)

        fallback_url = "https://github.com/jean-voila/FeurStagram/releases/download/v437-0-0-33-78/feurstagram-437-0-0-33-78.apk"
        try:
            if download_file(fallback_url, dest):
                return
        except Exception as e:
            print(f"FeurStagram fallback download error: {e}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main()
