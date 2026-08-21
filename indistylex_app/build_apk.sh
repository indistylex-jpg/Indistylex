#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

export FLUTTER_ROOT="${FLUTTER_ROOT:-/home/shivam/work/tools/flutter_linux}"
export JAVA_HOME="${JAVA_HOME:-/home/shivam/work/tools/jdk-17.0.14+7}"
export ANDROID_HOME="${ANDROID_HOME:-/home/shivam/Android/Sdk}"
export PATH="${SCRIPT_DIR}/.tools/bin:${FLUTTER_ROOT}/bin:${JAVA_HOME}/bin:${ANDROID_HOME}/cmdline-tools/latest/bin:${ANDROID_HOME}/platform-tools:${PATH}"

cd "${SCRIPT_DIR}"

bash scripts/sync_brand_from_website.sh

SDKMANAGER="${ANDROID_HOME}/cmdline-tools/latest/bin/sdkmanager"
if [[ -x "${SDKMANAGER}" ]]; then
  echo "Ensuring Android SDK 36 and NDK 27 are installed..."
  yes | "${SDKMANAGER}" --licenses >/dev/null 2>&1 || true
  yes | "${SDKMANAGER}" "platforms;android-36" "build-tools;36.0.0" "ndk;27.0.12077973" || true
fi

cat > android/local.properties <<EOF
sdk.dir=${ANDROID_HOME}
flutter.sdk=${FLUTTER_ROOT}
flutter.buildMode=release
flutter.versionName=1.0.0
flutter.versionCode=1
EOF

flutter pub get
dart run flutter_launcher_icons
flutter build apk --release

APK_PATH="${SCRIPT_DIR}/build/app/outputs/flutter-apk/app-release.apk"
echo ""
echo "APK built successfully:"
echo "  ${APK_PATH}"
