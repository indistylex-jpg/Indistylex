#!/usr/bin/env bash
set -euo pipefail

export FLUTTER_ROOT="/home/shivam/work/tools/flutter_linux"
export JAVA_HOME="/home/shivam/work/tools/jdk-17.0.14+7"
export ANDROID_HOME="/home/shivam/Android/Sdk"
export PATH="/home/shivam/work/indistylex_app/.tools/bin:$FLUTTER_ROOT/bin:$JAVA_HOME/bin:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH"

cd "$(dirname "$0")"

cat > android/local.properties <<EOF
sdk.dir=$ANDROID_HOME
flutter.sdk=$FLUTTER_ROOT
flutter.buildMode=release
flutter.versionName=1.0.0
flutter.versionCode=1
EOF

flutter pub get
dart run flutter_launcher_icons
flutter build apk --release

echo ""
echo "APK built successfully:"
echo "  build/app/outputs/flutter-apk/app-release.apk"
