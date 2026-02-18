[app]

# (str) Title of your application
title = Lalitha Tailors

# (str) Package name
package.name = lalithatailors

# (str) Package domain (needed for android/ios packaging)
package.domain = org.lalitha

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
# CRITICAL: Added 'ttf' for Telugu font and 'json' for history
source.include_exts = py,png,jpg,kv,atlas,ttf,json

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy==2.3.0,plyer,android

# (str) Custom source folders for requirements
# Sets custom source for any requirements with recipes
# requirements.source.kivy = ../../kivy

# (list) Garden requirements
#garden_requirements =

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

# (list) Supported orientations
# Valid options are: landscape, portrait, portrait-reverse or landscape-reverse
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (string) Presplash background color (for android)
# Supported formats are: #RRGGBB #AARRGGBB or one of the following names:
# red, blue, green, black, white, gray, cyan, magenta, yellow, lightgray,
# darkgray, grey, lightgrey, darkgrey, aqua, fuchsia, lime, maroon, navy,
# olive, purple, silver, teal.
android.presplash_color = #FFFFFF

# (list) Permissions
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible.
# API 34 = Android 14
android.api = 34

# (int) Minimum API your APK will support.
# API 24 = Android 7.0
android.minapi = 24

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (str) The format used to package the app for release mode (aab or apk or aar).
android.release_artifact = apk

# (str) The format used to package the app for debug mode (apk or aar).
android.debug_artifact = apk

# (list) List of Java classes to add to the compilation
#android.add_src =

# (list) Java classes to exclude from the compilation
#android.rm_src =

# (list) Gradle dependencies to add
#android.gradle_dependencies =

# (list) The Android Archs to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
# CRITICAL: Must include arm64-v8a for modern phones
android.archs = arm64-v8a, armeabi-v7a

# (bool) enables Android auto backup feature (Android API >= 23)
android.allow_backup = True

# (str) python-for-android branch to use
# CRITICAL FIX: 'master' branch fixes the Gradle/Java errors on API 34
p4a.branch = master


[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
# CRITICAL FIX: Set to 0 to prevent GitHub Actions permission errors
warn_on_root = 0

# (str) Path to build artifact storage, absolute or relative to spec file
# build_dir = ./.buildozer

# (str) Path to build output storage, absolute or relative to spec file
# bin_dir = ./bin

#    -----------------------------------------------------------------------------
#    List as sections
#
#    You can define all the "list" as [section:key].
#    Each line will be considered as a option to the list.
#    Let's take [app] / source.exclude_patterns.
#    Instead of doing:
#
#        [app]
#        source.exclude_patterns = license,data/audio/*.wav,data/images/original/*
#
#    You can do:
#
#        [app:source.exclude_patterns]
#        license
#        data/audio/*.wav
#        data/images/original/*
#
#    -----------------------------------------------------------------------------
#    Profiles
#
#    You can extend section / key with a profile
#    For example, you want to deploy a demo version of your application without
#    HD content. You could first change the title to add "(demo)" in the name
#    and extend the excluded directories to remove the HD content.
#
#        [app@demo]
#        title = My Application (demo)
#
#        [app:source.exclude_patterns@demo]
#        images/hd/*
#
#    Then, invoke buildozer with the "demo" profile:
#
#        buildozer --profile demo android debug
