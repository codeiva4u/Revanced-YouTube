import sys
import glob
import zipfile
import os

def patch_microg():
    apks = glob.glob("MicroG-RE-*.apk")
    if not apks:
        print("No MicroG-RE APK found to patch.")
        return

    apk_path = apks[0]
    print(f"Patching targetSdkVersion in {apk_path} ...")

    with zipfile.ZipFile(apk_path, 'r') as zin:
        manifest = bytearray(zin.read('AndroidManifest.xml'))
        attr_id = b'\x70\x02\x01\x01'
        idx = manifest.find(attr_id)
        if idx != -1:
            val_idx = manifest.find(b'\x17\x00\x00\x00', idx)
            if val_idx != -1:
                manifest[val_idx] = 0x21  # Change 23 (Android 6.0) to 33 (Android 13)
                temp_path = 'patched_' + apk_path
                with zipfile.ZipFile(temp_path, 'w', zipfile.ZIP_DEFLATED) as zout:
                    for item in zin.infolist():
                        data = manifest if item.filename == 'AndroidManifest.xml' else zin.read(item.filename)
                        zout.writestr(item, data)
                os.replace(temp_path, apk_path)
                print(f"Successfully updated targetSdkVersion to 33 in {apk_path}")

if __name__ == '__main__':
    patch_microg()
