import buildozer
import os
import sys

path = os.path.join(
    os.path.dirname(buildozer.__file__), 'targets/android.py'
)
print(f"Patching: {path}")

with open(path, 'r') as f:
    content = f.read()

# Simple text replacement — find the NDK download line and skip it
# This is the line that tries to download the NDK zip
old = "        url = '%s' % ndkurl"
new = (
    "        # PATCHED: skip download if NDK already exists\n"
    "        if os.path.exists(self.android_ndk_dir):\n"
    "            print('NDK already present, skipping download.')\n"
    "            return\n"
    "        url = '%s' % ndkurl"
)

if old in content:
    content = content.replace(old, new)
    with open(path, 'w') as f:
        f.write(content)
    print("Patch applied successfully!")
    sys.exit(0)

# Fallback: try a different known line
old2 = "        self.buildozer.download(url, filename)"
new2 = (
    "        # PATCHED: skip NDK download\n"
    "        if os.path.exists(self.android_ndk_dir):\n"
    "            print('NDK already present, skipping download.')\n"
    "            return\n"
    "        self.buildozer.download(url, filename)"
)

if old2 in content:
    content = content.replace(old2, new2)
    with open(path, 'w') as f:
        f.write(content)
    print("Patch applied (fallback) successfully!")
    sys.exit(0)

# Last resort: print the _install_android_ndk method so we can see it
print("ERROR: Could not find patch target. Showing NDK method contents:")
inside = False
for i, line in enumerate(content.splitlines()):
    if '_install_android_ndk' in line:
        inside = True
    if inside:
        print(f"  {i+1}: {line}")
    if inside and i > 0 and line.strip() == '' and i > 5:
        break

sys.exit(1)
