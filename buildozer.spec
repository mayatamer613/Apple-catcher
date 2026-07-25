[app]

# (str) Title of your application
title = Apple Catcher

# (str) Package name
package.name = applecatcher

# (str) Package domain (needed for android packaging)
package.domain = org.apple

# (list) Source files to include (let it include python files and assets)
source.include_exts = py,png,jpg,kv,atlas,ttf

# (list) Application requirements
requirements = python3,kivy

# (str) Supported orientation (portrait, landscape or all)
orientation = portrait

# (list) Permissions
#android.permissions = INTERNET

# --- ANDROID SPECIFIC ---

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
#android.ndk_version = 25b

# (bool) Use AndroidX support
android.androidx = True

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
