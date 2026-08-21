# Indistylex — Flutter Mobile App

Official Android & iOS app for [indistylex.com](https://indistylex.com).

## Brand (matches website)

| Item | Value |
|------|-------|
| Primary | `#1E4D8C` |
| Accent | `#2563EB` |
| Font | Inter |
| Logo | Same SVG as website (`assets/images/logo.svg`) |
| App icon | Kids tee mark on blue (`assets/images/app_icon.png`) |

## Quick start

```bash
flutter pub get
dart run flutter_launcher_icons
flutter run
```

## Build release APK

```bash
bash build_apk.sh
# or
flutter build apk --release
```

Output: `build/app/outputs/flutter-apk/app-release.apk`

## Sync logo/icons from website

After website brand updates:

```bash
bash scripts/sync_brand_from_website.sh
dart run flutter_launcher_icons
```

## API

Base URL: `https://indistylex.com/api/v1` (see `lib/app/constants/api_constants.dart`)
