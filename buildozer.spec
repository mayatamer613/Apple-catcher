[app]

# (str) Title of your application
title = My Game

# (str) Package name
package.name = mygame

# (str) Package domain (needed for android packaging)
package.domain = org.test

# (list) Source files to include (let it match python and assets)
source.include_exts = py,png,jpg,kv,atlas,ttf

# (list) Application requirements
# أضف هنا مكتبات بايثون التي تستخدمها لعبتك (مثل kivy أو pygame أو غيرها)
requirements = python3,kivy

# (str) Supported orientations
orientation = portrait

# (list) Permissions
android.permissions = INTERNET

# (int) Target Android API
android.api = 33

# (int) Minimum API your APK will support
android.minapi = 21

# (str) Android NDK version to use
android.ndk = r25b

# (bool) قبول تراخيص الأندرويد تلقائياً لتفادى توقف البيلد
android.accept_sdk_license = True

[buildozer]

# (int) Log level (2 = debug with full output to track any error)
log_level = 2

# (int) Display warning if buildozer is run as root
warn_on_root = 1
