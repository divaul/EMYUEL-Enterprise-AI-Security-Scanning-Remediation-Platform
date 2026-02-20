"""Insert _exiftool_cmd helper into tool_executor.py"""
import re

FUNC = '''
def _exiftool_cmd(target, domain, temp_dir, is_url_target, is_path_target):
    """
    Build exiftool command for EXIF metadata/geolocation leak detection.

    - Path target: exiftool -recurse on local dir/file
    - URL target : download images found on the page -> scan with exiftool
    Returns (cmd_list, timeout, stdin_data) or None
    """
    if is_path_target:
        return (
            ['exiftool', '-recurse', '-json',
             '-GPS:All', '-Make', '-Model', '-Software',
             '-Artist', '-Copyright', '-Comment', target],
            120, None
        )

    if is_url_target:
        img_dir = os.path.join(temp_dir, f'exif_imgs_{domain}')
        os.makedirs(img_dir, exist_ok=True)

        # Write a small Python helper that downloads page images and runs exiftool
        script_lines = [
            "import urllib.request, re, os, subprocess, sys",
            f"img_dir = {repr(img_dir)}",
            "os.makedirs(img_dir, exist_ok=True)",
            "try:",
            f"    html = urllib.request.urlopen({repr(target)}, timeout=15).read().decode('utf-8','replace')",
            "except Exception as e:",
            "    print(f'Could not fetch: {e}'); sys.exit(1)",
            "pat = re.compile(r'[^\\'\"\\s><]+\\.(?:jpg|jpeg|png|gif|webp|bmp|tiff)', re.I)",
            "imgs = list(set(pat.findall(html)))[:25]",
            "saved = []",
            "for i, img in enumerate(imgs):",
            f"    base = {repr(target.rstrip('/'))}",
            "    url = img if img.startswith('http') else base + '/' + img.lstrip('/')",
            "    bn = os.path.basename(img.split('?')[0]) or f'img{i}.jpg'",
            "    dest = os.path.join(img_dir, bn)",
            "    try: urllib.request.urlretrieve(url, dest); saved.append(dest)",
            "    except: pass",
            "print(f'[ExifTool] Downloaded {len(saved)}/{len(imgs)} images')",
            "if not saved: print('[ExifTool] No images downloaded'); sys.exit(0)",
            "r = subprocess.run(",
            "    ['exiftool', '-recurse', '-json',",
            "     '-GPS:GPSLatitude', '-GPS:GPSLongitude',",
            "     '-GPS:GPSLatitudeRef', '-GPS:GPSLongitudeRef',",
            "     '-Make', '-Model', '-Software', img_dir],",
            "    capture_output=True, text=True)",
            "out = r.stdout.strip() or r.stderr.strip()",
            "print(out if out else '[ExifTool] No EXIF metadata found in images')",
        ]
        script_src = "\n".join(script_lines)

        script_path = os.path.join(temp_dir, f'exif_scan_{domain}.py')
        try:
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_src)
        except Exception:
            return None
        return (['python', script_path], 90, None)

    return None

'''

with open('gui/tool_executor.py', 'r', encoding='utf-8') as f:
    src = f.read()

# Insert after _shuffledns_cmd definition block, before Pipeline Chains comment
MARKER = '\n# \u2500\u2500\u2500 Pipeline Chains'
if MARKER in src and '_exiftool_cmd' not in src:
    src = src.replace(MARKER, FUNC + MARKER)
    with open('gui/tool_executor.py', 'w', encoding='utf-8') as f:
        f.write(src)
    print("SUCCESS: inserted _exiftool_cmd")
elif '_exiftool_cmd' in src:
    print("ALREADY EXISTS: _exiftool_cmd already in file")
else:
    print("ERROR: marker not found")
    print("Looking for:", repr(MARKER[:40]))
    idx = src.find('Pipeline Chains')
    print("Pipeline Chains at char:", idx)
    print("Context:", repr(src[idx-5:idx+30]))
