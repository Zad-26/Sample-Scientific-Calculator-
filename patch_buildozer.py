import buildozer
import os

path = os.path.join(os.path.dirname(buildozer.__file__), 'targets/android.py')

with open(path, 'r') as f:
    content = f.read()

old = 'self.buildozer.download(url,'
new = '# PATCHED: skip NDK download\n            return\n            self.buildozer.download(url,'

if old in content:
    content = content.replace(old, new, 1)
    with open(path, 'w') as f:
        f.write(content)
    print('Patch applied OK')
else:
    print('Pattern not found - may already be patched or version differs')
