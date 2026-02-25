[app]

# App name shown on the phone
title = Scientific Calculator

# Package name (no spaces, lowercase)
package.name = scientificcalculator

# Unique domain (change yourname to your actual name or anything unique)
package.domain = org.yourname

# Source directory (. means root of the repo)
source.dir = .

# File types to include
source.include_exts = py,png,jpg,kv,atlas

# App version
version = 1.0

# Python packages your app needs
requirements = python3,kivy

# Screen orientation
orientation = portrait

# Not fullscreen (shows status bar)
fullscreen = 0

# Android permissions
android.permissions = INTERNET

# Android API versions
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33

# CPU architectures to support
android.archs = arm64-v8a, armeabi-v7a

# Allow backup
android.allow_backup = True

# App icon (optional - add your own icon.png to the repo and uncomment)
# icon.filename = %(source.dir)s/icon.png

# Splash screen (optional)
# presplash.filename = %(source.dir)s/splash.png

[buildozer]

# Buildozer log level (2 = verbose, good for debugging)
log_level = 2

# Warn if running as root
warn_on_root = 1
