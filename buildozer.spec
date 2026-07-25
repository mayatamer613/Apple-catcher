[app]

# (str) Title of your application
title = Apple Catcher

# (str) Package name
package.name = applecatcher

# (str) Package domain (needed for android packaging)
package.domain = org.apple

# (str) Where your source code is located
source.dir = .

# (list) Source files to include (let it include python files and assets)
source.include_exts = py,png,jpg,kv,atlas,ttf

# (str) Application versioning
version = 0.1

# (list) Application requirements
requirements = python3,kivy

# (str) Supported orientation (portrait, landscape or all)
orientation = portrait

# --- ANDROID SPECIFIC ---

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (bool) Use AndroidX support
android.androidx = True

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
