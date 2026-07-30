# Keep Razorpay classes
-keep class com.razorpay.** { *; }
-keepclassmembers class com.razorpay.** { *; }
-dontwarn com.razorpay.**

# Flutter
-keep class io.flutter.** { *; }
-keep class io.flutter.plugins.** { *; }

# Play Core (deferred components - not used but referenced by Flutter engine)
-dontwarn com.google.android.play.core.**

# Obfuscate app code in release builds
-keep class com.indistylex.app.** { *; }
-keepattributes *Annotation*

# Secure storage
-keep class com.it_nomads.fluttersecurestorage.** { *; }
