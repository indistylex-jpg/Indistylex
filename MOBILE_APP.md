# Mobile App (Flutter)

The official Indistylex mobile app is the **Flutter project** at:

```
../indistylex_app/
```

It connects to the live website API at `https://indistylex.com/api/v1` and uses the same brand colors, logo, and lifestyle images as the website.

## Build

```bash
cd ../indistylex_app
flutter pub get
dart run flutter_launcher_icons   # regenerate Android/iOS icons from website assets
flutter build apk --release       # Android
flutter build ios --release       # iOS (Mac + Xcode)
```

## Sync brand from website

When logo or colors change on the website:

```bash
bash indistylex_app/scripts/sync_brand_from_website.sh
cd indistylex_app && dart run flutter_launcher_icons
```

## Note

There is **no native Android WebView app** in this repo. Use `indistylex_app` only.
