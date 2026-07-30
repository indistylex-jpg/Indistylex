# Indistylex Mobile App

Premium Kids Fashion - E-commerce mobile app built with Flutter.

## Quick Start

```bash
# Install dependencies
flutter pub get

# Run on device/emulator
flutter run

# Build APK
flutter build apk --release
```

## Features
- Browse products by category
- Product detail with sizes, colors, reviews
- Shopping cart & checkout
- Razorpay payment integration
- Wishlist
- Order tracking
- User authentication (email + Google)
- Push notifications
- Search with filters

## Tech Stack
- Flutter 3.24+
- Provider (state management)
- HTTP/Dio (networking)
- Cached Network Image
- Razorpay Flutter
- Firebase (push notifications)
- Flutter Secure Storage

## Brand Colors
- Primary: `#1A1A1A` (Black)
- Accent: `#C8A962` (Gold)
- Fonts: Playfair Display + Inter

## Backend
Connects to Flask API at `https://indistylex.com/api/`

See [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed instructions.
