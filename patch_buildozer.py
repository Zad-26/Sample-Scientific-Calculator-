import buildozer
import os
import sys

path = os.path.join(
    os.path.dirname(buildozer.__file__), 'targets/android.py'
)
print(f"Patching: {path}")

with open(path, 'r') as f:
    content = f.read()

# Replace the file_exists check (which fails on symlinks)
# with os.path.exists (which follows symlinks correctly)
old = (
    "        ndk_dir = self.android_ndk_dir\n"
    "        if self.buildozer.file_exists(ndk_dir):\n"
    "            self.buildozer.info('Android NDK found at {0}'.format(ndk_dir))\n"
    "            return ndk_dir"
)
new = (
    "        ndk_dir = self.android_ndk_dir\n"
    "        if os.path.exists(ndk_dir):\n"
    "            self.buildozer.info('Android NDK found at {0}'.format(ndk_dir))\n"
    "            return ndk_dir"
)

if old in content:
    content = content.replace(old, new)
    with open(path, 'w') as f:
        f.write(content)
    print("Patch applied! file_exists -> os.path.exists")
    sys.exit(0)

print("ERROR: Could not find patch target. Showing lines 385-400:")
for i, line in enumerate(content.splitlines()):
    if 385 <= i+1 <= 405:
        print(f"  {i+1}: {repr(line)}")

sys.exit(1)
