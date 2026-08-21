#!/usr/bin/env bash
# Copy latest website brand assets into the Flutter app.
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROOT="$(cd "${APP_DIR}/.." && pwd)"
WEB="${ROOT}/Indistylex/app/static/images"
APP="${APP_DIR}/assets/images"

mkdir -p "${APP}"

cp "${WEB}/logo.svg" "${APP}/logo.svg"
cp "${WEB}/logo-icon.svg" "${APP}/logo-icon.svg"
cp "${WEB}/favicon.svg" "${APP}/favicon.svg"
cp "${WEB}/brand/favicon-192x192.png" "${APP}/app_icon.png"
cp "${WEB}/brand/favicon-192x192.png" "${APP}/app_icon_foreground.png"
cp "${WEB}/logo-white.svg" "${APP}/logo-white.svg"

echo "Brand assets synced to ${APP}/"
echo "Regenerate launcher icons:"
echo "  cd ${APP_DIR} && dart run flutter_launcher_icons"
