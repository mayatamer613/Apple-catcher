[app]

# (str) Title of your application
title = My Game

# (str) Package name
package.name = mygame

# (str) Package domain (needed for android packaging)
package.domain = org.test

# (str) Where your source code is located
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas,ttf

# (str) Application versioning
version = 0.1

# (list) Application requirements
requirements = python3,pygame,sdl2

# (str) Supported orientation
orientation = portrait

# (int) Target Android API
android.api = 33

# (int) Minimum API your APK will support
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Accept SDK licenses automatically
android.accept_sdk_license = True

[buildozer]

# (int) Log level (2 = debug with full output)
log_level = 2

# (int) Display warning if buildozer is run as root
warn_on_root = 1
