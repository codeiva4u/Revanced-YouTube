import subprocess
import re
import sys
import os
import json

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

def get_latest_version(app_name):
    if app_name == "twitter":
        url = "https://www.apkmirror.com/apk/x-corp/x/"
        pattern = r'href="(/apk/x-corp/x/x-([0-9\.-]+)-release/)"'
        default_ver = "12.7.1-release.0"
    elif app_name == "instagram":
        url = "https://www.apkmirror.com/apk/instagram/instagram/"
        pattern = r'href="(/apk/instagram/instagram/instagram-([0-9\.-]+)-release/)"'
        default_ver = "435.0.0.37.76"
    else:
        return ""

    html = get_html_curl(url)
    matches = re.findall(pattern, html)
    
    stable_matches = []
    for link, ver in matches:
        if 'alpha' not in link.lower() and 'beta' not in link.lower():
            ver_clean = ver.rstrip('-').replace('-', '.') if not app_name == 'twitter' else ver
            stable_matches.append(ver_clean)
            
    if stable_matches:
        return stable_matches[0]
        
    return default_ver

def download_app_via_apkmd(app_name, version, out_path):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    org = "x-corp" if app_name == "twitter" else "instagram"
    repo = "x" if app_name == "twitter" else "instagram"
    
    config = {
        "options": {
            "arch": "universal" if app_name == "twitter" else "arm64-v8a",
            "dpi": "nodpi",
            "outDir": os.path.dirname(out_path)
        },
        "apps": [
            {
                "org": org,
                "repo": repo,
                "type": "apk",
                "outFile": os.path.basename(out_path).replace('.apk', '')
            }
        ]
    }
    
    if version:
        config["apps"][0]["version"] = version
        
    config_file = f"apkmd-{app_name}.json"
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)
        
    try:
        print(f"Downloading latest {app_name} stock APK via apkmd...")
        subprocess.check_call(["build_tools/apkmd", config_file])
        if os.path.exists(out_path) and os.path.getsize(out_path) > 10000000:
            print(f"Successfully downloaded {app_name} stock APK ({os.path.getsize(out_path)} bytes)")
            return True
    except Exception as e:
        print(f"apkmd download error for {app_name}: {e}", file=sys.stderr)
        
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
        ver = get_latest_version("twitter")
        print(ver)
        return

    if action == "instagram_version":
        ver = get_latest_version("instagram")
        print(ver)
        return

    if action == "download_twitter":
        ver = get_latest_version("twitter")
        dest = "stock/twitter-stock.apk"
        if not download_app_via_apkmd("twitter", ver, dest):
            # Fallback download
            fallback_url = "https://github.com/crimera/twitter-apk/releases/download/12.7.1-release.0/twitter-piko-v12.7.1-release.0.apk"
            print("Downloading Twitter stock APK from fallback mirror...")
            subprocess.check_call(["curl", "-s", "-L", "-o", dest, fallback_url])
        return

    if action == "download_instagram":
        ver = get_latest_version("instagram")
        dest = "stock/instagram-stock.apk"
        if not download_app_via_apkmd("instagram", ver, dest):
            # Fallback download
            fallback_url = "https://github.com/krvstek/uni-apks/releases/download/26.07.24-piko/instagram-piko-v435.0.0.37.76-arm64-v8a.apk"
            print("Downloading Instagram stock APK from fallback mirror...")
            subprocess.check_call(["curl", "-s", "-L", "-o", dest, fallback_url])
        return

if __name__ == "__main__":
    main()
