"""
Patches Buildozer's android.py to completely replace
_install_android_ndk so it never downloads anything.
"""
import buildozer
import os
import sys
import ast

path = os.path.join(
    os.path.dirname(buildozer.__file__),
    'targets/android.py'
)
print(f"Target file: {path}")

with open(path, 'r') as f:
    lines = f.readlines()

# Find the start and end of _install_android_ndk method
start_idx = None
end_idx = None
method_indent = None

for i, line in enumerate(lines):
    if 'def _install_android_ndk(self)' in line:
        start_idx = i
        method_indent = len(line) - len(line.lstrip())
        print(f"Found method at line {i+1}, indent={method_indent}")
        continue

    if start_idx is not None and end_idx is None:
        stripped = line.strip()
        if stripped == '':
            continue
        current_indent = len(line) - len(line.lstrip())
        # Method ends when we hit a new def/class at same or lower indent
        if current_indent <= method_indent and stripped.startswith('def '):
            end_idx = i
            print(f"Method ends at line {i+1}")
            break

if start_idx is None:
    print("ERROR: Could not find _install_android_ndk!")
    sys.exit(1)

if end_idx is None:
    end_idx = len(lines)

print(f"Method spans lines {start_idx+1} to {end_idx}")
print("Original method:")
for i in range(start_idx, min(start_idx+10, end_idx)):
    print(f"  {i+1}: {lines[i]}", end='')

# Build replacement method using same indentation
spaces = ' ' * (method_indent + 4)  # method body indent
new_method = [
    lines[start_idx],  # keep def line as-is
    f"{spaces}\"\"\"Patched: use pre-installed NDK, skip download.\"\"\"\n",
    f"{spaces}ndk_dir = self.android_ndk_dir\n",
    f"{spaces}import os as _os\n",
    f"{spaces}if _os.path.isdir(ndk_dir):\n",
    f"{spaces}    self.buildozer.info('NDK found at {{}}'.format(ndk_dir))\n",
    f"{spaces}    return ndk_dir\n",
    f"{spaces}raise Exception(\n",
    f"{spaces}    'NDK not found at: ' + ndk_dir + '\\n'\n",
    f"{spaces}    'Make sure NDK is copied to Buildozer platform folder.'\n",
    f"{spaces})\n",
    "\n",
]

new_lines = lines[:start_idx] + new_method + lines[end_idx:]

with open(path, 'w') as f:
    f.writelines(new_lines)

print("\nPatched method written:")
for line in new_method:
    print(f"  {line}", end='')

# Verify
with open(path, 'r') as f:
    verify = f.read()
if 'NDK not found at' in verify:
    print("\nPatch verified successfully!")
else:
    print("\nERROR: Patch verification failed!")
    sys.exit(1)
