import urllib.request
import re
import sys
import os

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

def get_html(url):
    req = urllib.request.Request(url, headers=headers)
    return urllib.request.urlopen(req).read().decode('utf-8')

def main():
    action = sys.argv[1] if len(sys.argv) > 1 else "version"
    
    try:
        app_html = get_html("https://www.apkmirror.com/apk/google-inc/photos/")
        release_links = re.findall(r'href="(/apk/google-inc/photos/google-photos-[^"]+-release/)"', app_html)
        if not release_links:
            sys.exit(1)
            
        stable_links = [l for l in release_links if 'beta' not in l.lower()]
        target_link = stable_links[0] if stable_links else release_links[0]
        
        ver_match = re.search(r'google-photos-([0-9-]+)-release', target_link)
        version_str = ver_match.group(1).replace('-', '.') if ver_match else "7.85.0.952162352"
        
        if action == "version":
            print(version_str)
            return

        latest_release_url = "https://www.apkmirror.com" + target_link
        rel_html = get_html(latest_release_url)
        variant_links = re.findall(r'href="(/apk/google-inc/photos/google-photos-[^"]+-android-apk-download/)"', rel_html)
        if not variant_links:
            sys.exit(1)
            
        variant_url = "https://www.apkmirror.com" + variant_links[0]
        var_html = get_html(variant_url)
        dl_page_links = re.findall(r'href="(/apk/google-inc/photos/google-photos-[^"]+-android-apk-download/download/\?[^"]+)"', var_html)
        if not dl_page_links:
            sys.exit(1)
            
        dl_page_url = "https://www.apkmirror.com" + dl_page_links[0]
        dl_html = get_html(dl_page_url)
        real_dl_links = re.findall(r'href="(/wp-content/themes/APKMirror/download\.php\?[^"]+)"', dl_html)
        if not real_dl_links:
            sys.exit(1)
            
        final_url = "https://www.apkmirror.com" + real_dl_links[0].replace("&amp;", "&")
        
        req_file = urllib.request.Request(final_url, headers=headers)
        with urllib.request.urlopen(req_file) as resp:
            content = resp.read()
            if len(content) > 10000000:
                os.makedirs("stock", exist_ok=True)
                with open("stock/gphotos-stock.apk", "wb") as f:
                    f.write(content)
                print(f"Downloaded {len(content)} bytes for version {version_str}")
            else:
                sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
