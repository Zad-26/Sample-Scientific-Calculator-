[app]

title = Scientific Calculator
package.name = scientificcalculator
package.domain = org.zad26

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.1

requirements = python3,kivy==2.3.0

orientation = portrait
fullscreen = 0

android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.ndk = 25.2.9519653
android.sdk = 33
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
